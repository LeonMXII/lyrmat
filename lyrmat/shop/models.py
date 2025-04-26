from django.contrib.auth.models import User
from django.db import models

# Производитель
class Manufacturer(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Производители"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name

# Категория товара
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Категории"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

# Товар
class Product(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_lte_enabled = models.BooleanField(default=False)
    release_date = models.DateField()

    class Meta:
        verbose_name = "Товары"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

# Клиент
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Клиенты"
        verbose_name_plural = "Клиенты"
    def __str__(self):
        return self.name

# Заказ клиента
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    is_ordered = models.BooleanField(default=False)

    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Заказы"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.name}"

# Позиция заказа
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиции"
        verbose_name_plural = "Позиции"
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
