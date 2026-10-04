from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile
from products.models import Category, Product
from suppliers.models import Supplier
from expenses.models import ExpenseCategory, Expense
from sales.models import Sale, SaleItem
from decimal import Decimal
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample data for TrackCart system'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for TrackCart...')
        
        # Create superuser admin
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@trackcart.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                is_superuser=True,
                is_staff=True
            )
            admin_profile = admin_user.userprofile
            admin_profile.role = 'admin'
            admin_profile.phone = '+1234567890'
            admin_profile.address = '123 Admin Street, City, State'
            admin_profile.save()
            self.stdout.write(f'Created admin user: admin / admin123')
        
        # Create staff user
        if not User.objects.filter(username='staff').exists():
            staff_user = User.objects.create_user(
                username='staff',
                email='staff@trackcart.com',
                password='staff123',
                first_name='John',
                last_name='Doe'
            )
            staff_profile = staff_user.userprofile
            staff_profile.role = 'staff'
            staff_profile.phone = '+1987654321'
            staff_profile.address = '456 Staff Avenue, City, State'
            staff_profile.save()
            self.stdout.write(f'Created staff user: staff / staff123')
        
        # Create categories
        categories_data = [
            {'name': 'Beverages', 'description': 'Soft drinks, juices, water, coffee, tea'},
            {'name': 'Snacks', 'description': 'Chips, crackers, nuts, candies'},
            {'name': 'Dairy Products', 'description': 'Milk, cheese, yogurt, butter'},
            {'name': 'Bakery', 'description': 'Bread, pastries, cakes, cookies'},
            {'name': 'Fruits & Vegetables', 'description': 'Fresh produce, organic items'},
            {'name': 'Frozen Foods', 'description': 'Frozen meals, ice cream, frozen vegetables'},
            {'name': 'Personal Care', 'description': 'Toothpaste, shampoo, soap, cosmetics'},
            {'name': 'Household Items', 'description': 'Cleaning supplies, paper products'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create suppliers
        suppliers_data = [
            {
                'name': 'Fresh Foods Wholesale',
                'contact_person': 'Mike Johnson',
                'phone': '+1555123456',
                'email': 'orders@freshfoods.com',
                'address': '789 Wholesale Blvd',
                'city': 'Supply City',
                'state': 'SC',
                'credit_limit': 5000.00
            },
            {
                'name': 'Beverage Distributors Inc',
                'contact_person': 'Sarah Wilson',
                'phone': '+1555987654',
                'email': 'sales@beveragedist.com',
                'address': '321 Distribution Way',
                'city': 'Drink Town',
                'state': 'DT',
                'credit_limit': 3000.00
            },
            {
                'name': 'Daily Essentials Supply',
                'contact_person': 'Robert Brown',
                'phone': '+1555456789',
                'email': 'info@dailyessentials.com',
                'address': '654 Essential Ave',
                'city': 'Necessity City',
                'state': 'NC',
                'credit_limit': 4000.00
            }
        ]
        
        admin_user = User.objects.get(username='admin')
        
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults={
                    'contact_person': sup_data['contact_person'],
                    'phone': sup_data['phone'],
                    'email': sup_data['email'],
                    'address': sup_data['address'],
                    'city': sup_data['city'],
                    'state': sup_data['state'],
                    'credit_limit': sup_data['credit_limit'],
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')
        
        # Create products
        products_data = [
            # Beverages
            {'name': 'Coca Cola 330ml', 'category': 'Beverages', 'sku': 'BEV001', 'price': 40, 'cost': 28, 'stock': 150},
            {'name': 'Pepsi 330ml', 'category': 'Beverages', 'sku': 'BEV002', 'price': 40, 'cost': 28, 'stock': 120},
            {'name': 'Orange Juice 1L', 'category': 'Beverages', 'sku': 'BEV003', 'price': 120, 'cost': 84, 'stock': 45},
            {'name': 'Bottled Water 500ml', 'category': 'Beverages', 'sku': 'BEV004', 'price': 20, 'cost': 12, 'stock': 200},
            {'name': 'Coffee Beans 250g', 'category': 'Beverages', 'sku': 'BEV005', 'price': 220, 'cost': 150, 'stock': 25},
            
            # Snacks
            {'name': 'Potato Chips 150g', 'category': 'Snacks', 'sku': 'SNK001', 'price': 2.99, 'cost': 1.50, 'stock': 80},
            {'name': 'Mixed Nuts 200g', 'category': 'Snacks', 'sku': 'SNK002', 'price': 5.99, 'cost': 3.20, 'stock': 35},
            {'name': 'Chocolate Bar', 'category': 'Snacks', 'sku': 'SNK003', 'price': 1.99, 'cost': 0.90, 'stock': 60},
            {'name': 'Crackers Pack', 'category': 'Snacks', 'sku': 'SNK004', 'price': 3.49, 'cost': 1.80, 'stock': 40},
            
            # Dairy Products
            {'name': 'Whole Milk 1L', 'category': 'Dairy Products', 'sku': 'DAI001', 'price': 2.49, 'cost': 1.20, 'stock': 85},
            {'name': 'Cheddar Cheese 200g', 'category': 'Dairy Products', 'sku': 'DAI002', 'price': 4.99, 'cost': 2.80, 'stock': 30},
            {'name': 'Greek Yogurt 500g', 'category': 'Dairy Products', 'sku': 'DAI003', 'price': 3.99, 'cost': 2.10, 'stock': 25},
            {'name': 'Butter 250g', 'category': 'Dairy Products', 'sku': 'DAI004', 'price': 3.49, 'cost': 1.90, 'stock': 55},
            
            # Bakery
            {'name': 'White Bread Loaf', 'category': 'Bakery', 'sku': 'BAK001', 'price': 2.99, 'cost': 1.50, 'stock': 45},
            {'name': 'Croissants 6pk', 'category': 'Bakery', 'sku': 'BAK002', 'price': 4.99, 'cost': 2.50, 'stock': 20},
            {'name': 'Chocolate Muffin', 'category': 'Bakery', 'sku': 'BAK003', 'price': 2.49, 'cost': 1.20, 'stock': 35},
            
            # Fruits & Vegetables
            {'name': 'Bananas 1kg', 'category': 'Fruits & Vegetables', 'sku': 'FRU001', 'price': 60, 'cost': 42, 'stock': 8, 'unit': 'kg'},
            {'name': 'Apples 1kg', 'category': 'Fruits & Vegetables', 'sku': 'FRU002', 'price': 180, 'cost': 126, 'stock': 5, 'unit': 'kg'},
            {'name': 'Carrots 500g', 'category': 'Fruits & Vegetables', 'sku': 'VEG001', 'price': 1.99, 'cost': 0.90, 'stock': 15},
            
            # Personal Care
            {'name': 'Toothpaste 100ml', 'category': 'Personal Care', 'sku': 'PER001', 'price': 3.99, 'cost': 2.00, 'stock': 40},
            {'name': 'Shampoo 400ml', 'category': 'Personal Care', 'sku': 'PER002', 'price': 6.99, 'cost': 3.50, 'stock': 25},
            {'name': 'Hand Soap 250ml', 'category': 'Personal Care', 'sku': 'PER003', 'price': 2.99, 'cost': 1.40, 'stock': 35},
        ]
        
        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category'])
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': category,
                    'price': Decimal(str(prod_data['price'])),
                    'cost_price': Decimal(str(prod_data['cost'])),
                    'stock_quantity': prod_data['stock'],
                    'unit': prod_data.get('unit', 'pcs'),
                    'low_stock_threshold': 10
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create expense categories
        expense_categories = [
            {'name': 'Utilities', 'description': 'Electricity, water, gas, internet'},
            {'name': 'Rent', 'description': 'Store rent and property costs'},
            {'name': 'Inventory Purchase', 'description': 'Product procurement costs'},
            {'name': 'Marketing', 'description': 'Advertising and promotional expenses'},
            {'name': 'Staff Salaries', 'description': 'Employee wages and benefits'},
            {'name': 'Maintenance', 'description': 'Equipment and store maintenance'},
            {'name': 'Office Supplies', 'description': 'Stationery, printing, office materials'},
        ]
        
        for exp_cat in expense_categories:
            category, created = ExpenseCategory.objects.get_or_create(
                name=exp_cat['name'],
                defaults={'description': exp_cat['description']}
            )
            if created:
                self.stdout.write(f'Created expense category: {category.name}')
        
        # Create sample expenses
        sample_expenses = [
            {'title': 'Monthly Electricity Bill', 'category': 'Utilities', 'amount': 245.50, 'days_ago': 5},
            {'title': 'Store Rent - October', 'category': 'Rent', 'amount': 2500.00, 'days_ago': 10},
            {'title': 'Fresh Produce Purchase', 'category': 'Inventory Purchase', 'amount': 850.75, 'days_ago': 3},
            {'title': 'Social Media Ads', 'category': 'Marketing', 'amount': 150.00, 'days_ago': 7},
            {'title': 'Staff Salaries - October', 'category': 'Staff Salaries', 'amount': 4200.00, 'days_ago': 15},
            {'title': 'Cash Register Repair', 'category': 'Maintenance', 'amount': 125.00, 'days_ago': 2},
            {'title': 'Receipt Paper & Bags', 'category': 'Office Supplies', 'amount': 85.30, 'days_ago': 8},
        ]
        
        for exp_data in sample_expenses:
            category = ExpenseCategory.objects.get(name=exp_data['category'])
            expense_date = date.today() - timedelta(days=exp_data['days_ago'])
            
            expense, created = Expense.objects.get_or_create(
                title=exp_data['title'],
                defaults={
                    'category': category,
                    'amount': Decimal(str(exp_data['amount'])),
                    'expense_date': expense_date,
                    'payment_method': random.choice(['cash', 'card', 'bank_transfer']),
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f'Created expense: {expense.title}')
        
        # Create sample sales
        products = list(Product.objects.all())
        staff_user = User.objects.get(username='staff')
        
        for i in range(15):  # Create 15 sample sales
            sale_date = date.today() - timedelta(days=random.randint(0, 30))
            
            sale = Sale.objects.create(
                customer_name=random.choice([
                    'John Smith', 'Alice Johnson', 'Bob Wilson', 'Sarah Davis',
                    'Mike Brown', 'Lisa Garcia', 'Tom Miller', 'Emma Jones',
                    '', '', ''  # Some walk-in customers
                ]),
                payment_method=random.choice(['cash', 'card', 'upi']),
                created_by=random.choice([admin_user, staff_user])
            )
            
            # Add 1-4 items to each sale
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                if product.stock_quantity > 0:
                    quantity = random.randint(1, min(3, product.stock_quantity))
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price
                    )
            
            # Set payment received
            sale.payment_received = sale.total_amount + Decimal(str(round(random.uniform(0, 5), 2)))
            sale.save()
            
            if i == 0:
                self.stdout.write(f'Created sample sale: {sale.sale_number}')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nSample data created successfully!\n'
                '\nLogin credentials:\n'
                'Admin: admin / admin123\n'
                'Staff: staff / staff123\n\n'
                'Features created:\n'
                f'- {Category.objects.count()} product categories\n'
                f'- {Product.objects.count()} products (some with low stock)\n'
                f'- {Supplier.objects.count()} suppliers\n'
                f'- {ExpenseCategory.objects.count()} expense categories\n'
                f'- {Expense.objects.count()} sample expenses\n'
                f'- {Sale.objects.count()} sample sales\n'
            )
        )
