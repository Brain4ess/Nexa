from django.contrib import admin
from .models import Product, Brand, ProductImage, Attribute, ProductAttribute, CategoryAttribute

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "category", "brand", "is_active")
    list_filter = ("is_active", "category", "brand")
    search_fields = ("name",)
    inlines = [ProductImageInline, ProductAttributeInline]

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ("category", "attribute")
