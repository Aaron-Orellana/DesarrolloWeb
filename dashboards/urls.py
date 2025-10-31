from django.urls import path
from . import views

urlpatterns = [
    path("secpla/", views.dashboard_secpla, name="dashboard_secpla"),
    path('territorial/', views.territorial_dashboard, name='dashboard_territorial'),
    path('direccion/', views.dashboard_direccion, name='dashboard_direccion'),

]