from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Cart, Order, OrderItem, Category, MenuItem
from django.contrib.auth.models import User, Group

# Create your views here.


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AddManagerDeliveryCrewSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        user = User.objects.get(id=validated_data['id'])
        group = Group.objects.get(name='manager')
        user.groups.add(group)
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price',
                  'featured', 'category', 'category_id']

    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        # read_only_fields = ["id", "user", "price"]
        fields = ['id', 'user',
                  'quantity', 'unit_price', 'price', 'menuitem']
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),    fields=['menuitem', 'user'])
        ]


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        read_only_fields = ['id', 'user', 'total', 'date', 'order_items']
        fields = ['delivery_crew', 'status', 'id',
                  'user', 'total', 'date', 'order_items']

    def get_order_items(self, obj):
        order_items = obj.orderitem_set.all()
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
        validators = [
            UniqueTogetherValidator(
                queryset=OrderItem.objects.all(),
                fields=['menuitem', 'order']
            )
        ]
