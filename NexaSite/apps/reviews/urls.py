from django.urls import path

from .views import review_create_view, review_delete_view, review_update_view, reviews_more_view

urlpatterns = [
    path("product/<slug:slug>/create/", review_create_view, name="product_review_create"),
    path("product/<slug:slug>/more/", reviews_more_view, name="product_reviews_more"),
    path("product/<slug:slug>/<int:review_id>/update/", review_update_view, name="product_review_update"),
    path("product/<slug:slug>/<int:review_id>/delete/", review_delete_view, name="product_review_delete"),
]
