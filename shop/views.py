from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from django.contrib.auth.models import User
from shop.models import Product, Size, BasketItem, Order
from shop.serializers import ProcductSerializer, BasketSerializer, BasketItemSerializer

from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from rest_framework import status

from shop.serializers import UserSerializer, OrderSerializer
import razorpay

Key_id = "rzp_test_SnJESp7rS0B4eX"
key_secret  = "ZuAe8gC2opcR9yStlmyo2nN9"


class SignupView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()



class ProductListApiView(ListAPIView):

    serializer_class = ProcductSerializer

    queryset = Product.objects.all()

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class ProductDetailView(RetrieveAPIView):

    serializer_class = ProcductSerializer

    queryset = Product.objects.all()

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]



class AddToCart(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        product_obj = Product.objects.get(id=id)
        basket_obj = request.user.cart
        size__name = request.data.get("size")
        qty = request.data.get("quantity")
        size_obj = Size.objects.get(name = size__name)

        BasketItem.objects.create(
            basket_object = basket_obj,
            product_object = product_obj,
            size_object = size_obj,
            quantity = qty


        )
        return Response(data={"message":"created"})
    

class CartListView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        qs = request.user.cart
        serializer_instance = BasketSerializer(qs)
        return Response(data=serializer_instance.data)
    
class UpdateCartView(UpdateAPIView, DestroyAPIView ):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = BasketItemSerializer

    queryset = BasketItem.objects.all()

    def perform_update(self, serializer):
        size_name = self.request.data.get("size_object")
        size_object = Size.objects.get(name = size_name)
        return serializer.save(size_object=size_object)


    
class CheckoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        
        user_obj = request.user
        delivery_address = request.data.get("delivery_address")
        phone = request.data.get("phone")
        pin = request.data.get("pin")
        email = request.data.get("email")
        payment_mode = request.data.get("payment_mode")

        order_object = Order.objects.create(
            delivery_address  = delivery_address,
            user_object = user_obj,
            phone = phone,
            pin = pin,
            email = email,
            payment_mode = payment_mode

        )

        cart_items = request.user.cart.basketitems

        for bi in cart_items:
            order_object.basket_item_objects.add(bi)
            bi.is_order_placed = True
            bi.save()
        if payment_mode == "cod":
            order_object.save()
            return Response(data={"message":"created"})
        
        elif payment_mode=="online" and order_object:
            client = razorpay.Client(auth=(Key_id, key_secret))
            data = { "amount": order_object.total*100, "currency": "INR", "receipt": "order_rcptid_11" }
            payment = client.order.create(data=data)
            order_id = payment.get("id")
            key_id = Key_id
            order_total = payment.get("amount")
            order_object.order_id = order_id
            order_object.save()
            data = {"order_id":order_id, "key_id":key_id, "order_total":order_total, "user":request.user.username}



            return Response(data=data, status=status.HTTP_200_OK)
        

class PaymentVerificationView(APIView):
    def post(self, request, a8rgs, **kwargs):
        data = request.data()
        client = razorpay.Client(auth=(Key_id, key_secret))

        try:
            client.utility.verify_payment_signature(data)
            order_id = data.get("rayzorpay_order_id")
            order_object = Order.objects.get(order_id =order_id)
            order_object.is_paid = True
            return Response(data= {"message":"success"}, status=status.HTTP_200_OK)

        except:
            return Response(data={"message":"payment faIled"}, status= status.HTTP_400_BAD_REQUEST)


        







class OrderSummary(ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


    def get_queryset(self):
        return Order.objects.filter(user_object =self.request.user)
    
