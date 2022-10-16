import logging
import re
from typing import Any

from starlette.status import HTTP_200_OK

from starlite import LoggingConfig

from hackathon.config.settings import get_settings

settings = get_settings()


class AccessLogFilter(logging.Filter):
    """Filter for omitting log records from uvicorn access logs based on request path.

    Args:
        *args: Unpacked into [`logging.Filter.__init__()`][logging.Filter].
        path_re: Regex, paths matched are filtered.
        **kwargs: Unpacked into [`logging.Filter.__init__()`][logging.Filter].
    """

    def __init__(self, *args: Any, path_re: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.path_filter = re.compile(path_re)

    def filter(self, record: logging.LogRecord) -> bool:
        *_, req_path, _, status_code = record.args
        if (
            self.path_filter.match(req_path) and
            status_code == HTTP_200_OK
        ):
            return False
        return True


config = LoggingConfig(
    root={"level": settings.app.LOG_LEVEL, "handlers": ["queue_listener"]},
    filters={
        "health_filter": {
            "()": AccessLogFilter,
            "path_re": f"^{settings.api.V1_STR}{settings.api.HEALTHCHECK_PATH}$",
        },
    },
    formatters={
        "standard": {
            "format": "%(asctime)s loglevel=%(levelname)-6s logger=%(name)s %(funcName)s() L%(lineno)-4d %(message)s",
        },
    },
    loggers={
        "app": {
            "propagate": True,
        },
        "uvicorn.access": {
            "propagate": True,
            "filters": ["health_filter"],
        },
        "uvicorn.error": {
            "propagate": True,
        },
        "sqlalchemy.engine": {
            "propagate": True,
        },
    },
)
