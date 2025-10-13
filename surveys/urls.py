from django.urls import path
from . import views

urlpatterns = [
    path('encuestas/', views.encuesta_listar, name='encuesta_listar'),
    path('encuestas/crear/', views.encuesta_crear, name='encuesta_crear'),
    path('encuestas/<int:encuesta_id>/', views.encuesta_detalle, name='encuesta_detalle'),
    path('encuestas/<int:encuesta_id>/editar/', views.encuesta_editar, name='encuesta_editar'),
    path('encuestas/<int:encuesta_id>/cambiar-estado/', views.encuesta_cambiar_estado, name='encuesta_cambiar_estado'),
    path('encuestas/<int:encuesta_id>/eliminar/', views.encuesta_eliminar, name='encuesta_eliminar'),
]
