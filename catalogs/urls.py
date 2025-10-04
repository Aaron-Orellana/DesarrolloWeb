from django.urls import path
from . import views

urlpatterns = [ 
    path('incidencia/crear/', views.incidencia_crear, name='incidencia_crear'),
    path('incidencia/guardar/', views.incidencia_guardar, name='incidencia_guardar'),
    path('incidencia/listar/', views.incidencia_listar, name='incidencia_listar'),
]
