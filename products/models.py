from django.db import models
from django.conf import settings
from django.db.models import Avg



class Category(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'seller'}
    )
    category = models.ForeignKey(
    Category,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)

    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_promoted = models.BooleanField(default=False)
    promotion_expires = models.DateTimeField(null=True, blank=True)

    
    @property
    def average_rating(self):
        return round(
            self.reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        )


        
    

class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()  # 1 to 5 stars
    description = models.TextField()

    image = models.ImageField(upload_to="reviews/images/", null=True, blank=True)
    video = models.FileField(upload_to="reviews/videos/", null=True, blank=True)
    
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.CASCADE,null=True,
    blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"


    
  
  
  
class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="offers/")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
  
  
  
class PromotionRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=7)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    is_paid = models.BooleanField(default=False)  # 🔥 important

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
