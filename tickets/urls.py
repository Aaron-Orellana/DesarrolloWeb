from django.urls import path
from tickets import views
print(f"Type of MultimediaListView: {type(views.MultimediaListView)}")
print(f"Type of MultimediaCreateView: {type(views.MultimediaCreateView)}")

urlpatterns = [
    path('solicitud/', views.solicitud_listar, name='solicitud_listar'),
    path('solicitud/crear/', views.solicitud_crear, name='solicitud_crear'),
    path('solicitud/ver/<int:solicitud_incidencia_id>/', views.solicitud_ver, name='solicitud_ver'),
    path('solicitud/editar/<int:solicitud_incidencia_id>/', views.solicitud_editar, name='solicitud_editar'),
    path('solicitud/<int:solicitud_incidencia_id>/multimedia/', views.MultimediaListView.as_view(), name='multimedia_listar'),
    path('solicitud/<int:solicitud_incidencia_id>/multimedia/crear/', views.MultimediaCreateView.as_view(), name='multimedia_crear'),
]