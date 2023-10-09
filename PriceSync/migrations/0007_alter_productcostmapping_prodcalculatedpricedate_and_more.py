# Generated by Django 4.2.5 on 2023-10-06 10:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PriceSync', '0006_productcostmapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcostmapping',
            name='prodCalculatedPriceDate',
            field=models.DateField(default=datetime.date.today, verbose_name='Calculated On'),
        ),
        migrations.AlterField(
            model_name='productcostmapping',
            name='prodNashuaSellingPrice_USD',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='productcostmapping',
            name='prodSupplierCost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='productcostmapping',
            name='prodSupplierLandedCost_USD',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=18),
        ),
    ]
