from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manufacturer, Category, Product, Customer, Order, OrderItem, UserProfile, Supplier, \
    ProductAttribute, ProductAttributeValue, SupplierInvoice
from .permissions import IsSupplierUser, IsAdminOrOwner
from .serializers import (
    ManufacturerSerializer,
    CategorySerializer,
    ProductSerializer,
    CustomerSerializer,
    OrderSerializer,
    OrderItemSerializer, ProductAttributeSerializer, ProductAttributeValueSerializer, SupplierInvoiceSerializer
)

def get_current_order(user):
    customer = get_object_or_404(Customer, user=user)
    order, _ = Order.objects.get_or_create(customer=customer, is_ordered=False)
    return order


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = get_object_or_404(UserProfile, user=user)
        if profile.role == 'supplier':
            supplier = get_object_or_404(Supplier, user=user)
            return Product.objects.filter(supplier=supplier)
        return Product.objects.all()

    def perform_create(self, serializer):
        profile = get_object_or_404(UserProfile, user=self.request.user)
        if profile.role != 'supplier':
            raise PermissionDenied("Только поставщики могут создавать товары.")

        supplier = get_object_or_404(Supplier, user=self.request.user)
        serializer.save(supplier=supplier)

    def perform_update(self, serializer):
        instance = self.get_object()
        supplier = get_object_or_404(Supplier, user=self.request.user)
        if instance.supplier != supplier:
            raise PermissionDenied("Нельзя редактировать чужой товар.")
        serializer.save()

    def perform_destroy(self, instance):
        supplier = get_object_or_404(Supplier, user=self.request.user)
        if instance.supplier != supplier:
            raise PermissionDenied("Нельзя удалить чужой товар.")
        instance.delete()


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=user)


# контроллер для работы с заказами
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer = get_object_or_404(Customer, user=user)
        return Order.objects.filter(customer=customer, is_ordered=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_staff:
            customer = get_object_or_404(Customer, user=request.user)
            if instance.customer != customer:
                return Response({'error': 'Нет доступа к заказу'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def supplier_orders(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)

        if profile.role != 'supplier':
            return Response({'error': 'Только поставщики могут просматривать свои заказы'}, status=403)

        supplier = get_object_or_404(Supplier, user=user)
        order_items = OrderItem.objects.filter(product__supplier=supplier)
        order_ids = order_items.values_list('order_id', flat=True).distinct()
        orders = Order.objects.filter(id__in=order_ids, is_ordered=True).distinct()

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

# контроллер для работы с позициями в заказе
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order = get_current_order(self.request.user)
        if order:
            return OrderItem.objects.filter(order=order)
        return OrderItem.objects.none()


# Работа со статусом заказа
class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, order_id):
        is_paid = request.data.get('is_paid')

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

        order.is_paid = is_paid
        order.save()

        return Response({'message': 'Статус заказа обновлён'}, status=status.HTTP_200_OK)


# Регистрация пользователей
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        role = request.data.get("role")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь с таким именем уже существует."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        UserProfile.objects.create(user=user, role=role)

        if role == 'customer':
            Customer.objects.create(user=user, email=email, name=username)
        elif role == 'supplier':
            Supplier.objects.create(user=user, company_name=request.data.get("company_name", username),
                                    contact_email=email)

        token = Token.objects.create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key})


# Добавить товар в корзину
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        order = get_current_order(request.user)
        if not order:
            customer = get_object_or_404(Customer, user=request.user)
            order = Order.objects.create(customer=customer, is_ordered=False)

        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        order_item.quantity = order_item.quantity + quantity if not created else quantity
        order_item.save()

        return Response({'message': 'Продукт добавлен в корзину'}, status=status.HTTP_200_OK)


# Удалить товар из корзины
class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        order = get_current_order(request.user)

        if not order:
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = OrderItem.objects.get(order=order, product__id=product_id)
            item.delete()
            return Response({'message': 'Товар удалён из корзины.'}, status=status.HTTP_200_OK)
        except OrderItem.DoesNotExist:
            return Response({'error': 'Товара нет в корзине.'}, status=status.HTTP_400_BAD_REQUEST)


# Отправка email
def send_email(user_email, order_id):
    subject = f"Подтверждение заказа #{order_id}"
    message = f"Спасибо за ваш заказ #{order_id} в магазине Lyrmat!\nМы начали обработку заказа."
    try:
        send_mail(subject, message, 'noreply@lyrmat.com', [user_email])
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")


# Подтверждение заказа
class ConfirmOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order = get_current_order(request.user)

        if not order:
            return Response({'error': 'Активный заказ не найден.'}, status=status.HTTP_400_BAD_REQUEST)

        if not order.shipping_address or not order.city or not order.postal_code:
            return Response({'error': 'Адрес доставки не указан.'}, status=status.HTTP_400_BAD_REQUEST)

        if not order.items.exists():
            return Response({'error': 'Корзина пуста.'}, status=status.HTTP_400_BAD_REQUEST)

        order.is_ordered = True
        order.save()

        send_email(request.user.email, order.id)

        return Response({'message': 'Заказ подтверждён.'}, status=status.HTTP_200_OK)


# Добавление адреса доставки
class AddShippingAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer = get_object_or_404(Customer, user=request.user)
        order = get_current_order(request.user)

        if not order:
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        address = request.data.get('shipping_address')
        city = request.data.get('city')
        postal_code = request.data.get('postal_code')

        if not address or not city or not postal_code:
            return Response({'error': 'Заполните все поля адреса.'}, status=status.HTTP_400_BAD_REQUEST)

        order.shipping_address = address
        order.city = city
        order.postal_code = postal_code
        order.save()

        return Response({'message': 'Адрес доставки успешно добавлен.'}, status=status.HTTP_200_OK)


# Удаление адреса доставки
class RemoveShippingAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        customer = get_object_or_404(Customer, user=request.user)
        order = get_current_order(request.user)

        if not order:
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        order.shipping_address = None
        order.city = None
        order.postal_code = None
        order.save()

        return Response({'message': 'Адрес доставки удалён.'}, status=status.HTTP_200_OK)

class SupplierOrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSupplierUser]

    def list(self, request):
        supplier = get_object_or_404(Supplier, user=request.user)
        items = OrderItem.objects.filter(product__supplier=supplier, order__is_ordered=True)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_shipped(self, request, pk=None):
        item = get_object_or_404(OrderItem, pk=pk, product__supplier__user=request.user)
        item.status = 'shipped'
        item.save()
        return Response({'message': 'Статус отправки обновлён.'}, status=status.HTTP_200_OK)

class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer
    permission_classes = [IsAdminUser]


class ProductAttributeValueViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer
    permission_classes = [IsAuthenticated]


class SupplierInvoiceViewSet(viewsets.ModelViewSet):
    queryset = SupplierInvoice.objects.all()
    serializer_class = SupplierInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsSupplierUser]

    def get_queryset(self):
        supplier = get_object_or_404(Supplier, user=self.request.user)
        return SupplierInvoice.objects.filter(supplier=supplier)

    def perform_create(self, serializer):
        supplier = get_object_or_404(Supplier, user=self.request.user)
        serializer.save(supplier=supplier)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsSupplierUser])
    def confirm(self, request, pk=None):
        invoice = self.get_object()
        if invoice.confirmed:
            return Response({'message': 'Накладная уже подтверждена.'}, status=status.HTTP_400_BAD_REQUEST)
        invoice.confirmed = True
        invoice.save()
        return Response({'message': 'Накладная подтверждена.'}, status=status.HTTP_200_OK)
