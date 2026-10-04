from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('create/', views.expense_create, name='expense_create'),
    path('<int:expense_id>/edit/', views.expense_edit, name='expense_edit'),
    path('<int:expense_id>/detail/', views.expense_detail, name='expense_detail'),
    path('delete/', views.expense_delete, name='expense_delete'),
    path('categories/', views.category_manage, name='category_manage'),
    path('monthly/', views.monthly_expenses, name='monthly_expenses'),
]
