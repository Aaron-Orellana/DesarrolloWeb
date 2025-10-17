from django.urls import path
from .views import (
    SignUpView,
    ProfileUpdate,
    EmailUpdate,
    user_list,
    user_create,
    user_edit,
    user_toggle_active,
    user_delete,
)
from django.contrib import admin
from registration import views

urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('profile/', ProfileUpdate.as_view(), name="profile"),  
    path('profile/email/', EmailUpdate.as_view(), name="profile_email"),       
    path('profile_edit/', views.profile_edit, name='profile_edit'),   
    path('cerrar_sesion/', views.logout_view, name='logout'),
    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/<int:pk>/edit/', user_edit, name='user_edit'),
    path('users/<int:pk>/toggle/', user_toggle_active, name='user_toggle_active'),
    path('users/<int:pk>/delete/', user_delete, name='user_delete'),




    ]
