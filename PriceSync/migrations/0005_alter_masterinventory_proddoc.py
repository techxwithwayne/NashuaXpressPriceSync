# Generated by Django 4.2.5 on 2023-10-06 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PriceSync', '0004_masterinventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterinventory',
            name='prodDOC',
            field=models.DateField(verbose_name='Date of Creation'),
        ),
    ]
