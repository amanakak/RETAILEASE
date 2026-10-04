from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'low_stock_threshold', 'is_low_stock', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'sku', 'barcode']
    list_editable = ['price', 'stock_quantity', 'low_stock_threshold']
    readonly_fields = ['created_at', 'updated_at']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'
