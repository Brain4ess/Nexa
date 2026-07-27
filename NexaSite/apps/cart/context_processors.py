import logging

from apps.cart.services import CartService

logger = logging.getLogger(__name__)

def cart_count(request):
    if not request.session.session_key:
        return {"cart_count": 0}
    count = request.session.get("_cart_count")
    if count is not None:
        return {"cart_count": "99+" if count > 99 else count}
    try:
        cart = CartService.get_cart(request)
        count = cart.items_count
        request.session["_cart_count"] = count
        return {"cart_count": "99+" if count > 99 else count}
    except Exception:
        logger.exception("Unexpected error in cart_count context processor")
        return {"cart_count": 0}
