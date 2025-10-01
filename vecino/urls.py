from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_vecinos, name='lista_vecinos'),
]
