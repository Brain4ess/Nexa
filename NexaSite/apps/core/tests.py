import pytest
from apps.categories.models import Category


pytestmark = pytest.mark.django_db


class TestSlugMixin:
    def test_slug_generated_from_name(self):
        category = Category.objects.create(name="Test Category")

        assert category.slug == "test-category"

    def test_slug_unique_on_duplicate_name(self):
        cat1 = Category.objects.create(name="My Category")
        cat2 = Category.objects.create(name="My Category")

        assert cat1.slug != cat2.slug
        assert cat1.slug == "my-category"
        assert cat2.slug == "my-category-1"

    def test_slug_multiple_duplicates(self):
        cats = [Category.objects.create(name="My Category") for _ in range(3)]

        assert cats[0].slug == "my-category"
        assert cats[1].slug == "my-category-1"
        assert cats[2].slug == "my-category-2"

    def test_existing_slug_not_overwritten(self):
        category = Category.objects.create(name="Test")
        original_slug = category.slug
        category.name = "Updated"
        category.save()

        assert category.slug == original_slug

    def test_slug_queried(self):
        Category.objects.create(name="Query Test")

        assert Category.objects.filter(slug="query-test").exists()


class TestTimestampMixin:
    def test_timestamps_set_on_create(self):
        category = Category.objects.create(name="Timed")

        assert category.created_at is not None
        assert category.updated_at is not None

    def test_updated_at_changes_on_save(self):
        category = Category.objects.create(name="Timed")
        original_updated = category.updated_at
        category.name = "Updated Timed"
        category.save()

        assert category.updated_at > original_updated


class TestCoreViews:
    def test_index_page(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert "pages/index.html" in [t.name for t in response.templates]

    def test_about_page(self, client):
        response = client.get("/about")

        assert response.status_code == 200
        assert "pages/about.html" in [t.name for t in response.templates]

    def test_404_handler(self, client):
        response = client.get("/nonexistent-page/")

        assert response.status_code == 404
        assert "404.html" in [t.name for t in response.templates]
