from django.urls import path, include
from .permissions import IsSupplierUser
from rest_framework.routers import DefaultRouter
from .views import (
    ManufacturerViewSet,
    CategoryViewSet,
    ProductViewSet,
    CustomerViewSet,
    OrderViewSet,
    OrderItemViewSet,
    RegisterView,
    CustomAuthToken, AddToCartView, RemoveFromCartView, ConfirmOrderView, AddShippingAddressView,
    RemoveShippingAddressView, UpdateOrderStatusView, SupplierOrderViewSet, ProductAttributeViewSet,
    ProductAttributeValueViewSet, SupplierInvoiceViewSet
)

router = DefaultRouter()
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'supplier-orders', SupplierOrderViewSet, basename='supplier-orders')
router.register(r'attributes', ProductAttributeViewSet)
router.register(r'attribute-values', ProductAttributeValueViewSet)
router.register(r'invoices', SupplierInvoiceViewSet, basename='supplierinvoice')



urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/confirm/', ConfirmOrderView.as_view(), name='confirm_order'),
    path('cart/address/add/', AddShippingAddressView.as_view(), name='add_shipping_address'),
    path('cart/address/remove/', RemoveShippingAddressView.as_view(), name='remove_shipping_address'),
    path('orders/<int:order_id>/status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
]




