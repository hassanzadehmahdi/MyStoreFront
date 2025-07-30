from django.urls import path, include

# from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from .views import ProductViewSet, CollectionViewSet, ReviewViewSet, CartViewSet, CartItemViewSet, CustomerViewSet, \
    OrderViewSet, OrderItemViewSet, ProductImageViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet, basename='collections')
router.register('carts', CartViewSet, basename='carts')
router.register('customers', CustomerViewSet, basename='customer')
router.register('orders', OrderViewSet, basename='order')

product_router = NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('reviews', ReviewViewSet, basename='product-reviews' )
product_router.register('images', ProductImageViewSet, basename='product-images' )

cart_router = NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', CartItemViewSet, basename='cart-items' )

order_router = NestedDefaultRouter(router, 'orders', lookup='order')
order_router.register('items', OrderItemViewSet, basename='order-items' )

urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(cart_router.urls)),
    path('', include(order_router.urls)),
]

# urlpatterns = [
#     path('products/', ProductView.as_view(), name='product-list'),
#     path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
#     path('collections/', CollectionView.as_view(), name='collection-list'),
#     path('collections/<int:pk>/', CollectionDetailView.as_view(), name='collection-detail'),
# ]