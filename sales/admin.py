from django.contrib import admin
from .models import Customer, Sale, SaleItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'loyalty_points']
    search_fields = ['name', 'phone', 'email']

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['total_price']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_number', 'customer_name', 'total_amount', 'payment_method', 'created_by', 'created_at']
    list_filter = ['payment_method', 'created_at', 'created_by']
    search_fields = ['sale_number', 'customer_name', 'customer_phone']
    readonly_fields = ['sale_number', 'total_amount', 'created_at', 'updated_at']
    inlines = [SaleItemInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing sale
            return self.readonly_fields + ['created_by']
        return self.readonly_fields

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'total_price']
    list_filter = ['sale__created_at']
    readonly_fields = ['total_price']
