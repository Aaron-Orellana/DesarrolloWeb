from django.urls import path
from . import views

urlpatterns = [ 
    path('incidencias/crear/', views.incidencia_crear, name='incidencia_crear'),
    path('incidencias/guardar/', views.incidencia_guardar, name='incidencia_guardar'),
    path('incidencias/', views.incidencia_listar, name='incidencia_listar'),
    path('incidencias/<int:incidencia_id>/ver/', views.incidencia_ver, name='incidencia_ver'),
    path('incidencias/<int:incidencia_id>/editar/', views.incidencia_editar, name='incidencia_editar'),
    path('incidencias/<int:incidencia_id>/eliminar/', views.incidencia_eliminar, name='incidencia_eliminar'),
]
