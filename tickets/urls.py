from django.urls import path
from . import views

urlpatterns = [
    path('solicitud/', views.solicitud_listar, name='solicitud_listar'),
    path('solicitud/crear/', views.solicitud_crear, name='solicitud_crear'),
    path('solicitud/editar/<int:solicitud_incidencia_id>/', views.solicitud_editar, name='solicitud_editar'),
]