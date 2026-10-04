from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'created_at']
    search_fields = ['name', 'contact_person', 'phone', 'email']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
