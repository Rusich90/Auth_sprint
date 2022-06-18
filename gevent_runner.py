__all__ = ["application"]

from gevent import monkey

monkey.patch_all()

from app import app as application  # noqa: E402
