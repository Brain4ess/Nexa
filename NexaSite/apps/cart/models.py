from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import F, Sum
from django.db.models.fields import DecimalField
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
        result = self.items.aggregate(total=Sum("quantity"))["total"]
        return result if result is not None else 0

    @property
    def total_price(self):
        result = self.items.aggregate(
            total=Sum(F("quantity") * F("product__price"), output_field=DecimalField(max_digits=14, decimal_places=2))
        )["total"]
        if result is None:
            return Decimal("0.00")
        return result.quantize(Decimal("0.01"))

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
