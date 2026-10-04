from django.contrib import admin
from .models import ExpenseCategory, Expense

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'expense_date', 'created_by', 'created_at']
    list_filter = ['category', 'expense_date', 'created_by']
    search_fields = ['title', 'description']
    date_hierarchy = 'expense_date'
