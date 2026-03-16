from django.db import models
from orders.models import Order

class Payment(models.Model):

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=200)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment for Order {self.order.id}"
