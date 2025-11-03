from django.urls import path
from . import views



urlpatterns = [
    path("secpla/", views.dashboard_secpla, name="dashboard_secpla"),
    path('territorial/', views.territorial_dashboard, name='dashboard_territorial'),
    path('direccion/', views.dashboard_direccion, name='dashboard_direccion'),
    path('departamento/', views.dashboard_departamento, name='dashboard_departamento'),
    path('asignar-cuadrilla/<int:incidencia_id>/', views.asignar_cuadrilla, name='asignar_cuadrilla'),
]