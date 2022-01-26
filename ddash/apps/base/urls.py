from django.views.generic.base import TemplateView
from django.urls import path

from . import views

urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="base/robots.txt", content_type="text/plain"
        ),
    ),
]

app_name = "base"
