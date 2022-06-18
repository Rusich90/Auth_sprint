from datetime import timedelta
from http import HTTPStatus
from typing import Optional

import click
from flasgger import Swagger
from flask import Flask
from flask.cli import with_appcontext
from flask.json import jsonify
from flask.logging import create_logger
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .api import api_v1
from .core.alchemy import db, init_alchemy
from .core.config import JWTSettings
from .core.redis import redis
from .core import tracing
from .core import limiter
from .models.db_models import User
from .serializers.auth import ErrorBody

app = Flask(__name__)
swagger = Swagger(app)
logger = create_logger(app)

# Setup db and migrations
init_alchemy(app)
migrate = Migrate(app, db)

# Setup the Flask-JWT-Extended extension
jwt_conf = JWTSettings()
app.config["JWT_SECRET_KEY"] = jwt_conf.secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=jwt_conf.access_exp)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=jwt_conf.refresh_exp)
app.config["JWT_ERROR_MESSAGE_KEY"] = "error"
jwt = JWTManager(app)

# Setup routing
app.register_blueprint(api_v1)


# cli create superuser
@app.cli.command("create_superuser")
@click.option("--username", "-u", default="superuser", prompt="Username")
@click.option("--password", "-p", default="superpassword", prompt="Passoword")
@with_appcontext
def create_superuser(username: str, password: str):
    init_alchemy(app)
    db.create_all()

    new_user = User(login=username, is_superuser=True)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()


# noinspection PyUnusedLocal
@app.errorhandler(HTTPStatus.FORBIDDEN)
def permission_denied(exc: BaseException):
    return jsonify({"error": "You don't have permissions"}), HTTPStatus.FORBIDDEN


# noinspection PyUnusedLocal
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = redis.get(jti)
    return token_in_redis is not None


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]["user_id"]
    user = User.query.filter_by(id=identity).one_or_none()
    if not user:
        msg = "Something went wrong"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT
    return user


@app.route("/health")
def health_handler():
    """Check app health
    ---
    tags:
      - utils
    produces:
      - application/json
    schemes: ['http', 'https']
    definitions:
      BoolAnswer:
        type: object
        properties:
          success:
            type: boolean
    responses:
      200:
        schema:
          $ref: '#/definitions/BoolAnswer'
    """
    return {"success": True}


@app.before_first_request
def on_startup():
    """Prepare application and services."""
    limiter.setup(app)
    tracing.setup(app)


@app.teardown_request
def on_shutdown(error: Optional[BaseException] = None):
    """Teardown application and services."""
    if error is not None:
        logger.exception("%s: %s", type(error).__name__, error)
