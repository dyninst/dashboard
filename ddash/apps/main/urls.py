from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("testrun/detail/<int:id>", views.testrun_detail, name="testrun_detail"),
]

app_name = "main"
