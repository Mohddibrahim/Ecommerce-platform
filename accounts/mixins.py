from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

class AdminRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "Admin access required.")
        return redirect("product_list")