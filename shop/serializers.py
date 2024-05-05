from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from shop.models import Product, Category, Brand, Size, Basket, BasketItem, Order
# Create your views here.



class UserSerializer(ModelSerializer):
    password1 = serializers.CharField(write_only = True)
    password2 = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password1", "password2", "password"]
        read_only_fields = ["id", "password"]
        



    def create(self, validated_data):
        password1 = validated_data.pop("password1")
        password2 = validated_data.pop("password2")
        if password1!=password2:
            raise serializers.ValidationError("password mismatch!!")
        return User.objects.create_user(**validated_data, password=password1)
    

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class BrandSerializer(ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name"]

class SizeSerializer(ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name"]

class ProcductSerializer(ModelSerializer):
    category_object = CategorySerializer(read_only = True) # this shows category id and name
    brand_object = BrandSerializer(read_only = True)
    size_object = SizeSerializer(read_only = True, many = True)
    class Meta:
        model = Product
        fields = "__all__"

class CartProductSerialiazer(ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "price", "image"]



class BasketItemSerializer(ModelSerializer):
    item_total = serializers.IntegerField(read_only =True)
    size_object = serializers.StringRelatedField()
    product_object = CartProductSerialiazer(read_only = True)
    class Meta:
        model = BasketItem

        fields = ["id", 
                  "product_object", 
                  "size_object", 
                  "quantity", 
                  "created_date", 
                  "item_total"
                  ]
        
class BasketSerializer(ModelSerializer):
    basketitems = BasketItemSerializer(many =True)
    basket_total = serializers.CharField()
    owner = serializers.StringRelatedField()

    class Meta:
        model = Basket
        fields = ["id",
                  "owner",
                  "basketitems",
                  "basket_total"]


class OrderSerializer(ModelSerializer):
    total = serializers.CharField(read_only = True)
    basket_item_objects = BasketItemSerializer(many = True)
    user_object = serializers.StringRelatedField()
    class Meta:
        model = Order
        fields = "__all__"

