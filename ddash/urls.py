from django.urls import include, path
from django.contrib import admin
from django.views.generic.base import TemplateView

from ddash.apps.base import urls as base_urls
from ddash.apps.main import urls as main_urls
from ddash.apps.users import urls as user_urls
from ddash.apps.api import urls as api_urls

admin.site.site_header = "Dyninst Dashboard Admin"
admin.site.site_title = "Dyninst Dashboard Admin"
admin.site.index_title = "Dyninst Dashboard Admin"

# Configure custom error pages
handler404 = "ddash.apps.base.views.handler404"
handler500 = "ddash.apps.base.views.handler500"

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(base_urls, namespace="base")),
    path("api/", include(api_urls, namespace="api")),
    path("", include(main_urls, namespace="main")),
    path("", include(user_urls, namespace="users")),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="base/robots.txt", content_type="text/plain"
        ),
    ),
]
