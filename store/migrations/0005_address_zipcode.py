# Generated by Django 4.0.3 on 2023-04-25 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='zipcode',
            field=models.PositiveBigIntegerField(null=True),
        ),
    ]
