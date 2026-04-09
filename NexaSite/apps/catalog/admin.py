from django.contrib import admin
from .models import Product, ProductImage, Attribute, ProductAttribute, AttributeGroup

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("id", "name", "price", "stock", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name",)
    inlines = [ProductImageInline, ProductAttributeInline]

class AttributeInline(admin.TabularInline):
    model = Attribute
    extra = 1

@admin.register(AttributeGroup)
class AttributeGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "order")
    list_filter = ("category",)
    search_fields = ("name",)
    inlines = [AttributeInline]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "group", "order")
    list_filter = ("group",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute", "value")
    list_filter = ("attribute__group",)
    search_fields = ("product__name", "attribute__name")
