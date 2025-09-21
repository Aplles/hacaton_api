REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication"
    ],
    "DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination"
    "PAGE_SIZE": 20,
}
