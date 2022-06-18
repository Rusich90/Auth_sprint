from flask import Blueprint

from .v1 import v1

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api")
api_v1.register_blueprint(v1)
