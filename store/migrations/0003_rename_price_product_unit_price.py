# Generated by Django 4.0.3 on 2023-04-24 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_cart_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='unit_price',
        ),
    ]
