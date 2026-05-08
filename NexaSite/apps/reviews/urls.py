from django.urls import path

from .views import review_create_view, reviews_more_view

urlpatterns = [
    path("product/<slug:slug>/create/", review_create_view, name="product_review_create"),
    path("product/<slug:slug>/more/", reviews_more_view, name="product_reviews_more"),
]
