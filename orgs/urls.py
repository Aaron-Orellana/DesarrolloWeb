from django.urls import path
from . import views

urlpatterns = [
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('departamentos/crear', views.departamento_crear, name='departamento_crear'),
    path('departamentos/guardar', views.departamento_guardar, name='departamento_guardar'),
    path('departamentos/', views.departamento_listar, name='departamento_listar'),
]
