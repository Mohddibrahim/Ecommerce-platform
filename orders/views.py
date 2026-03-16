from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.db import transaction
from decimal import Decimal

from cart.models import Cart
from .models import Order, OrderItem


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = Cart.objects.get(user=self.request.user)
        total = Decimal(0)

        for item in cart.items.all():
            total += item.product.price * item.quantity

        context["total"] = total
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)

        total = Decimal(0)
        for item in cart.items.all():
            total += item.product.price * item.quantity

        order = Order.objects.create(
    user=request.user,
    total_amount=total,
    status='paid'
)

        for item in cart.items.all():
            if item.quantity > item.product.stock:
              raise ValueError("Not enough stock")
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete()

        return redirect("order_list")


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "order_list.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction


@login_required
@transaction.atomic
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)

    if order.status != "paid":
        return redirect("order_list")

    for item in order.items.all():
        item.product.stock += item.quantity
        item.product.save()

    order.status = "cancelled"
    order.save()

    return redirect("order_list")
