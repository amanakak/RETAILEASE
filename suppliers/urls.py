from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('create/', views.supplier_create, name='supplier_create'),
    path('<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('<int:supplier_id>/detail/', views.supplier_detail, name='supplier_detail'),
    path('delete/', views.supplier_delete, name='supplier_delete'),
    path('activate/', views.supplier_activate, name='supplier_activate'),
]
