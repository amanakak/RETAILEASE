from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('sales', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('loyalty_points', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.AddField(model_name='sale', name='customer', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='sales.customer')),
        migrations.AddField(model_name='sale', name='loyalty_points_earned', field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name='sale', name='loyalty_points_redeemed', field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name='sale', name='round_up_amount', field=models.DecimalField(decimal_places=2, default=0, max_digits=10)),
    ]
