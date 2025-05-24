from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Manufacturer, Category, Product, Customer, Order, OrderItem, Supplier, UserProfile, \
    ProductAttribute, ProductAttributeValue, SupplierInvoice


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = Supplier
        fields = ['id', 'company_name', 'contact_email', 'user', 'user_id']


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = '__all__'


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute = ProductAttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttribute.objects.all(),
        source='attribute',
        write_only=True
    )

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'attribute_id', 'value']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    manufacturer = ManufacturerSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    attributes = ProductAttributeValueSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['supplier']

    def create(self, validated_data):
        user = self.context['request'].user
        if hasattr(user, 'supplier_profile'):
            validated_data['supplier'] = user.supplier_profile
        return super().create(validated_data)

    def validate(self, data):
        user = self.context['request'].user
        if hasattr(user, 'userprofile') and user.userprofile.role == 'supplier':
            if 'supplier' in data and data['supplier'] != user.supplier_profile:
                raise serializers.ValidationError("Вы не можете указывать чужого поставщика.")

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop('attributes', [])
        instance = super().update(instance, validated_data)

        instance.attributes.all().delete()
        for attr in attributes_data:
            ProductAttributeValue.objects.create(
                product=instance,
                attribute_id=attr['attribute_id'],
                value=attr['value']
            )
        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'



class SupplierInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierInvoice
        fields = '__all__'
        read_only_fields = ['confirmed', 'created_at']