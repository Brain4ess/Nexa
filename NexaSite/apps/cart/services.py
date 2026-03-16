from decimal import Decimal
from django.db import transaction
from apps.cart.models import CartItem
from apps.orders.models import Order, OrderItem

class CheckoutService:
    @staticmethod
    @transaction.atomic
    def checkout(user, address):
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            raise ValueError("Cart is empty")

        total_price = Decimal(0)

        # Making the order
        order = Order.objects.create(
            user=user,
            address=address
        )

        for item in cart_items:
            product = item.product

            if item.quantity > product.stock:
                raise ValueError(f"Not enough stock for {product.name}")

            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=item.quantity
            )

            # Decreasing item stock
            product.stock -= item.quantity
            product.save()

            total_price += product.price * item.quantity

        # Updating order total price
        order.total_price = total_price
        order.save()

        # Clearing cart
        cart_items.delete()

        return order
