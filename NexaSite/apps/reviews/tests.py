import pytest
from django.utils import timezone
from datetime import timedelta
from apps.reviews.models import Review, ReviewUpdate
from apps.reviews.selectors import approved_reviews_qs
from factories import UserFactory, ProductFactory, ReviewFactory


pytestmark = pytest.mark.django_db


class TestReviewsMoreView:
    def test_load_more_reviews(self, client):
        product = ProductFactory()
        ReviewFactory.create_batch(7, product=product)
        response = client.get(f"/reviews/product/{product.slug}/more/?offset=0")

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["has_more"] is True
        assert data["next_offset"] == 5

    def test_load_more_last_page(self, client):
        product = ProductFactory()
        ReviewFactory.create_batch(3, product=product)
        response = client.get(f"/reviews/product/{product.slug}/more/?offset=0")

        data = response.json()
        assert data["has_more"] is False

    def test_load_more_nonexistent_product(self, client):
        response = client.get("/reviews/product/nonexistent/more/?offset=0")

        assert response.status_code == 404

    def test_load_more_negative_offset(self, client):
        product = ProductFactory()
        ReviewFactory.create_batch(5, product=product)
        response = client.get(f"/reviews/product/{product.slug}/more/?offset=-1")

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestReviewCreateView:
    def test_requires_login(self, client):
        product = ProductFactory()
        response = client.post(f"/reviews/product/{product.slug}/create/")

        assert response.status_code == 302

    def test_create_review_success(self, client):
        user = UserFactory()
        product = ProductFactory()
        client.force_login(user)
        response = client.post(f"/reviews/product/{product.slug}/create/", {
            "rating": 5,
            "title": "Great!",
            "text": "Amazing product!",
            "usage_period": "more_month",
        })

        assert response.status_code == 302
        assert Review.objects.filter(user=user, product=product).exists()

    def test_create_review_ajax(self, client):
        user = UserFactory()
        product = ProductFactory()
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"rating": 5, "title": "Great!", "text": "Amazing!", "usage_period": "more_month"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "review_html" in data

    def test_create_review_duplicate(self, client):
        user = UserFactory()
        product = ProductFactory()
        ReviewFactory(user=user, product=product)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"rating": 5, "title": "Another", "text": "Review", "usage_period": "more_month"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert response.json()["ok"] is False

    def test_create_review_missing_rating(self, client):
        user = UserFactory()
        product = ProductFactory()
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"title": "Review", "text": "Text", "usage_period": "more_month"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "rating" in response.json()["errors"]

    def test_create_review_title_too_long(self, client):
        user = UserFactory()
        product = ProductFactory()
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"rating": 5, "title": "x" * 51, "text": "Text", "usage_period": "more_month"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "title" in response.json()["errors"]

    def test_create_review_text_too_long(self, client):
        user = UserFactory()
        product = ProductFactory()
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"rating": 5, "title": "Title", "text": "x" * 3001, "usage_period": "more_month"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "text" in response.json()["errors"]

    def test_create_review_text_too_many_lines(self, client):
        user = UserFactory()
        product = ProductFactory()
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"rating": 5, "title": "Title", "text": "x\n" * 16, "usage_period": "more_month"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "text" in response.json()["errors"]

    def test_create_review_invalid_usage_period(self, client):
        user = UserFactory()
        product = ProductFactory()
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"rating": 5, "title": "Title", "text": "Text", "usage_period": "invalid"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "usage_period" in response.json()["errors"]

    def test_create_review_returns_average_rating(self, client):
        user = UserFactory()
        product = ProductFactory()
        ReviewFactory(product=product, rating=4)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/create/",
            {"rating": 5, "title": "Great!", "text": "Amazing!", "usage_period": "more_month"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        data = response.json()
        assert data["average_rating"] == "4.5"
        assert data["reviews_count"] == 2


class TestReviewUpdateView:
    def test_requires_login(self, client):
        product = ProductFactory()
        review = ReviewFactory(product=product)
        response = client.post(f"/reviews/product/{product.slug}/{review.id}/update/")

        assert response.status_code == 302

    def test_update_own_review(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": "Update text"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert ReviewUpdate.objects.filter(review=review, user=user).exists()

    def test_update_not_own_review(self, client):
        user = UserFactory()
        other = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=other, product=product)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": "Update text"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 404

    def test_update_empty_text(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "text" in response.json()["errors"]

    def test_update_text_too_long(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": "x" * 1001},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "text" in response.json()["errors"]

    def test_update_too_many_lines(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": "x\n" * 11},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "text" in response.json()["errors"]

    def test_update_limit_5_updates(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        for _ in range(5):
            ReviewUpdate.objects.create(review=review, user=user, text="Update text")
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": "Another update"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "limit" in response.json()["errors"]

    def test_update_cooldown_3_days(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        ReviewUpdate.objects.create(review=review, user=user, text="First update")
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": "Second update"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 400
        assert "cooldown" in response.json()["errors"]

    def test_update_after_cooldown(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        update = ReviewUpdate.objects.create(review=review, user=user, text="Old update")
        ReviewUpdate.objects.filter(pk=update.pk).update(
            created_at=timezone.now() - timedelta(days=4)
        )
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/update/",
            {"text": "New update"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        assert response.json()["ok"] is True


class TestReviewDeleteView:
    def test_requires_login(self, client):
        product = ProductFactory()
        review = ReviewFactory(product=product)
        response = client.post(f"/reviews/product/{product.slug}/{review.id}/delete/")

        assert response.status_code == 302

    def test_delete_own_review(self, client):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/delete/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert not Review.objects.filter(pk=review.pk).exists()

    def test_delete_not_own_review(self, client):
        user = UserFactory()
        other = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=other, product=product)
        client.force_login(user)
        response = client.post(f"/reviews/product/{product.slug}/{review.id}/delete/")

        assert response.status_code == 404

    def test_delete_returns_updated_rating(self, client):
        user = UserFactory()
        product = ProductFactory()
        ReviewFactory(product=product, rating=4)
        review = ReviewFactory(user=user, product=product, rating=5)
        client.force_login(user)
        response = client.post(
            f"/reviews/product/{product.slug}/{review.id}/delete/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        data = response.json()
        assert data["average_rating"] == "4.0"
        assert data["reviews_count"] == 1


class TestReviewSelectors:
    def test_approved_reviews_only(self):
        product = ProductFactory()
        ReviewFactory(product=product, is_approved=True)
        ReviewFactory(product=product, is_approved=False)

        qs = approved_reviews_qs(product)

        assert qs.count() == 1

    def test_own_review_first(self):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(product=product, user=user, is_approved=True)

        qs = approved_reviews_qs(product, user=user)

        assert qs.first().pk == review.pk

    def test_order_by_date(self):
        product = ProductFactory()
        ReviewFactory(product=product, is_approved=True)

        qs = approved_reviews_qs(product)

        assert qs.count() == 1


class TestReviewModel:
    def test_updates_count(self):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        ReviewUpdate.objects.create(review=review, user=user, text="Update 1")
        ReviewUpdate.objects.create(review=review, user=user, text="Update 2")

        assert review.updates_count == 2

    def test_can_add_update_initial(self):
        review = ReviewFactory()

        assert review.can_add_update is True

    def test_can_add_update_after_5(self):
        user = UserFactory()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product)
        for _ in range(5):
            ReviewUpdate.objects.create(review=review, user=user, text="Update")

        assert review.can_add_update is False

    def test_can_add_update_cooldown(self):
        review = ReviewFactory()
        update = ReviewUpdate.objects.create(review=review, user=UserFactory(), text="Recent")
        ReviewUpdate.objects.filter(pk=update.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        assert review.can_add_update is False

    def test_can_add_update_after_cooldown(self):
        review = ReviewFactory()
        update = ReviewUpdate.objects.create(review=review, user=UserFactory(), text="Old")
        ReviewUpdate.objects.filter(pk=update.pk).update(
            created_at=timezone.now() - timedelta(days=4)
        )

        assert review.can_add_update is True

    def test_next_update_available_at(self):
        review = ReviewFactory()
        update = ReviewUpdate.objects.create(review=review, user=UserFactory(), text="Update")

        expected = update.created_at + timedelta(days=3)
        assert review.next_update_available_at is not None
        assert abs(review.next_update_available_at - expected) < timedelta(seconds=1)
