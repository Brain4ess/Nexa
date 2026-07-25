import pytest
from decimal import Decimal
from django.contrib.sessions.backends.db import SessionStore
from apps.cart.models import Cart, CartItem
from apps.cart.services import CartService
from apps.cart.context_processors import cart_count
from factories import UserFactory, ProductFactory, CartFactory, GuestCartFactory, CartItemFactory


pytestmark = pytest.mark.django_db


class TestCartServiceGetCart:
    def test_authenticated_user_creates_cart(self, rf, client):
        user = UserFactory()
        request = rf.get("/")
        request.user = user
        request.session = client.session

        cart = CartService.get_cart(request)

        assert cart.user == user
        assert cart.session_key is None

    def test_authenticated_user_returns_existing_cart(self, rf, client):
        user = UserFactory()
        cart = CartFactory(user=user)
        request = rf.get("/")
        request.user = user
        request.session = client.session

        result = CartService.get_cart(request)

        assert result.pk == cart.pk

    def test_anonymous_creates_session(self, rf, client):
        request = rf.get("/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})()
        session = client.session
        session.create()
        request.session = session

        cart = CartService.get_cart(request)

        assert cart.session_key == session.session_key
        assert cart.user is None

    def test_anonymous_returns_existing_session_cart(self, rf, client):
        request = rf.get("/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})()
        session = client.session
        session.create()
        request.session = session
        cart = GuestCartFactory(session_key=session.session_key)

        result = CartService.get_cart(request)

        assert result.pk == cart.pk

    def test_anonymous_creates_session_if_missing(self, rf, client):
        request = rf.get("/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})()
        request.session = SessionStore()

        cart = CartService.get_cart(request)

        assert request.session.session_key is not None
        assert cart.session_key == request.session.session_key

    def test_authenticated_merges_guest_cart(self, rf, client):
        user = UserFactory()
        request = rf.get("/")
        request.user = user
        session = client.session
        session.create()
        session["cart_merged"] = None
        request.session = session
        product = ProductFactory()
        guest_cart = GuestCartFactory(session_key=session.session_key)
        CartItemFactory(cart=guest_cart, product=product, quantity=2)

        cart = CartService.get_cart(request)

        assert cart.user == user
        assert CartItem.objects.filter(cart=cart, product=product).exists()
        assert session.get("cart_merged") is True


class TestCartServiceMerge:
    def test_merge_guest_to_user_combines_items(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        session = client.session
        session.create()
        session.save()
        request = rf.get("/")
        request.session = session
        guest_cart = GuestCartFactory(session_key=session.session_key)
        CartItemFactory(cart=guest_cart, product=product, quantity=3)

        result = CartService.merge_guest_cart_to_user(request, user)

        assert result.user == user
        item = CartItem.objects.get(cart=result, product=product)
        assert item.quantity == 3

    def test_merge_guest_to_user_sums_duplicates(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        session = client.session
        session.create()
        session.save()
        request = rf.get("/")
        request.session = session
        guest_cart = GuestCartFactory(session_key=session.session_key)
        CartItemFactory(cart=guest_cart, product=product, quantity=2)
        user_cart = CartFactory(user=user)
        CartItemFactory(cart=user_cart, product=product, quantity=1)

        result = CartService.merge_guest_cart_to_user(request, user)

        item = CartItem.objects.get(cart=result, product=product)
        assert item.quantity == 3

    def test_merge_no_guest_cart(self, rf, client):
        user = UserFactory()
        session = client.session
        session.create()
        request = rf.get("/")
        request.session = session

        result = CartService.merge_guest_cart_to_user(request, user)

        assert result.user == user
        assert Cart.objects.filter(user=user).exists()

    def test_merge_same_cart_no_op(self, rf, client):
        user = UserFactory()
        cart = CartFactory(user=user, session_key="key")
        session = client.session
        session.create()
        request = rf.get("/")
        request.session = session

        result = CartService.merge_guest_cart_to_user(request, user)

        assert result.pk == cart.pk

    def test_merge_no_session_key(self, rf):
        user = UserFactory()
        request = rf.get("/")
        request.session = SessionStore()

        result = CartService.merge_guest_cart_to_user(request, user)

        assert result.user == user

    def test_merge_guest_cart_deleted(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        session = client.session
        session.create()
        session.save()
        request = rf.get("/")
        request.session = session
        guest_cart = GuestCartFactory(session_key=session.session_key)
        CartItemFactory(cart=guest_cart, product=product)
        CartFactory(user=user)

        CartService.merge_guest_cart_to_user(request, user)

        assert not Cart.objects.filter(pk=guest_cart.pk).exists()


class TestCartServiceAdd:
    def test_add_new_product(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        request = rf.post("/")
        request.user = user
        request.session = client.session

        cart = CartService.add_product(request, product, quantity=2)

        item = CartItem.objects.get(cart=cart, product=product)
        assert item.quantity == 2

    def test_add_existing_increases_quantity(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=1)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        CartService.add_product(request, product, quantity=3)

        item = CartItem.objects.get(cart=cart, product=product)
        assert item.quantity == 4

    def test_add_quantity_too_low(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        request = rf.post("/")
        request.user = user
        request.session = client.session

        with pytest.raises(ValueError, match="greater than zero"):
            CartService.add_product(request, product, quantity=0)

    def test_add_exceeds_stock(self, rf, client):
        user = UserFactory()
        product = ProductFactory(stock=5)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        with pytest.raises(ValueError, match="Not enough stock"):
            CartService.add_product(request, product, quantity=10)

    def test_add_exceeds_stock_on_update(self, rf, client):
        user = UserFactory()
        product = ProductFactory(stock=5)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=3)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        with pytest.raises(ValueError, match="Not enough stock"):
            CartService.add_product(request, product, quantity=3)


class TestCartServiceUpdate:
    def test_update_quantity(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=1)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        CartService.update_product_quantity(request, product, quantity=5)

        item = CartItem.objects.get(cart=cart, product=product)
        assert item.quantity == 5

    def test_update_quantity_zero_deletes(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=1)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        cart = CartService.update_product_quantity(request, product, quantity=0)

        assert not CartItem.objects.filter(cart=cart, product=product).exists()

    def test_update_nonexistent_item(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        request = rf.post("/")
        request.user = user
        request.session = client.session

        with pytest.raises(ValueError, match="Cart item not found"):
            CartService.update_product_quantity(request, product, quantity=2)

    def test_update_exceeds_stock(self, rf, client):
        user = UserFactory()
        product = ProductFactory(stock=3)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=1)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        with pytest.raises(ValueError, match="Not enough stock"):
            CartService.update_product_quantity(request, product, quantity=10)


class TestCartServiceRemove:
    def test_remove_existing_item(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        CartService.remove_product(request, product)

        assert not CartItem.objects.filter(cart=cart, product=product).exists()

    def test_remove_nonexistent_no_error(self, rf, client):
        user = UserFactory()
        product = ProductFactory()
        CartFactory(user=user)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        CartService.remove_product(request, product)


class TestCartServiceClear:
    def test_clear_cart(self, rf, client):
        user = UserFactory()
        cart = CartFactory(user=user)
        CartItemFactory.create_batch(3, cart=cart)
        request = rf.post("/")
        request.user = user
        request.session = client.session

        CartService.clear_cart(request)

        assert cart.items.count() == 0


class TestCartViews:
    def test_cart_view_authenticated(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get("/cart/")

        assert response.status_code == 200
        assert "pages/cart.html" in [t.name for t in response.templates]

    def test_cart_view_with_items(self, client):
        user = UserFactory()
        cart = CartFactory(user=user)
        CartItemFactory.create_batch(2, cart=cart)
        client.force_login(user)
        response = client.get("/cart/")

        assert response.status_code == 200
        assert len(response.context["items"]) == 2

    def test_cart_add_view_get_redirects(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get("/cart/add/")

        assert response.status_code == 302

    def test_cart_add_view_success(self, client):
        user = UserFactory()
        product = ProductFactory(stock=10)
        client.force_login(user)
        response = client.post("/cart/add/", {"product_id": product.id, "quantity": 2})

        assert response.status_code == 302
        assert CartItem.objects.filter(cart__user=user, product=product).exists()

    def test_cart_add_view_ajax(self, client):
        user = UserFactory()
        product = ProductFactory(stock=10)
        client.force_login(user)
        response = client.post(
            "/cart/add/",
            {"product_id": product.id, "quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["items_count"] == 1
        assert data["total_price"] == "1000.00"

    def test_cart_add_view_out_of_stock_ajax(self, client):
        user = UserFactory()
        product = ProductFactory(stock=1)
        client.force_login(user)
        client.post("/cart/add/", {"product_id": product.id, "quantity": 1})
        response = client.post(
            "/cart/add/",
            {"product_id": product.id, "quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        data = response.json()
        assert data["ok"] is False

    def test_cart_update_view_ajax(self, client):
        user = UserFactory()
        product = ProductFactory(stock=10)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=2)
        client.force_login(user)
        response = client.post(
            "/cart/update/",
            {"product_id": product.id, "quantity": 5},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        item = CartItem.objects.get(cart=cart, product=product)
        assert item.quantity == 5

    def test_cart_remove_view_ajax(self, client):
        user = UserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product)
        client.force_login(user)
        response = client.post(
            "/cart/remove/",
            {"product_id": product.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert not CartItem.objects.filter(cart=cart, product=product).exists()

    def test_cart_count_context_processor_authenticated(self, rf, client):
        user = UserFactory()
        cart = CartFactory(user=user)
        CartItemFactory.create_batch(3, cart=cart)
        request = rf.get("/")
        request.user = user
        request.session = client.session

        result = cart_count(request)

        assert result["cart_count"] == 3

    def test_cart_count_context_processor_over_99(self, rf, client):
        user = UserFactory()
        cart = CartFactory(user=user)
        CartItemFactory.create_batch(100, cart=cart, quantity=1)
        request = rf.get("/")
        request.user = user
        request.session = client.session

        result = cart_count(request)

        assert result["cart_count"] == "99+"

    def test_cart_count_context_processor_anonymous(self, rf, client):
        request = rf.get("/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})()
        request.session = client.session

        result = cart_count(request)

        assert result["cart_count"] == 0

    def test_cart_models(self):
        user = UserFactory()
        product = ProductFactory(price=500.00)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=3)

        assert cart.items_count == 3
        assert cart.total_price == Decimal("1500.00")
        assert str(cart) == f"Cart of {user}"

        item = cart.items.first()
        assert item.total_price == Decimal("1500.00")
        assert str(item) == f"{product.name} x 3"
