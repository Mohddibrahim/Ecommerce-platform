# accounts/views.py
from django.views.generic import CreateView,ListView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect,render
from .forms import RegisterForm
from .models import User,SellerComplaint
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count,Q
from orders.models import OrderItem
from django.views.generic import TemplateView
from orders.models import Order
from products.models import Review,PromotionRequest,Product
from .models import SellerComplaint
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/customer_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context["orders"] = Order.objects.filter(user=user)
        context["reviews"] = Review.objects.filter(user=user)
        context["complaints"] = SellerComplaint.objects.filter(customer=user)

        context["total_orders"] = context["orders"].count()
        context["total_reviews"] = context["reviews"].count()
        context["total_complaints"] = context["complaints"].count()

        return context



@login_required
def approve_seller(request, pk):
    if request.user.role != "admin":
        return redirect("product_list")

    seller = get_object_or_404(User, pk=pk, role="seller")
    seller.is_approved = True
    seller.is_blocked = False
    seller.save()
    return redirect("seller_management")


@login_required
def block_seller(request, pk):
    if request.user.role != "admin":
        return redirect("product_list")

    seller = get_object_or_404(User, pk=pk, role="seller")
    seller.is_blocked = True
    seller.save()
    return redirect("seller_management")


class AdminRequiredMixin(UserPassesTestMixin):
    login_url = "login"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == "admin"

    def handle_no_permission(self):
        return redirect("product_list")

from django.db.models import Count, Q

class SellerManagementView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/seller_management.html"
    context_object_name = "sellers"

    def get_queryset(self):
        return User.objects.filter(role="seller").annotate(
            complaint_count=Count("complaints", distinct=True),
            product_count=Count("product", distinct=True),
            order_count=Count(
                "product__orders__order",
                filter=Q(product__orders__order__status="delivered"),
                distinct=True
            ),
            promotion_count=Count(
                "promotionrequest",
                filter=Q(promotionrequest__status="approved"),
                distinct=True
            ),
            pending_promo_count=Count(
                "promotionrequest",
                filter=Q(promotionrequest__status="pending"),
                distinct=True
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sellers = User.objects.filter(role="seller")

        context["total_sellers"] = sellers.count()
        context["pending_sellers"] = sellers.filter(is_approved=False).count()
        context["blocked_sellers"] = sellers.filter(is_blocked=True).count()

        context["pending_promotion_count"] = PromotionRequest.objects.filter(
            status="pending"
        ).count()

        return context



class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        user = form.save(commit=False)

       
        user.role = "customer"
        user.is_approved = True   
        user.save()

        login(self.request, user)
        return redirect("product_list")
    
    
class SellerRegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "accounts/seller_signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = "seller"
        user.is_approved = False   # must be approved by admin
        user.save()
        return redirect("login")
    

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        user = form.get_user()

        # Seller not approved
        if user.role == "seller" and not user.is_approved:
            messages.error(self.request, "Waiting for admin approval.")
            return redirect("login")

        # Seller blocked
        if user.role == "seller" and user.is_blocked:
            messages.error(self.request, "Your account is blocked.")
            return redirect("login")

        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user

        if user.role == "admin":
            return reverse_lazy("seller_management")

        elif user.role == "seller":
            return reverse_lazy("seller_products")

        return reverse_lazy("product_list")


@login_required
def add_complaint(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)

    if order_item.order.user != request.user:
        return redirect("order_list")

    if order_item.order.status not in ["paid", "delivered"]:
        return redirect("order_list")

    # Prevent duplicate complaint
    if SellerComplaint.objects.filter(order_item=order_item).exists():
        messages.warning(request, "Complaint already submitted for this order.")
        return redirect("order_list")

    if request.method == "POST":
        SellerComplaint.objects.create(
            seller=order_item.product.seller,
            customer=request.user,
            product=order_item.product,
            order_item=order_item,
            issue_type=request.POST.get("issue_type"),
            message=request.POST.get("message")
        )

        messages.success(request, "Complaint submitted successfully!")
        return redirect("order_list")

    return render(request, "complaint_form.html", {"item": order_item})



class ComplaintManagementView(AdminRequiredMixin, ListView):
    model = SellerComplaint
    template_name = "accounts/seller_complaints.html"
    context_object_name = "complaints"

    def get_queryset(self):
        seller_id = self.kwargs.get("seller_id")

        qs = SellerComplaint.objects.select_related(
            "seller",
            "customer",
            "product"
        )

        if seller_id:
            qs = qs.filter(seller__id=seller_id)

        return qs.order_by("-id")

        
from django.contrib.auth.mixins import LoginRequiredMixin

class SellerComplaintView(LoginRequiredMixin, ListView):
    model = SellerComplaint
    template_name = "accounts/seller_complaints.html"
    context_object_name = "complaints"

    def get_queryset(self):
        if self.request.user.role != "seller":
            return SellerComplaint.objects.none()

        return SellerComplaint.objects.filter(
            seller=self.request.user
        ).select_related(
            "customer", "product"
        ).order_by("-created_at")


@login_required
def update_complaint_status(request, pk):
    if request.user.role != "admin":
        return redirect("product_list")

    complaint = get_object_or_404(SellerComplaint, pk=pk)

    complaint.status = request.POST.get("status")
    complaint.admin_note = request.POST.get("admin_note")

    if complaint.status == "resolved":
        from django.utils import timezone
        complaint.resolved_at = timezone.now()

    complaint.save()

    return redirect("complaint_management")

class MyComplaintsView(LoginRequiredMixin, ListView):
    model = SellerComplaint
    template_name = "accounts/my_complaints.html"
    context_object_name = "complaints"

    def get_queryset(self):
        return SellerComplaint.objects.filter(customer=self.request.user).order_by("-created_at")
    
    
    
@login_required
def edit_complaint(request, pk):
    complaint = get_object_or_404(SellerComplaint, pk=pk)

    # Only customer who created it can edit
    if complaint.customer != request.user:
        return redirect("my_complaints")

    # Cannot edit resolved complaints
    if complaint.status == "resolved":
        messages.error(request, "Resolved complaints cannot be edited.")
        return redirect("my_complaints")

    if request.method == "POST":
        complaint.issue_type = request.POST.get("issue_type")
        complaint.message = request.POST.get("message")
        complaint.save()

        messages.success(request, "Complaint updated successfully.")
        return redirect("my_complaints")

    return render(request, "accounts/edit_complaint.html", {
        "complaint": complaint
    })

    

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import SellerComplaint


@login_required
def delete_complaint(request, pk):
    complaint = get_object_or_404(
        SellerComplaint,
        pk=pk,
        customer=request.user   # only owner can delete
    )

    if request.method == "POST":
        complaint.delete()
        return redirect("my_complaints")

    return render(request, "accounts/delete_confirm.html", {
        "complaint": complaint
    })
