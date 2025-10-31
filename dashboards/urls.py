from django.urls import path
from . import views

urlpatterns = [
    path("secpla/", views.dashboard_secpla, name="dashboard_secpla"),
    path('territorial/', views.territorial_dashboard, name='dashboard_territorial'),
    path('direccion/', views.dashboard_direccion, name='dashboard_direccion'),

path('secpla/usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('secpla/incidencias/creadas/', views.listar_incidencias_creadas, name='listar_incidencias_creadas'),
    path('secpla/incidencias/derivadas/', views.listar_incidencias_derivadas, name='listar_incidencias_derivadas'),
    path('secpla/incidencias/rechazadas/', views.listar_incidencias_rechazadas, name='listar_incidencias_rechazadas'),
    path('secpla/incidencias/finalizadas/', views.listar_incidencias_finalizadas, name='listar_incidencias_finalizadas'),


]