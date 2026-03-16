from django.db import models
from django.conf import settings
from apps.core.mixins import TimestampMixin
from apps.catalog.models import Product

class Cart(TimestampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    def __str__(self):
        return f"Cart of {self.user}"
    
    @property
    def total_price(self):
        return sum(
            item.product.price * item.quantity
            for item in self.items.all()
        )

class CartItem(TimestampMixin):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
