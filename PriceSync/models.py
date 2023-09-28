from django.db import models

# dont forget to run py manage.py makemigrations PriceSync 
# then run py manage.py migrate PriceSync

# Create your models here.
class PriceList(models.Model):
    prodCode = models.CharField(max_length=40, primary_key=True, null=False, blank=False, verbose_name='Product Code', help_text='Enter the product code.')
    prodDesc = models.TextField(blank=True, null=True)
    prodPrice = models.DecimalField(max_digits=18, decimal_places=2)

#    def __str__(self):
#        return self.prodCode


    
