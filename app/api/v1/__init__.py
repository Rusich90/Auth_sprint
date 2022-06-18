from flask import Blueprint

from . import auth, oauth, roles, users

v1 = Blueprint("v1", __name__, url_prefix="/v1")
v1.register_blueprint(auth.auth)
v1.register_blueprint(oauth.oauth)
v1.register_blueprint(roles.roles)
v1.register_blueprint(users.users)
