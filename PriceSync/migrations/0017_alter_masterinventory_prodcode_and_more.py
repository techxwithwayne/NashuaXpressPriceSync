# Generated by Django 4.2.5 on 2023-10-23 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PriceSync', '0016_masterinventory_prodid_productcostmapping_prodid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterinventory',
            name='prodCode',
            field=models.CharField(default=0, help_text='Enter the product code.', max_length=40, verbose_name='Product Code'),
        ),
        migrations.AlterField(
            model_name='masterinventory',
            name='prodID',
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='productcostmapping',
            name='prodID',
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='productcostmapping',
            name='prodSupplierCode',
            field=models.CharField(default=0, help_text='Enter the product supplier code.', max_length=40, verbose_name='Product Supplier Code'),
        ),
    ]
