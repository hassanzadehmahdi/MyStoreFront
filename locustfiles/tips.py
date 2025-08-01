# Preload related objects
from store.models import Product

Product.objects.select_related('...')
Product.objects.prefetch_related('...')

# Load only what you need
Product.objects.only('title')
Product.objects.defer('description')

# Use values
Product.objects.values()
Product.objects.values_list()

# Count properly
Product.objects.count()
list(Product.objects.all()) # BAD

# Bulk create/update
Product.objects.bulk_create([])