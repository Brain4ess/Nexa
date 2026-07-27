import logging

from django.db import transaction
from django.db.models import Sum
from apps.cart.models import Cart, CartItem

logger = logging.getLogger(__name__)

class CartService:
    @staticmethod
    def _update_cart_count_session(request, cart):
        result = cart.items.aggregate(total=Sum("quantity"))["total"]
        request.session["_cart_count"] = result or 0

    @staticmethod
    def get_cart(request):
        if request.user.is_authenticated:
            if request.session.session_key and not request.session.get("cart_merged"):
                try:
                    CartService.merge_guest_cart_to_user(request, request.user)
                    request.session["cart_merged"] = True
                except Exception:
                    logger.exception("Failed to merge guest cart for user %s", request.user)

            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart

        if not request.session.session_key:
            request.session.create()

        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart

    @staticmethod
    @transaction.atomic
    def merge_guest_cart_to_user(request, user):
        if not request.session.session_key:
            cart = Cart.objects.get_or_create(user=user)[0]
            CartService._update_cart_count_session(request, cart)
            return cart

        guest_cart = Cart.objects.filter(session_key=request.session.session_key).first()
        user_cart, _ = Cart.objects.get_or_create(user=user)

        if not guest_cart or guest_cart.pk == user_cart.pk:
            CartService._update_cart_count_session(request, user_cart)
            return user_cart

        for guest_item in guest_cart.items.select_related("product"):
            cart_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=guest_item.product,
                defaults={"quantity": guest_item.quantity},
            )

            if not created:
                cart_item.quantity += guest_item.quantity
                cart_item.save(update_fields=["quantity"])

        guest_cart.delete()
        CartService._update_cart_count_session(request, user_cart)
        return user_cart

    @staticmethod
    @transaction.atomic
    def add_product(request, product, quantity=1):
        if quantity < 1:
            raise ValueError("Quantity must be greater than zero")

        if quantity > product.stock:
            raise ValueError("Not enough stock")

        cart = CartService.get_cart(request)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = item.quantity + quantity
            if new_quantity > product.stock:
                raise ValueError("Not enough stock")
            item.quantity = new_quantity
            item.save(update_fields=["quantity"])

        CartService._update_cart_count_session(request, cart)
        return cart

    @staticmethod
    @transaction.atomic
    def update_product_quantity(request, product, quantity):
        cart = CartService.get_cart(request)
        item = CartItem.objects.filter(cart=cart, product=product).first()

        if not item:
            raise ValueError("Cart item not found")

        if quantity < 1:
            item.delete()
            CartService._update_cart_count_session(request, cart)
            return cart

        if quantity > product.stock:
            raise ValueError("Not enough stock")

        item.quantity = quantity
        item.save(update_fields=["quantity"])
        CartService._update_cart_count_session(request, cart)
        return cart

    @staticmethod
    @transaction.atomic
    def remove_product(request, product):
        cart = CartService.get_cart(request)
        CartItem.objects.filter(cart=cart, product=product).delete()
        CartService._update_cart_count_session(request, cart)
        return cart

    @staticmethod
    @transaction.atomic
    def clear_cart(request):
        cart = CartService.get_cart(request)
        cart.items.all().delete()
        CartService._update_cart_count_session(request, cart)
        return cart
