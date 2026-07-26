import pytest
from django.contrib.auth import get_user_model
from apps.cart.models import Cart, CartItem
from factories import UserFactory, ProductFactory, CartFactory, CartItemFactory


pytestmark = pytest.mark.django_db
User = get_user_model()


class TestLogin:
    def test_login_by_email(self, client):
        UserFactory(email="test@example.com", password="testpass123")

        response = client.post("/login/", {"identifier": "test@example.com", "password": "testpass123"}, follow=True)

        assert response.context["user"].is_authenticated

    def test_login_by_username(self, client):
        UserFactory(username="testuser", password="testpass123")

        response = client.post("/login/", {"identifier": "testuser", "password": "testpass123"}, follow=True)

        assert response.context["user"].is_authenticated

    def test_login_wrong_password(self, client):
        UserFactory(password="testpass123")

        response = client.post("/login/", {"identifier": "test@example.com", "password": "wrongpass"})

        assert response.status_code == 200

    def test_login_empty_identifier(self, client):
        response = client.post("/login/", {"identifier": "", "password": "testpass123"})

        assert response.status_code == 200

    def test_login_identifier_too_long(self, client):
        response = client.post("/login/", {"identifier": "x" * 129, "password": "testpass123"})

        assert response.status_code == 200

    def test_login_merges_guest_cart(self, client):
        user = UserFactory(email="login@test.com", password="testpass123")
        product = ProductFactory()

        session = client.session
        session.save()
        guest_cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=guest_cart, product=product, quantity=2)

        client.post("/login/", {"identifier": "login@test.com", "password": "testpass123"})

        assert CartItem.objects.filter(cart__user=user, product=product).exists()

    def test_login_get(self, client):
        response = client.get("/login/")

        assert response.status_code == 200
        assert "pages/login.html" in [t.name for t in response.templates]


class TestRegister:
    def test_register_success(self, client):
        response = client.post("/register/", {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Strongpass123!",
            "password2": "Strongpass123!",
        }, follow=True)

        assert response.context["user"].is_authenticated
        assert User.objects.filter(email="new@example.com").exists()

    def test_register_username_too_short(self, client):
        response = client.post("/register/", {
            "username": "ab",
            "email": "new@example.com",
            "password": "strongpass123",
            "password2": "strongpass123",
        })

        assert response.status_code == 200

    def test_register_username_has_spaces(self, client):
        response = client.post("/register/", {
            "username": "new user",
            "email": "new@example.com",
            "password": "Strongpass123!",
            "password2": "Strongpass123!",
        }, follow=True)

        assert response.context["user"].is_authenticated
        assert User.objects.filter(username="new user").exists()

    def test_register_passwords_mismatch(self, client):
        response = client.post("/register/", {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpass123",
            "password2": "differentpass",
        })

        assert response.status_code == 200

    def test_register_password_too_short(self, client):
        response = client.post("/register/", {
            "username": "newuser",
            "email": "new@example.com",
            "password": "short",
            "password2": "short",
        })

        assert response.status_code == 200

    def test_register_duplicate_username(self, client):
        UserFactory(username="existing")
        response = client.post("/register/", {
            "username": "existing",
            "email": "new@example.com",
            "password": "strongpass123",
            "password2": "strongpass123",
        })

        assert response.status_code == 200

    def test_register_duplicate_email(self, client):
        UserFactory(email="dup@example.com")
        response = client.post("/register/", {
            "username": "newuser",
            "email": "dup@example.com",
            "password": "strongpass123",
            "password2": "strongpass123",
        })

        assert response.status_code == 200

    def test_register_merges_guest_cart(self, client):
        product = ProductFactory()

        session = client.session
        session.save()
        guest_cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=guest_cart, product=product)

        response = client.post("/register/", {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Strongpass123!",
            "password2": "Strongpass123!",
        }, follow=True)

        assert User.objects.filter(email="new@example.com").exists()
        user = User.objects.get(email="new@example.com")
        assert CartItem.objects.filter(cart__user=user, product=product).exists()

    def test_register_get(self, client):
        response = client.get("/register/")

        assert response.status_code == 200
        assert "pages/register.html" in [t.name for t in response.templates]


class TestLogout:
    def test_logout(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get("/logout/", follow=True)

        assert not response.context["user"].is_authenticated


class TestAccount:
    def test_account_requires_login(self, client):
        response = client.get("/account/")

        assert response.status_code == 302

    def test_account_page(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get("/account/")

        assert response.status_code == 200
        assert "pages/account.html" in [t.name for t in response.templates]

    def test_change_password_success(self, client):
        user = UserFactory(password="oldpass123")
        client.force_login(user)

        response = client.post("/account/", {
            "action": "change_password",
            "current_password": "oldpass123",
            "new_password1": "Newpass456!",
            "new_password2": "Newpass456!",
        }, follow=True)

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("Newpass456!")

    def test_change_password_wrong_current(self, client):
        user = UserFactory(password="oldpass123")
        client.force_login(user)

        response = client.post("/account/", {
            "action": "change_password",
            "current_password": "wrongpass",
            "new_password1": "newpass456",
            "new_password2": "newpass456",
        }, follow=True)

        assert response.status_code == 200

    def test_change_password_mismatch(self, client):
        user = UserFactory(password="oldpass123")
        client.force_login(user)

        response = client.post("/account/", {
            "action": "change_password",
            "current_password": "oldpass123",
            "new_password1": "newpass456",
            "new_password2": "different456",
        }, follow=True)

        assert response.status_code == 200

    def test_change_email_success(self, client):
        user = UserFactory(email="old@example.com", password="testpass123")
        client.force_login(user)

        response = client.post("/account/", {
            "action": "change_email",
            "current_email": "old@example.com",
            "new_email": "new@example.com",
            "confirm_email": "new@example.com",
        }, follow=True)

        user.refresh_from_db()
        assert user.email == "new@example.com"

    def test_change_email_wrong_current(self, client):
        user = UserFactory(email="old@example.com")
        client.force_login(user)

        response = client.post("/account/", {
            "action": "change_email",
            "current_email": "wrong@example.com",
            "new_email": "new@example.com",
            "confirm_email": "new@example.com",
        }, follow=True)

        assert response.status_code == 200

    def test_change_email_already_used(self, client):
        UserFactory(email="taken@example.com")
        user = UserFactory(email="old@example.com")
        client.force_login(user)

        response = client.post("/account/", {
            "action": "change_email",
            "current_email": "old@example.com",
            "new_email": "taken@example.com",
            "confirm_email": "taken@example.com",
        }, follow=True)

        assert response.status_code == 200

    def test_change_email_same_as_current(self, client):
        user = UserFactory(email="same@example.com")
        client.force_login(user)

        response = client.post("/account/", {
            "action": "change_email",
            "current_email": "same@example.com",
            "new_email": "same@example.com",
            "confirm_email": "same@example.com",
        }, follow=True)

        assert response.status_code == 200
