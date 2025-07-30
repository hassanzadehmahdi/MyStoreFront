from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.status import HTTP_404_NOT_FOUND

from .pagination import DefaultPagination
from .filters import ProductFilter
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer, Order, ProductImage
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewCustomerHistoryPermissions
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, \
    AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer, \
    CreateOrderSerializer, UpdateOrderSerializer, SimpleCustomerSerializer, ProductImageSerializer


# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']


    # Instead of the django_filter
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id', None)
    #     if collection_id:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Collection cannot be deleted because it is associated with an product.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser] #FullDjangoModelPermissions

    def get_serializer_class(self):
        user = self.request.user
        if user and user.is_staff:
            return CustomerSerializer
        return SimpleCustomerSerializer

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [IsAuthenticated()]
    #     return [AllowAny()]

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            # serializer = SimpleCustomerSerializer(customer)
            serializer = self.get_serializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            # serializer = SimpleCustomerSerializer(customer, data=request.data)
            serializer = self.get_serializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return None

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermissions])
    def history(self, request, pk):
        return Response('OK')


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}









# TOKEN legion = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzMTAzMjgxLCJpYXQiOjE3NTMwMTY4ODEsImp0aSI6ImZkMDcyZTdiMjA3NTQzMjdhYWRhOGVlNjNhOWQyMTc0IiwidXNlcl9pZCI6MX0.i6dyQk9MQ02t344YZSTKt61H5cTSstVDsDCAiFnebpM
# TOKEN mahdi = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzMTg5MjE1LCJpYXQiOjE3NTMxMDI4MTUsImp0aSI6IjA2Y2Y4MmMxODA4ZTQ4ZWRhMTM3ZTdiNTljMTgzY2YzIiwidXNlcl9pZCI6Mn0.AvnBG4q6v86AJL6D-cHfsoWWf9YiIO6nSPY7jHxDyXg

#########################################################################
# Class based views with Mixins
#
# class ProductView(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#     def get_serializer_context(self):
#         return {'request': self.request}
#
#
# class ProductDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, id=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# class CollectionView(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializer
#
#     def get_serializer_context(self):
#         return {'request': self.request}
#
#
# class CollectionDetailView(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializer
#
#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), id=pk)
#         if collection.products.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it is associated with an product.'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

######################################################################
# Class base view with APIView

# class ProductView(APIView):
#     def get(self, request):
#         products_queryset =
#         serializer = ProductSerializer(products_queryset, many=True, context={'request': request})
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# class ProductDetailView(APIView):
#
#     def get(self, request, pk):
#         product = get_object_or_404(Product, id=pk)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         product = get_object_or_404(Product, id=pk)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, id=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class CollectionView(APIView):
    # def get(self, request):
    #     collections_queryset = Collection.objects.annotate(products_count=Count('products')).all()
    #     serializer = CollectionSerializer(collections_queryset, many=True, context={'request': request})
    #     return Response(serializer.data)
    #
    # def post(self, request):
    #     serializer = CollectionSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
#
# class CollectionDetailView(APIView):
#     def get(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), id=pk)
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     def put(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), id=pk)
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), id=pk)
#         if collection.products.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it is associated with an product.'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



###################################################################
#function view code:
#
# @api_view(['GET', 'POST'])
# def product_list(request):
#     if request.method == 'GET':
#         products_queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(products_queryset, many=True, context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     return None
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail(request, pk: int):
#     product = get_object_or_404(Product, id=pk)
#     if request.method == 'GET':
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     return None
#
#     # instead of get_object_or_404
#     # try:
#     #     product = Product.objects.get(id=id)
#     #     serializer = ProductSerializer(product)
#     #     return Response(serializer.data)
#     # except Product.DoesNotExist:
#     #     return Response(status=HTTP_404_NOT_FOUND)
#
# @api_view(['GET', 'POST'])
# def collection_list(request):
#     if request.method == 'GET':
#         collections_queryset = Collection.objects.annotate(products_count=Count('products')).all()
#         serializer = CollectionSerializer(collections_queryset, many=True, context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return None
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def collection_detail(request, pk: int):
#     collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), id=pk)
#     if request.method == 'GET':
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         if collection.products.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it is associated with an product.'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#     return None
#
