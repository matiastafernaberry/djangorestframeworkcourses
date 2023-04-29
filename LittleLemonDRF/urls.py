from django.urls import include, path

from .views import CartItemsView
from .views import OrdersView, SingleOrdersView
from .views import (CategoriesView,
                          DeleteSingleManagersDeliveryCrew,
                          ManagersDeliveryCrewView, MenuItemsView,
                          ViewSingleMenuItemView)

urlpatterns = [
    # user geoup
    path('api/groups/<str:group>/users',
         ManagersDeliveryCrewView.as_view(), name="Create Manager | Delivery Crew"),
    path('api/groups/<str:group>/users/<int:pk>',
         DeleteSingleManagersDeliveryCrew.as_view(), name="Manager | Delivery Crew"),


    # categories
    path('api/categories', CategoriesView.as_view()),


    # menu items
    path('api/menu-items', MenuItemsView.as_view()),
    path('api/menu-items/<int:pk>', ViewSingleMenuItemView.as_view()),


    # cart items
    path("api/cart/menu-items", CartItemsView.as_view(), name="Carts"),


    # Order items
    path("api/orders", OrdersView.as_view(), name="Orders"),
    path("api/orders/<int:pk>",
         SingleOrdersView.as_view(), name="SingleOrder"),


    # Add djoser AUTH urs
    path('api/', include("djoser.urls")),
    path('', include("djoser.urls.authtoken")),
]
