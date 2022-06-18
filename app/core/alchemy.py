__all__ = ["db", "init_alchemy"]

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import SQLAlchemySettings

db = SQLAlchemy()


def init_alchemy(app: Flask):
    cfg = SQLAlchemySettings()
    app.config["SQLALCHEMY_DATABASE_URI"] = _build_url(cfg)
    db.init_app(app)


def _build_url(cfg: SQLAlchemySettings) -> str:
    """Build database connection URL based on setting."""
    parts = [f"{cfg.connector}://"]

    if cfg.username is not None:
        parts.append(cfg.username)

    if cfg.password is not None:
        parts.append(f":{cfg.password.get_secret_value()}")

    parts.append(f"@{cfg.host}")

    if cfg.port is not None:
        parts.append(f":{cfg.port}")

    if cfg.database_name is not None:
        parts.append(f"/{cfg.database_name}")

    return "".join(parts)
