from flask import Flask
from flask_jwt_extended import current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import RateLimitSettings


def key_function() -> str:
    """Return user's id or ip."""
    try:
        user = current_user()
    except RuntimeError:
        return get_remote_address()
    else:
        return str(user.id)


limiter_settings = RateLimitSettings()
limiter = Limiter(
    key_func=key_function,
    storage_uri=limiter_settings.storage_uri,
    strategy=limiter_settings.strategy,
    default_limits=limiter_settings.default,
    default_limits_per_method=limiter_settings.default_limits_per_method,
    key_prefix=limiter_settings.key_prefix,
)


def setup(app: Flask):
    limiter.init_app(app)
