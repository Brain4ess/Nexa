import logging

from apps.cart.services import CartService

logger = logging.getLogger(__name__)

def cart_count(request):
    try:
        cart = CartService.get_cart(request)
        count = cart.items_count
        return {"cart_count": "99+" if count > 99 else count}
    except AttributeError:
        return {"cart_count": 0}
    except Exception:
        logger.exception("Unexpected error in cart_count context processor")
        return {"cart_count": 0}
