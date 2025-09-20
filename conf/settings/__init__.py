from split_settings.tools import include

settings = [
    "database.py",  # database settings
    "django.py",  # standard django settings
    "logger.py",  # logger settings
    "rest_framework.py",  # rest_framework settings
    "swagger.py",  # swagger settings
]

include(*settings)
