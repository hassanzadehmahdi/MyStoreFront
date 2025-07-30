from decimal import Decimal

from django.db import transaction

from rest_framework import serializers

from store.signals import order_created
from store.models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)

    # products_count = serializers.SerializerMethodField(method_name='get_products_count')
    #
    # def get_products_count(self, collection):
    #     return collection.products.count()



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection', 'images']

    images = ProductImageSerializer(many=True, read_only=True)

    price_with_tax = serializers.SerializerMethodField(method_name='get_price_with_tax')

    def get_price_with_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # price = serializers.DecimalField(max_digits=10, decimal_places=2, source='unit_price')
    # collection = serializers.StringRelatedField()
    # collection = serializers.PrimaryKeyRelatedField()
    # collection = CollectionSerializer()
    # collection = serializers.HyperlinkedRelatedField(queryset=Collection.objects.all(), view_name='collection-detail', lookup_field='pk')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart: Cart):
        total_price = 0
        for item in cart.items.all():
            total_price += item.quantity * item.product.unit_price

        return total_price


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with given id was found!')
        return value

    def save(self):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, product_id=product_id, quantity=quantity) # or **self.validated_data

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()#read_only=True

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'birth_date', 'phone', 'membership', 'resume']


class SimpleCustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    membership = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'birth_date', 'phone', 'membership', 'resume']




class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity', 'total_price']

    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, order_item: OrderItem):
        return order_item.quantity * order_item.unit_price


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'placed_at', 'payment_status', 'items', 'total_price']

    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, order: Order):
        total_price = 0
        for item in order.items.all():
            total_price += item.quantity * item.unit_price

        return total_price

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with given id was found!')
        elif CartItem.objects.filter(cart_id=cart_id).count() < 1:
            raise serializers.ValidationError('The cart is empty!')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context.get('user_id')

            customer = Customer.objects.get(user_id=user_id)

            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)

            order_items = []
            for item in cart_items:
                order_items.append(
                    OrderItem(order=order, product=item.product, unit_price=item.product.unit_price, quantity=item.quantity)
                )

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order

