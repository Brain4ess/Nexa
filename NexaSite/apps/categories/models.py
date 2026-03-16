from django.db import models
from apps.core.mixins import TimestampMixin, SlugMixin

class Category(TimestampMixin, SlugMixin):
    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
