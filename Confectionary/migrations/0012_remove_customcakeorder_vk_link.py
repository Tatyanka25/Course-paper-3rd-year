# Generated by Django 5.1.7 on 2025-03-30 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Confectionary', '0011_alter_customcakeorder_social_media'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customcakeorder',
            name='vk_link',
        ),
    ]
