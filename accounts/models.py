from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)
    
    is_blocked = models.BooleanField(default=False)

    def is_seller(self):
        return self.role == 'seller'

    def is_customer(self):
        return self.role == 'customer'
  
  
class SellerComplaint(models.Model):

    ISSUE_TYPES = [
        ("late_delivery", "Late Delivery"),
        ("damaged_product", "Damaged Product"),
        ("wrong_item", "Wrong Item"),
        ("fake_product", "Fake Product"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_review", "In Review"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="complaints",
        limit_choices_to={"role": "seller"}
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="complaints_made"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    order_item = models.ForeignKey(
        "orders.OrderItem",
        on_delete=models.CASCADE
    )

    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES, default="other")
    message = models.TextField()
    admin_note = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer.username} → {self.seller.username}"
