# Generated by Django 5.1.7 on 2025-03-25 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Confectionary', '0003_alter_product_price_alter_product_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_popular',
            field=models.BooleanField(default=False),
        ),
    ]
