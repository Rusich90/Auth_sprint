from . import app
from .core.config import FlaskSettings

settings = FlaskSettings()
app.run(
    host=settings.host,
    port=settings.port,
    debug=settings.debug,
)
