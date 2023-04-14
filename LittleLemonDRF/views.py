from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Rating
from .serializers import RatingSerializer
from .models import MenuItem, Category
from .serializers import RatingSerializer, MenuItemSerializer, CategorySerializer


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['title']


class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

def get_permissions(self):
    if(self.request.method=='GET'):
        return []

    return [IsAuthenticated()]