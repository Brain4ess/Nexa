from django.db import models
from django.conf import settings
from apps.catalog.models import Product
from apps.core.mixins import TimestampMixin

class Review(TimestampMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField(blank=True)

    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.product.name} - {self.rating}"
