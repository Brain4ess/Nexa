from django.contrib import admin
from .models import Review, ReviewUpdate

class ReviewUpdateInline(admin.TabularInline):
    model = ReviewUpdate
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    can_delete = False

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "usage_period", "is_approved", "created_at")
    list_filter = ("rating", "usage_period", "is_approved")
    search_fields = ("product__name", "user__username", "title", "text")
    inlines = [ReviewUpdateInline]
