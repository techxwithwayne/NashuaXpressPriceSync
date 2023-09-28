from import_export import resources
from .models import PriceList

class pricelistResource(resources.ModelResource):
    class meta:
        model = PriceList