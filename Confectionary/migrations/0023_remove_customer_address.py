# Generated by Django 5.1.7 on 2025-04-28 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Confectionary', '0022_alter_order_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
    ]
