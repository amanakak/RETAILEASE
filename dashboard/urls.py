from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('analytics/', views.analytics, name='analytics'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
]
