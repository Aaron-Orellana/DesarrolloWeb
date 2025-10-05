from django.urls import path
from orgs import views

orgs_urlpatterns = [
    path('direcciones/main_direccion/', views.main_direccion, name='main_direccion'),
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('direcciones/create_direccion/', views.direccion_crear, name='direccion_crear'),
    path('direcciones/save_direccion/', views.direccion_guardar, name='direccion_guardar'),

    path('departamentos/crear', views.departamento_crear, name='departamento_crear'),
    path('departamentos/guardar', views.departamento_guardar, name='departamento_guardar'),
    path('departamentos/', views.departamento_listar, name='departamento_listar'),
]
