from django.urls import path
from . import views

urlpatterns = [ 
    path('catalogs/crear/', views.incidencia_crear, name='incidencia_crear'),
    path('catalogs/guardar/', views.incidencia_guardar, name='incidencia_guardar'),
    path('catalogs/listar/', views.incidencia_listar, name='incidencia_listar'),
    path('catalogs/', views.incidencia_listar, name='incidencia_listar')
]
