# Generated by Django 4.0.3 on 2023-05-12 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_alter_order_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['user__first_name', 'user__last_name'], 'permissions': [('view_history', 'Can view history')]},
        ),
    ]
