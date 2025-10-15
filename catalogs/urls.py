from django.urls import path
from . import views

urlpatterns = [
    path('incidencias/', views.incidencia_listar, name='incidencia_listar'),
    path('incidencias/crear/', views.incidencia_crear, name='incidencia_crear'),
    path('incidencias/<int:incidencia_id>/', views.incidencia_ver, name='incidencia_ver'),
    path('incidencias/<int:incidencia_id>/editar/', views.incidencia_editar, name='incidencia_editar'),
    path('incidencias/<int:incidencia_id>/eliminar/', views.incidencia_eliminar, name='incidencia_eliminar'),
    path('incidencias/<int:incidencia_id>/bloquear/', views.incidencia_bloquear, name='incidencia_bloquear'),
    
]
