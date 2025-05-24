from django.contrib.auth.models import User
from django.db import models


# Роли пользователей
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Поставщик
class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    company_name = models.CharField(max_length=100)
    contact_email = models.EmailField()

    class Meta:
        verbose_name = "Поставщики"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.company_name


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
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='products')
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    email = models.EmailField(unique=True)
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
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Позиции"
        verbose_name_plural = "Позиции"

    def save(self, *args, **kwargs):
        if not self.supplier and self.product.supplier:
            self.supplier = self.product.supplier
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# Характеристика товара
class ProductAttribute(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return self.name

# Значение характеристики
class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значения характеристик"

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"

class SupplierInvoice(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    file = models.FileField(upload_to='invoices/')
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Накладная"
        verbose_name_plural = "Накладные"
        ordering = ['-created_at']
        unique_together = ('supplier', 'order')


    def confirm(self):
        self.confirmed = True
        self.save()

    def __str__(self):
        return f"Invoice #{self.id} - {self.order}"

class SupplierInvoiceItem(models.Model):
    invoice = models.ForeignKey(SupplierInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция накладной"
        verbose_name_plural = "Позиции накладной"
        unique_together = ('invoice', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity} для накладной #{self.invoice.id}"




