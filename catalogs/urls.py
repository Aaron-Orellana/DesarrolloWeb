from django.urls import path
from . import views

urlpatterns = [ 
    path('incidencias/crear/', views.incidencia_crear, name='incidencia_crear'),
    path('incidencias/guardar/', views.incidencia_guardar, name='incidencia_guardar'),
    path('incidencias/', views.incidencia_listar, name='incidencia_listar'),

]
