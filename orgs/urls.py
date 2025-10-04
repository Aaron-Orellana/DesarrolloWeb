from django.urls import path
from . import views

urlpatterns = [
    path('direcciones/', views.direccion_listar, name='direccion_listar'),
    path('departamentos/', views.departamento_listar, name='departamento_listar'),
]
