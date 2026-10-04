from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('create/', views.sale_create, name='sale_create'),
    path('<int:sale_id>/detail/', views.sale_detail, name='sale_detail'),
    path('<int:sale_id>/receipt/', views.sale_receipt, name='sale_receipt'),
    path('daily/', views.daily_sales, name='daily_sales'),
    path('get-product-info/', views.get_product_info, name='get_product_info'),
    path('search-products/', views.search_products, name='search_products'),
    path('search-customers/', views.search_customers, name='search_customers'),
]
