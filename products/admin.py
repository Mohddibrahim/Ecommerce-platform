from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "seller", "price", "stock", "stock_status")
    list_filter = ("seller", "category")
    search_fields = ("name",)

    def stock_status(self, obj):
        if obj.stock == 0:
            return "Out of Stock"
        elif obj.stock <= 5:
            return "Low Stock"
        return "In Stock"

    stock_status.short_description = "Stock Status"