from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator
from django.db import models

from apps.catalog.models import Product
from apps.core.mixins import TimestampMixin

class Review(TimestampMixin):
    class UsagePeriod(models.TextChoices):
        FEW_DAYS = "few_days", "Несколько суток"
        LESS_THAN_MONTH = "less_month", "Менее месяца"
        MORE_THAN_MONTH = "more_month", "Более месяца"
        MORE_THAN_3_MONTHS = "more_3_months", "Более 3 месяцев"
        MORE_THAN_6_MONTHS = "more_6_months", "Более 6 месяцев"
        MORE_THAN_YEAR = "more_year", "Более года"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=50, blank=True)
    text = models.TextField(validators=[MaxLengthValidator(3000)])
    usage_period = models.CharField(
        max_length=32,
        choices=UsagePeriod.choices,
    )
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_review_per_user_product",
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}"
