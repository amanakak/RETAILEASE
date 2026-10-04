from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], help_text="Cost price for profit calculation")
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10, validators=[MinValueValidator(0)], help_text="Alert when stock goes below this number")
    unit = models.CharField(max_length=20, default='pcs', help_text="Unit of measurement (e.g., pcs, kg, ltr)")
    expiry_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def profit_margin(self):
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def total_value(self):
        return self.stock_quantity * self.price

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Stock Adjustment'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=200, blank=True, null=True, help_text="Reference (e.g., Sale ID, Purchase Order)")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity})"
