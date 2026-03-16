from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart_detail'),
    path('add/<int:pk>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:pk>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<int:pk>/', views.UpdateCartView.as_view(), name='update_cart'), 
]