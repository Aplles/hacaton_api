import os

import environ

from conf.settings.django import BASE_DIR

env = environ.Env()
FULL_LOG_PATH = os.path.join(
    BASE_DIR, env("LOG_FILE_PATH", cast=str, default="logs/hakaton_logs")
)

os.makedirs(os.path.dirname(FULL_LOG_PATH), exist_ok=True)
with open(FULL_LOG_PATH, "a+"):
    pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {"()": "log_request_id.filters.RequestIDFilter"},
    },
    "formatters": {
        "standard": {
            "format": "%(levelname)-8s [%(asctime)s] [%(request_id)s] %(name)s: %(message)s"
        },
        "email": {"format": "%(levelname)-8s [%(asctime)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "rich.logging.RichHandler",
            "filters": ["request_id"],
            "formatter": "standard",
        },
        "db_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": FULL_LOG_PATH,
            "formatter": "standard",
        }
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["console", "db_file"],
            "propagate": False,
        },
        "django.db.backends": {
            "level": env("DJANGO_DB_LOGGER_LEVEL", cast=str, default="DEBUG"),
            "handlers": ["console", "db_file"],
            "propagate": False,
        }
    },
}
