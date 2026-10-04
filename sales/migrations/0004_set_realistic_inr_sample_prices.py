from decimal import Decimal
from django.db import migrations

PRICES = {
    'BEV001': (40, 28), 'BEV002': (40, 28), 'BEV003': (120, 84),
    'BEV004': (20, 12), 'BEV005': (220, 150), 'SNK001': (30, 21),
    'SNK002': (180, 126), 'SNK003': (50, 35), 'SNK004': (60, 42),
    'DAI001': (65, 46), 'DAI002': (180, 126), 'DAI003': (120, 84),
    'DAI004': (140, 98), 'BAK001': (50, 35), 'BAK002': (180, 126),
    'BAK003': (60, 42), 'FRU001': (60, 42), 'FRU002': (180, 126),
    'VEG001': (40, 28), 'PER001': (110, 77), 'PER002': (250, 175),
    'PER003': (45, 32),
}

def set_prices(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for sku, (price, cost) in PRICES.items():
        Product.objects.filter(sku=sku).update(price=Decimal(price), cost_price=Decimal(cost))

class Migration(migrations.Migration):
    dependencies = [('sales', '0003_convert_existing_currency_to_inr')]
    operations = [migrations.RunPython(set_prices, migrations.RunPython.noop)]
