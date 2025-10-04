from django.urls import path

from catalogs import views

catalog_urlpatterns = [
    path('incidencia/crear/', views.incidencia_crear, name='incidencia_crear'),
    path('incidencia/guardar/', views.incidencia_guardar, name='incidencia_guardar')
]