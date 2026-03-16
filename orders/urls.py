from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('my-orders/', views.OrderListView.as_view(), name='order_list'),
]