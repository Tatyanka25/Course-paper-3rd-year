# Generated by Django 5.1.7 on 2025-03-30 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Confectionary', '0015_alter_customcakeorder_social_media'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customcakeorder',
            name='delivery_method',
            field=models.CharField(choices=[('Самовывоз', 'Самовывоз'), ('Доставка по городу', 'Доставка по городу')], default=[('Самовывоз', 'Самовывоз'), ('Доставка по городу', 'Доставка по городу')], max_length=20),
        ),
    ]
