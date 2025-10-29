from django.urls import path
from . import views

urlpatterns = [
    path("secpla/", views.dashboard_secpla, name="dashboard_secpla"),
]
