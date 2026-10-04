from decimal import Decimal, ROUND_HALF_UP
from django.db import migrations

RATE = Decimal('90')

def convert_money(value):
    if value is None:
        return value
    return (value * RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def convert_existing_values(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    Sale = apps.get_model('sales', 'Sale')
    SaleItem = apps.get_model('sales', 'SaleItem')
    Expense = apps.get_model('expenses', 'Expense')
    Supplier = apps.get_model('suppliers', 'Supplier')
    conversions = [
        (Product, ('price', 'cost_price')),
        (Sale, ('total_amount', 'discount_amount', 'tax_amount', 'payment_received', 'change_amount', 'round_up_amount')),
        (SaleItem, ('unit_price', 'total_price')),
        (Expense, ('amount',)),
        (Supplier, ('credit_limit',)),
    ]
    for model, fields in conversions:
        for row in model.objects.all().iterator():
            for field in fields:
                setattr(row, field, convert_money(getattr(row, field)))
            row.save(update_fields=list(fields))

class Migration(migrations.Migration):
    dependencies = [
        ('sales', '0002_customer_loyalty'),
        ('products', '0001_initial'),
        ('expenses', '0001_initial'),
        ('suppliers', '0001_initial'),
    ]
    operations = [migrations.RunPython(convert_existing_values, migrations.RunPython.noop)]
