from django.urls import path
from . import views

urlpatterns = [
    path('encuestas/', views.encuesta_listar, name='encuesta_listar'),
    path('encuestas/crear/', views.encuesta_crear, name='encuesta_crear'),
    path('encuestas/ver/<int:encuesta_id>/', views.encuesta_ver, name='encuesta_ver'),
    path('encuestas/editar/<int:encuesta_id>/', views.encuesta_editar, name='encuesta_editar'),
    path('encuestas/bloquear/<int:encuesta_id>', views.encuesta_bloquear, name='encuesta_bloquear'),
    path('encuestas/eliminar/<int:encuesta_id>/', views.encuesta_eliminar, name='encuesta_eliminar'),
]
