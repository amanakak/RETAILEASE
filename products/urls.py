from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('<int:product_id>/detail/', views.product_detail, name='product_detail'),
    path('delete/', views.product_delete, name='product_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('low-stock/', views.low_stock_alert, name='low_stock_alert'),
]