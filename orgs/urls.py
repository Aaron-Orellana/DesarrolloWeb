from django.urls import path
from . import views

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

]
