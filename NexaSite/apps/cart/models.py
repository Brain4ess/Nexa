from decimal import Decimal
from django.conf import settings
from django.db import models
from apps.catalog.models import Product
from apps.core.mixins import TimestampMixin

class Cart(TimestampMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
    )

    def __str__(self):
        if self.user:
            return f"Cart of {self.user}"
        return f"Guest cart {self.session_key}"

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        total = Decimal("0")
        for item in self.items.select_related("product").all():
            total += item.product.price * item.quantity
        return total

class CartItem(TimestampMixin):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

    @property
    def image(self):
        main = self.product.images.filter(is_main=True).first()
        return main or self.product.images.first()
