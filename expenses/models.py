from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField(blank=True, null=True)
    expense_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    vendor_name = models.CharField(max_length=200, blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    recurring_period = models.CharField(max_length=20, blank=True, null=True, help_text="e.g., monthly, weekly")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
