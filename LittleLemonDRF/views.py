from django.shortcuts import render
from rest_framework import generics
from .serializers import CartSerializer, AddManagerDeliveryCrewSerializer, UserSerializer, CategorySerializer, MenuItemSerializer, OrderItemSerializer, OrderSerializer
from .models import Cart, Order, OrderItem, Category, MenuItem
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
import rest_framework.status as status
from .auth import IsManager, is_admin, is_manager, is_delivery_crew, is_customer, IsCustomer
from django.shortcuts import get_object_or_404
# Categories views


class CategoriesView(generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    permission_classes = [IsAdminUser]


# Managers and crew members
class ManagersDeliveryCrewView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        try:
            group = Group.objects.get(name=kwargs.get("group"))
        except:
            return Response({"message": "Group not found"}, status.HTTP_404_NOT_FOUND)
        users = group.user_set.all()
        users = self.serializer_class(users, many=True).data
        return Response({"users": users})

    def post(self, request, *args, **kwargs):
        self.serializer_class = AddManagerDeliveryCrewSerializer

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(pk=request.data['id'])
        managers = Group.objects.get(name=kwargs.get("group"))
        managers.user_set.add(user)
        user.groups.add(managers)
        return Response({'success': True}, status.HTTP_201_CREATED)


class DeleteSingleManagersDeliveryCrew(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('pk'))
        group = Group.objects.get(name=kwargs.get("group"))
        group.user_set.remove(user)
        user.groups.remove(group)
        return Response({'success': True}, status.HTTP_200_OK)


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["title", "category__title"]
    ordering_fields = ["price", "category"]
    
    def post(self, request, *args, **kwargs):
        if (is_manager(request) or is_admin(request)):
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response({"message": "Only managers can access this."}, status=status.HTTP_403_FORBIDDEN)


class ViewSingleMenuItemView(generics.RetrieveAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]




#Orders
class OrdersView(generics.ListCreateAPIView):
    """
    Order management endpoints
    """
    queryset = Order.objects.prefetch_related(
        "orderitem_set").filter(user=4).all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ["date", "total"]
    
    def get(self, request, *args, **kwargs):
        if is_manager(request):
            queryset = self.get_queryset
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        elif is_delivery_crew(request):
            queryset = self.queryset.filter(delivery_crew=request.user.id)
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        elif is_customer(request):
            queryset = self.queryset.filter(user=request.user.id)
            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)

        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        self.permission_classes = [IsCustomer]

        if is_customer(request):
            # Get the user's cart items
            cart_items = Cart.objects.filter(user=user)
            total_price = sum(item.price for item in cart_items)

            if len(cart_items) == 0:
                raise NotAcceptable("No cart items.")

            # Create a new order
            order = Order.objects.create(
                user=user,
                total=total_price,
                date=datetime.date.today()
            )

            # Create order items from the cart items
            order_items = []
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price
                )
                order_items.append(order_item)

            # Delete the cart items for this user
            cart_items.delete()

            # Serialize the order and order items
            serializer = self.serializer_class(order)
            data = serializer.data
            data['order_items'] = OrderItemSerializer(
                order_items, many=True).data
            return Response(data, status=status.HTTP_201_CREATED)

        else:
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


class SingleOrdersView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update_order(self, order, request, id):
        """Updates the order. A manager can use this endpoint to set a delivery crew to this order, and also update the order status to 0 or 1."""
        serializer = self.serializer_class(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def handle_put_patch(self, request, id):
        """
        Handles patching the single order item
        """
        if is_delivery_crew(request):
            order = get_object_or_404(
                Order, id=id, delivery_crew=request.user.id)
            if request.data.get("status"):
                order.status = request.data.get("status")
            return self.update_order(order, request, id=id)

        elif is_manager(request):
            order = get_object_or_404(Order, id=id)
            print(order)
            if request.data.get("status"):
                order.status = request.data.get("status")
            if request.data.get("delivery_crew"):
                user = get_object_or_404(
                    User, pk=request.data.get("delivery_crew"))
                order.delivery_crew = user
            return self.update_order(order, request, id=id)

        else:
            return Response({"message": "Unauthorized"}, status.HTTP_401_UNAUTHORIZED)

    def put(self, request, pk):
        return self.handle_put_patch(request=request, id=pk)

    def patch(self, request, pk):
        return self.handle_put_patch(request=request, id=pk)

    def get(self, request, *args, **kwargs):
        """
        For fetching the order item
        """
        if (is_customer(request)):
            order = get_object_or_404(
                Order, id=kwargs.get("pk"), user=request.user.id)
            serializer = self.serializer_class(order)
            return Response(serializer.data)
        elif is_delivery_crew(request):
            order = get_object_or_404(
                Order, id=kwargs.get("pk"), delivery_crew=request.user.id)
            serializer = self.serializer_class(order)
            return Response(serializer.data)


#Cart
class CartItemsView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request, *args, **kwargs):
        carts = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(carts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        item = get_object_or_404(MenuItem, id=request.data["menuitem"])
        cart = request.data
        cart["user"] = request.user.id
        cart["unit_price"] = item.price
        cart["price"] = (cart.get("quantity") or 0) * item.price

        serializer = self.serializer_class(data=cart)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user = request.user.id
        self.queryset.filter(user=user).delete()
        return Response({"message": "Deleted"})
