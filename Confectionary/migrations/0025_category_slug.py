# Generated by Django 5.1.7 on 2025-05-05 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Confectionary', '0024_remove_product_image_product_image_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=110, null=True),
        ),
    ]
