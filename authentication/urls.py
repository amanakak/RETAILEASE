from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('toggle-user-status/', views.toggle_user_status, name='toggle_user_status'),
    path('profile/', views.profile, name='profile'),
]
