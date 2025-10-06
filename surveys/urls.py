from django.urls import path
from . import views

urlpatterns = [
    path('encuestas/crear/', views.encuesta_crear, name='encuesta_crear'),
    path('encuestas/guardar', views.encuesta_guardar, name='encuesta_guardar'),
    path('encuestas/listar', views.encuesta_listar, name='encuesta_listar'),
]
