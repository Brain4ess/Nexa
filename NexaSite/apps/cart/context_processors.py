from apps.cart.services import CartService

def cart_count(request):
    try:
        cart = CartService.get_cart(request)
        return {"cart_count": cart.items_count}
    except Exception:
        return {"cart_count": 0}
