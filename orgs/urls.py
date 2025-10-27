from django.urls import path
from . import views
from .views import mis_incidencias_cuadrilla, marcar_en_proceso

urlpatterns = [
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('direcciones/crear/', views.direccion_crear, name='direccion_crear'),
    path('direcciones/editar/<int:direccion_id>/', views.direccion_editar, name='direccion_editar'),
    path('direcciones/ver/<int:direccion_id>/', views.direccion_ver, name='direccion_ver'),
    path('direcciones/bloquear/<int:direccion_id>/', views.direccion_bloquear, name='direccion_bloquea'),
    path('direcciones/eliminar/<int:direccion_id>/', views.direccion_eliminar, name='direccion_elimina'),

    path('departamentos/', views.departamento_listar, name='departamento_listar'),
    path('departamentos/crear/', views.departamento_crear, name='departamento_crear'),
    path('departamentos/editar/<int:departamento_id>/', views.departamento_editar, name='departamento_editar'),
    path('departamentos/ver/<int:departamento_id>/', views.departamento_ver, name='departamento_ver'),
    path('departamentos/bloquear/<int:departamento_id>/', views.departamento_bloquear, name='departamento_bloquear'),
    path('departamentos/eliminar/<int:departamento_id>/', views.departamento_eliminar, name='departamento_eliminar'),
    path('mis-incidencias/', mis_incidencias_cuadrilla, name='mis_incidencias_cuadrilla'),
    path('marcar-en-proceso/<int:pk>/', marcar_en_proceso, name='marcar_en_proceso'),

    path('cuadrillas/', views.cuadrilla_listar, name='cuadrilla_listar'),
    path('cuadrillas/crear/', views.cuadrilla_crear, name='cuadrilla_crear'),
    path('cuadrillas/editar/<int:cuadrilla_id>/', views.cuadrilla_editar, name='cuadrilla_editar'),
    path('cuadrillas/ver/<int:cuadrilla_id>/', views.cuadrilla_ver, name='cuadrilla_ver'),
    path('cuadrillas/bloquear/<int:cuadrilla_id>/', views.cuadrilla_bloquear, name='cuadrilla_bloquear'),

    path('territoriales/', views.territorial_listar, name='territorial_listar'),
    path('territoriales/crear/', views.territorial_crear, name='territorial_crear'),
    path('territoriales/editar/<int:territorial_id>/', views.territorial_editar, name='territorial_editar'),
    path('territoriales/ver/<int:territorial_id>/', views.territorial_ver, name='territorial_ver'),
    path('territoriales/eliminar/<int:territorial_id>/', views.territorial_eliminar, name='territorial_eliminar'),
]
