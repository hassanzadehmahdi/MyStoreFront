from django.contrib import admin, messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode

from .models  import Collection, Product, Cart, Customer, Promotion, Address, CartItem, Order, OrderItem, ProductImage


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
            ('10=<', 'Ok')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        elif self.value() == '10=<':
            return queryset.filter(inventory__gte=10)
        else:
            return queryset


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    readonly_fields = ('thumbnail',)

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html('<img src="{}" class="thumbnail" />', instance.image.url)
        else:
            return ''


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ['title']
    }
    autocomplete_fields = ['collection']
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection']
    list_filter = ['collection', 'last_update', InventoryFilter]
    search_fields = ['title']

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'LOW'
        else:
            return 'HIGH'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(request, f'{updated_count} products were successfully updated.', messages.INFO)

    class Media:
        css = {
            'all': ['store/styles.css']
        }


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']
    autocomplete_fields = ['user']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = f'{reverse('admin:store_order_changelist')}?{urlencode({'customer__id': str(customer.id)})}'

        return format_html('<a href={}>{}</a>', url, f'{customer.orders_count} orders')

    @admin.display(ordering='user__first_name')
    def first_name(self, customer):
        return customer.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self, customer):
        return customer.user.last_name

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count('order'))



class OrderItemInline(admin.TabularInline): #admin.StackedInline
    model = OrderItem
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    list_display = ['id', 'placed_at', 'customer', 'payment_status']
    list_per_page = 10
    inlines = [OrderItemInline]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = f'{reverse('admin:store_product_changelist')}?{urlencode({'collection__id': str(collection.id)})}'

        return format_html('<a href={}>{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('products'))


# Register your models here.
# admin.site.register(Collection)
# admin.site.register(Product)
# admin.site.register(Customer)
# admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Promotion)
admin.site.register(Address)
admin.site.register(CartItem)
admin.site.register(OrderItem)
