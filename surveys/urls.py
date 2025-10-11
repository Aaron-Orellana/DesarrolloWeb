from django.urls import path
from . import views

urlpatterns = [
    path('encuestas/crear/', views.encuesta_crear, name='encuesta_crear'),
    path('encuestas/guardar', views.encuesta_guardar, name='encuesta_guardar'),
    path('encuestas/listar', views.encuesta_listar, name='encuesta_listar'),
    path('encuestas/detalle/<int:encuesta_id>/', views.encuesta_detalle, name='encuesta_detalle'),
    path('encuestas/editar/<int:encuesta_id>/', views.encuesta_editar, name='encuesta_editar'),
    path('encuestas/cambiar-estado/<int:encuesta_id>/', views.encuesta_cambiar_estado, name='encuesta_cambiar_estado'),
    path('encuestas/eliminar/<int:encuesta_id>/', views.encuesta_eliminar, name='encuesta_eliminar'),
]
