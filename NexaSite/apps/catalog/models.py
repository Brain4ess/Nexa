from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from apps.core.mixins import TimestampMixin, SlugMixin
from apps.categories.models import Category

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
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

        if is_new:
            attrs = Attribute.objects.filter(group__category=self.category)
            for attr in attrs:
                ProductAttribute.objects.get_or_create(
                    product=self,
                    attribute=attr,
                    defaults={"value": ""}
                )

    @property
    def average_rating(self):
        return self.reviews.aggregate(avg=Avg("rating"))["avg"] or 0

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

class AttributeGroup(TimestampMixin):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="attribute_groups"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="unique_attribute_group_slug_per_category"
            )
        ]

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while AttributeGroup.objects.filter(
                category=self.category,
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

class Attribute(TimestampMixin):
    group = models.ForeignKey(
        AttributeGroup,
        on_delete=models.CASCADE,
        related_name="attributes"
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["group__order", "order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "slug"],
                name="unique_attribute_slug_per_group"
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Attribute.objects.filter(
                group=self.group,
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

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
    value = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        unique_together = ("product", "attribute")
        ordering = ["attribute__group__order", "attribute__order", "attribute__name"]

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"
