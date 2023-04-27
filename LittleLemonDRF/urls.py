from django.urls import path 
from . import views 
  
urlpatterns = [ 
    path('ratings', views.RatingsView.as_view()),
    path('secret/', views.secret),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('cart/menu-items', views.CartMenuItemsView.as_view()),
    path('orders', views.OrdersView.as_view()),
    path('orders/<int:pk>', views.SingleOrdersView.as_view()),  
] 