from django.db import models
from django.contrib.auth.models import User
from products.models import Product, StockMovement
from decimal import Decimal
from django.core.validators import MinValueValidator
import uuid

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone = models.CharField(max_length=30, blank=True, null=True, unique=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.loyalty_points} points)'

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('credit', 'Credit'),
    ]
    
    sale_number = models.CharField(max_length=50, unique=True, editable=False)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, related_name='sales')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    payment_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points_redeemed = models.PositiveIntegerField(default=0)
    loyalty_points_earned = models.PositiveIntegerField(default=0)
    round_up_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.sale_number:
            # Generate unique sale number
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = Sale.objects.filter(created_at__date=timezone.now().date()).count() + 1
            self.sale_number = f'SALE-{today}-{count:04d}'
        
        # Calculate change amount
        if self.payment_received > self.total_amount:
            self.change_amount = self.payment_received - self.total_amount
        else:
            self.change_amount = 0
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.sale_number} - {self.customer_name or 'Walk-in Customer'}"
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def final_amount(self):
        return self.subtotal - self.discount_amount + self.tax_amount
    
    def update_total(self):
        self.total_amount = self.final_amount
        self.save()

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update stock and create stock movement
        if not hasattr(self, '_stock_updated'):
            self.product.stock_quantity -= self.quantity
            self.product.save()
            
            StockMovement.objects.create(
                product=self.product,
                movement_type='out',
                quantity=self.quantity,
                reference=f'Sale #{self.sale.sale_number}',
                created_by=self.sale.created_by
            )
            
            self._stock_updated = True
        
        # Update sale total
        self.sale.update_total()
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
