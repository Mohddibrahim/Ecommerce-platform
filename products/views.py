from datetime import timedelta
from django.utils import timezone

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.contrib import messages
from django.db.models import Sum

from sellers.mixin import SellerRequiredMixin
from accounts.views import AdminRequiredMixin
from accounts.models import SellerComplaint
from orders.models import OrderItem

from .models import Product, Review, Category,Offer,PromotionRequest


# =========================
# CATEGORY VIEWS
# =========================

class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    fields = ["name"]
    template_name = "products/category_form.html"
    success_url = reverse_lazy("category_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CategoryEditView(AdminRequiredMixin, UpdateView):
    model = Category
    fields = ["name"]
    template_name = "products/category_form.html"
    success_url = reverse_lazy("category_list")


class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = "products/catergory_confirm.html"
    success_url = reverse_lazy("category_list")


# =========================
# PUBLIC PRODUCT VIEWS
# =========================

class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        """
        Returns all available products from approved sellers,
        and automatically removes expired promotions.
        """
        # 🔹 Auto remove expired promotions
        Product.objects.filter(
            is_promoted=True,
            promotion_expires__lt=timezone.now()
        ).update(is_promoted=False, promotion_expires=None)

        # 🔹 Get all active products
        return Product.objects.filter(
            is_available=True,
            seller__is_approved=True,
            seller__is_blocked=False
        ).order_by("-is_promoted", "-created_at")

    def get_context_data(self, **kwargs):
        """
        Adds offers to the context for the homepage carousel.
        """
        context = super().get_context_data(**kwargs)
        context["offers"] = Offer.objects.filter(active=True).order_by("-id")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True,
            seller__is_approved=True,
            seller__is_blocked=False
        )


# =========================
# SELLER DASHBOARD
# =========================

class SellerProductListView(LoginRequiredMixin, SellerRequiredMixin, ListView):
    model = Product
    template_name = "products/seller_product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = self.get_queryset()

        context["total_products"] = products.count()
        context["total_stock"] = products.aggregate(Sum("stock"))["stock__sum"] or 0
        context["low_stock"] = products.filter(stock__lte=5, stock__gt=0).count()
        context["out_of_stock"] = products.filter(stock=0).count()

        context["reviews"] = Review.objects.filter(
            product__seller=self.request.user
        ).select_related("product", "user").order_by("-id")

        context["complaints"] = SellerComplaint.objects.filter(
            seller=self.request.user
        ).select_related("product", "customer").order_by("-id")

        context["total_reviews"] = context["reviews"].count()
        context["total_complaints"] = context["complaints"].count()

        return context


# =========================
# PRODUCT CRUD
# =========================

class ProductCreateView(LoginRequiredMixin, SellerRequiredMixin, CreateView):
    model = Product
    fields = ["category", "name", "description", "price", "stock", "image"]
    template_name = "products/product_form.html"
    success_url = reverse_lazy("seller_products")

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.slug = slugify(form.instance.name)
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, SellerRequiredMixin, UpdateView):
    model = Product
    fields = ["category", "name", "description", "price", "stock", "image"]
    template_name = "products/product_form.html"
    success_url = reverse_lazy("seller_products")

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, SellerRequiredMixin, DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("seller_products")

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)


# =========================
# PROMOTION SYSTEM (7 DAYS)
# =========================
@login_required
def request_promotion(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == "POST":

        promo = PromotionRequest.objects.create(
            product=product,
            seller=request.user,
            amount=199.00,
            duration_days=7,
            is_paid=True  # simulate payment success
        )

        messages.success(request, "Promotion payment successful. Awaiting admin approval.")
        return redirect("seller_products")

    return render(request, "products/promotion_checkout.html", {
        "product": product,
        "amount": 199.00
    })





from django.db.models import Sum, Count

class PromotionManagementView(AdminRequiredMixin, ListView):
    model = PromotionRequest
    template_name = "products/promotion_management.html"
    context_object_name = "promotions"

    def get_queryset(self):
        qs = PromotionRequest.objects.select_related(
            "product", "seller"
        ).order_by("-requested_at")

        seller_id = self.request.GET.get("seller")
        if seller_id:
            qs = qs.filter(seller__id=seller_id)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["approved_count"] = PromotionRequest.objects.filter(
            status="approved"
        ).count()

        context["total_revenue"] = PromotionRequest.objects.filter(
            status="approved"
        ).aggregate(total=Sum("amount"))["total"] or 0

        return context



@login_required
def approve_promotion(request, pk):
    if request.user.role != "admin":
        return redirect("product_list")

    promo = get_object_or_404(PromotionRequest, pk=pk)

    promo.status = "approved"
    promo.product.is_promoted = True
    promo.product.save()
    promo.save()

    return redirect("promotion_management")


@login_required
def reject_promotion(request, pk):
    if request.user.role != "admin":
        return redirect("product_list")

    promo = get_object_or_404(PromotionRequest, pk=pk)
    promo.status = "rejected"
    promo.save()

    return redirect("promotion_management")


# =========================
# REVIEWS
# =========================

@login_required
def add_review(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id)

    if order_item.order.user != request.user:
        return redirect("order_list")

    if order_item.order.status not in ["paid", "delivered"]:
        return redirect("order_list")

    review_count = Review.objects.filter(
        product=order_item.product,
        user=request.user
    ).count()

    if review_count >= 3:
        messages.warning(request, "You can only review this product 3 times.")
        return redirect("order_list")

    if request.method == "POST":
        Review.objects.create(
            product=order_item.product,
            user=request.user,
            order_item=order_item,
            rating=request.POST.get("rating"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
            video=request.FILES.get("video"),
        )

        messages.success(request, "Review submitted successfully!")
        return redirect("order_list")

    return render(request, "review_form.html", {"item": order_item})


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)

    if request.method == "POST":
        review.rating = request.POST.get("rating")
        review.description = request.POST.get("description")
        review.save()
        messages.success(request, "Review updated.")
        return redirect("product_detail", pk=review.product.pk)

    return render(request, "products/edit_review.html", {"review": review})


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)

    if request.method == "POST":
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect("product_detail", pk=review.product.pk)

    return render(request, "products/delete_review.html", {"review": review})



class MyReviewsView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "accounts/my_reviews.html"
    context_object_name = "reviews"
    

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).order_by("-created_at")