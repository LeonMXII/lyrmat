from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manufacturer, Category, Product, Customer, Order, OrderItem
from .serializers import (
    ManufacturerSerializer,
    CategorySerializer,
    ProductSerializer,
    CustomerSerializer,
    OrderSerializer,
    OrderItemSerializer
)

def get_current_order(user):
    customer = get_object_or_404(Customer, user=user)
    order = Order.objects.filter(customer=customer, is_ordered=False).first()
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


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


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

        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь с таким именем уже существует."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        Customer.objects.create(user=user)

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
