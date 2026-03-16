from django.db import models
from django.db.models import Avg
from apps.core.mixins import TimestampMixin, SlugMixin
from apps.categories.models import Category

class Brand(TimestampMixin, SlugMixin):
    name = models.CharField(max_length=255, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Product(TimestampMixin, SlugMixin):
    name = models.CharField(max_length=255, db_index=True)

    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg("rating"))["avg"]
    
    @property
    def reviews_count(self):
        return self.reviews.count()

class ProductImage(TimestampMixin):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="products/")

    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_main"]

    def __str__(self):
        return f"Image for {self.product.name}"

class Attribute(TimestampMixin, SlugMixin):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class ProductAttribute(TimestampMixin):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="product_values"
    )

    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ("product", "attribute")

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"

class CategoryAttribute(TimestampMixin):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_attributes"
    )

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="category_attributes"
    )

    class Meta:
        unique_together = ("category", "attribute")

    def __str__(self):
        return f"{self.category.name} - {self.attribute.name}"
