from django.urls import path
from .views import cart_add_view, cart_remove_view, cart_update_view, cart_view

urlpatterns = [
    path("", cart_view, name="cart"),
    path("add/", cart_add_view, name="cart_add"),
    path("update/", cart_update_view, name="cart_update"),
    path("remove/", cart_remove_view, name="cart_remove"),
]
