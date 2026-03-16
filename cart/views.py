from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product
from .models import Cart, CartItem
from django.contrib import messages
from django.db import transaction



class CartDetailView(LoginRequiredMixin, TemplateView):
    template_name = "cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context["cart"] = cart

        return context


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if product.stock < 1:
            messages.error(request, "Product is out of stock.")
            return redirect("product_detail", pk=pk)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            cart_item.quantity += 1

        cart_item.save()

        # 🔥 Decrease stock
        product.stock -= 1
        product.save()

        messages.success(request, "Product added to cart.")
        return redirect("cart_detail")



class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, pk):
        cart_item = get_object_or_404(
            CartItem,
            pk=pk,
            cart__user=request.user
        )

        product = cart_item.product
        product.stock += cart_item.quantity
        product.save()

        cart_item.delete()
        return redirect("cart_detail")
    
    


class UpdateCartView(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request, pk):
        cart_item = get_object_or_404(
            CartItem,
            pk=pk,
            cart__user=request.user
        )

        action = request.POST.get("action")
        product = cart_item.product

        if action == "increase":
            if product.stock <= 0:
                messages.error(request, "No more stock available.")
                return redirect("cart_detail")

            cart_item.quantity += 1
            product.stock -= 1

        elif action == "decrease":
            cart_item.quantity -= 1
            product.stock += 1

            if cart_item.quantity <= 0:
                cart_item.delete()
                product.save()
                return redirect("cart_detail")

        cart_item.save()
        product.save()

        return redirect("cart_detail")