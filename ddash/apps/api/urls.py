from django.urls import path, include

from ddash.settings import cfg
import ddash.apps.api.views as api_views
import rest_framework.authtoken.views as authviews
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

router = routers.DefaultRouter()
"""
router.register(r"^architectures", ArchitectureViewSet, basename="architecture")
router.register(r"^builds", BuildViewSet, basename="build")

"""
schema_view = get_swagger_view(title="Dyninst Dashboard API")

server_views = [
    path("api/docs/", schema_view, name="docs"),
    path(
        "tables/results/",
        api_views.ResultsTable.as_view(),
        name="results_table",
    ),
]

urlpatterns = [
    path("api/", include(router.urls)),
    path("", include((server_views, "api"), namespace="internal_apis")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api-token-auth/", authviews.obtain_auth_token),
    path(
        "auth/token/",
        api_views.GetAuthToken.as_view(),
        name="auth_token",
    ),
    path(
        "",
        api_views.ServiceInfo.as_view(),
        name="service_info",
    ),
    path("results/log/", api_views.upload_log),
    path(
        "results/new/",
        api_views.NewTestResult.as_view(),
        name="new_test_result",
    ),
]


app_name = "api"
