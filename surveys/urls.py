from django.urls import path
from . import views

urlpatterns = [
    path('encuestas/', views.encuesta_listar, name='encuesta_listar'),
]
