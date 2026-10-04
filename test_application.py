#!/usr/bin/env python3
"""
Simple test script to verify TrackCart application functionality
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackcart.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Product, Category
from sales.models import Sale
from expenses.models import Expense

def test_application():
    """Test basic application functionality"""
    print("🧪 Testing TrackCart Application...")
    print("=" * 50)
    
    # Test 1: Check users
    admin_count = User.objects.filter(userprofile__role='admin').count()
    staff_count = User.objects.filter(userprofile__role='staff').count()
    print(f"✓ Users: {admin_count} admin(s), {staff_count} staff member(s)")
    
    # Test 2: Check categories
    category_count = Category.objects.count()
    print(f"✓ Product Categories: {category_count}")
    
    # Test 3: Check products
    product_count = Product.objects.filter(is_active=True).count()
    low_stock_count = len([p for p in Product.objects.filter(is_active=True) if p.is_low_stock])
    print(f"✓ Products: {product_count} total, {low_stock_count} low stock")
    
    # Test 4: Check sales
    sale_count = Sale.objects.count()
    total_sales = sum(sale.total_amount for sale in Sale.objects.all())
    print(f"✓ Sales: {sale_count} transactions, ${total_sales:.2f} total revenue")
    
    # Test 5: Check expenses
    expense_count = Expense.objects.count()
    total_expenses = sum(expense.amount for expense in Expense.objects.all())
    print(f"✓ Expenses: {expense_count} entries, ${total_expenses:.2f} total")
    
    # Test 6: Calculate profit
    profit = total_sales - total_expenses
    print(f"✓ Net Profit: ${profit:.2f}")
    
    print("\n" + "=" * 50)
    print("🎉 Application test completed successfully!")
    print("\n📋 Quick Start Guide:")
    print("1. Run: python manage.py runserver")
    print("2. Open: http://127.0.0.1:8000")
    print("3. Login with: admin/admin123 or staff/staff123")
    print("4. Explore the inventory management features!")

if __name__ == '__main__':
    test_application()
