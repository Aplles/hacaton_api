from django.urls import path
from django.urls import include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from conf.settings import django as settings
from django.conf.urls.static import static

urlpatterns = []

api_urlpatterns = [
    path("api/", include("api.urls")),
]

api_docs_urlpatterns = [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(urlconf=api_urlpatterns),
        name="api_schema",
    ),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="api_schema"),
        name="api_swagger-ui",
    ),
]

urlpatterns += (
    api_urlpatterns +
    api_docs_urlpatterns
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
