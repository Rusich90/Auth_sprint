import random
import string
from datetime import timedelta
from functools import wraps
from http import HTTPStatus
from typing import Union

from flask import abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    verify_jwt_in_request,
)

from app.core.config import JWTSettings
from app.core.enums import DefaultRole
from app.core.redis import redis
from app.core.tracing import tracer
from app.models.db_models import User
from app.serializers.auth import TokenBody

from .core.enums import DefaultRole


@tracer("get_new_tokens", __name__)
def get_new_tokens(user: User, user_agent: str) -> TokenBody:
    """
    Create new access and refresh tokens with user id and roles
    """
    identity = {"user_id": user.id, "roles": [role.name for role in user.roles]}
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    refresh_key = f"{user.id}_{user_agent}"

    # Put refresh token in redis for validate refreshing
    redis.set(refresh_key, refresh_token, ex=timedelta(days=JWTSettings().refresh_exp))
    return TokenBody(access_token=access_token, refresh_token=refresh_token)


@tracer("check_permissions", __name__)
def permissions_required(role: Union[str, DefaultRole]):
    if isinstance(role, DefaultRole):
        role = role.value

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_roles = get_jwt()["sub"]["roles"]
            if current_user.is_superuser or role in user_roles:
                return fn(*args, **kwargs)
            return abort(HTTPStatus.FORBIDDEN)

        return decorator

    return wrapper


def generate_password():
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation

    all_ = lower + upper + num + symbols

    temp = random.sample(all_, 12)

    password = "".join(temp)

    return password
