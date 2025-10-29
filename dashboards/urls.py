from django.urls import path
from dashboards import views

urlpatterns = [
    path('territorial', views.territorial_dashboard, name='territorial'),
]