from django.db import models
from django.utils.text import slugify

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SlugMixin(models.Model):
    slug = models.SlugField(unique=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug and hasattr(self, "name"):
            self.slug = slugify(self.name)
        if self.slug:
            model_class = self.__class__
            base_slug = self.slug
            slug = base_slug
            counter = 1
            while model_class.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
