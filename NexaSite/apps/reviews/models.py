from datetime import timedelta
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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

    @property
    def updates_count(self):
        return self.updates.count()

    @property
    def can_add_update(self):
        if self.updates_count >= 5:
            return False

        last_update = self.updates.order_by("-created_at").first()
        if not last_update:
            return True

        return timezone.now() - last_update.created_at >= timedelta(days=3)

def validate_max_10_lines(value):
    if len(value.splitlines()) > 10:
        raise ValidationError("Текст не должен превышать 10 строк")

class ReviewUpdate(TimestampMixin):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="updates",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_updates",
    )
    text = models.TextField(validators=[MaxLengthValidator(1000), validate_max_10_lines])

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Update for review #{self.review_id}"
