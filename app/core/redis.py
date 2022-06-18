__all__ = ["redis"]

from redis import Redis

from .config import RedisSettings

_cfg = RedisSettings()
redis = Redis(
    host=_cfg.host, port=_cfg.port, db=_cfg.db, encoding="utf-8", decode_responses=True
)
