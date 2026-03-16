from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class SellerRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role == 'seller' and user.is_approved

    def handle_no_permission(self):
        messages.error(self.request, "Seller approval required.")
        return redirect("product_list")