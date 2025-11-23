from django.urls import path
from . import views

urlpatterns = [
    path('ubicaciones/', views.ubicacion_listar, name='ubicacion_listar'),
    path('ubicaciones/crear/', views.ubicacion_crear, name='ubicacion_crear'),
]
