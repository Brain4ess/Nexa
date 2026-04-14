from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from apps.catalog.models import Product
from apps.cart.services import CartService

def cart_view(request):
    cart = CartService.get_cart(request)
    items = cart.items.select_related("product").prefetch_related("product__images")

    return render(request, "pages/cart.html", {
        "cart": cart,
        "items": items,
    })

def cart_add_view(request):
    if request.method != "POST":
        return redirect("cart")

    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))

    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        CartService.add_product(request, product, quantity)
    except ValueError as e:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": str(e)}, status=400)
        messages.error(request, str(e))
        return redirect(request.META.get("HTTP_REFERER", "cart"))

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        cart = CartService.get_cart(request)
        return JsonResponse({
            "ok": True,
            "items_count": cart.items_count,
            "total_price": str(cart.total_price),
        })

    return redirect(request.META.get("HTTP_REFERER", "cart"))

def cart_update_view(request):
    if request.method != "POST":
        return redirect("cart")

    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))

    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        CartService.update_product_quantity(request, product, quantity)
    except ValueError as e:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": str(e)}, status=400)
        messages.error(request, str(e))
        return redirect("cart")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        cart = CartService.get_cart(request)
        return JsonResponse({
            "ok": True,
            "items_count": cart.items_count,
            "total_price": str(cart.total_price),
        })

    return redirect("cart")

def cart_remove_view(request):
    if request.method != "POST":
        return redirect("cart")

    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id)

    CartService.remove_product(request, product)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        cart = CartService.get_cart(request)
        return JsonResponse({
            "ok": True,
            "items_count": cart.items_count,
            "total_price": str(cart.total_price),
        })

    return redirect("cart")
