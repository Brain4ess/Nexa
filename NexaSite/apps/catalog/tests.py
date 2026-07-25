import pytest
from django.core.paginator import Paginator
from apps.catalog.models import Product, AttributeGroup, Attribute
from apps.catalog.views import get_page_numbers
from factories import (
    ProductFactory, CategoryFactory,
    ReviewFactory, AttributeGroupFactory, AttributeFactory,
)


pytestmark = pytest.mark.django_db


class TestGetPageNumbers:
    def test_less_than_window(self):
        assert get_page_numbers(Paginator(list(range(3)), 1), 1, 5) == [1, 2, 3]

    def test_window_with_scroll(self):
        assert get_page_numbers(Paginator(list(range(20)), 1), 5, 3) == [4, 5, 6]

    def test_window_start(self):
        assert get_page_numbers(Paginator(list(range(10)), 1), 1, 3) == [1, 2, 3]

    def test_window_end(self):
        assert get_page_numbers(Paginator(list(range(10)), 1), 10, 3) == [8, 9, 10]


class TestCatalogView:
    def test_catalog_all_categories(self, client):
        CategoryFactory.create_batch(3)
        response = client.get("/catalog/")

        assert response.status_code == 200
        assert len(response.context["categories"]) == 3

    def test_catalog_by_category(self, client):
        category = CategoryFactory()
        ProductFactory.create_batch(5, category=category)
        response = client.get(f"/catalog/{category.slug}/")

        assert response.status_code == 200
        assert response.context["current_category"] == category
        assert len(response.context["products"]) == 5

    def test_catalog_empty_category(self, client):
        category = CategoryFactory()
        response = client.get(f"/catalog/{category.slug}/")

        assert response.status_code == 200
        assert len(response.context["products"]) == 0

    def test_catalog_nonexistent_category(self, client):
        response = client.get("/catalog/nonexistent/")

        assert response.status_code == 404

    def test_catalog_pagination(self, client):
        category = CategoryFactory()
        ProductFactory.create_batch(25, category=category)
        response = client.get(f"/catalog/{category.slug}/?page=2")

        assert response.status_code == 200
        assert len(response.context["products"]) == 10

    def test_catalog_inactive_product_hidden(self, client):
        category = CategoryFactory()
        ProductFactory(category=category, is_active=False)
        response = client.get(f"/catalog/{category.slug}/")

        assert len(response.context["products"]) == 0


class TestProductView:
    def test_product_detail(self, client):
        product = ProductFactory()
        response = client.get(f"/catalog/product/{product.slug}/")

        assert response.status_code == 200
        assert response.context["product"] == product

    def test_product_not_found(self, client):
        response = client.get("/catalog/product/nonexistent/")

        assert response.status_code == 404

    def test_product_reviews_displayed(self, client):
        product = ProductFactory()
        ReviewFactory.create_batch(3, product=product)
        response = client.get(f"/catalog/product/{product.slug}/")

        assert response.status_code == 200
        assert response.context["reviews_count"] == 3

    def test_product_reviews_not_approved_hidden(self, client):
        product = ProductFactory()
        ReviewFactory(product=product, is_approved=False)
        response = client.get(f"/catalog/product/{product.slug}/")

        assert response.context["reviews_count"] == 0

    def test_product_reviews_limit_5(self, client):
        product = ProductFactory()
        ReviewFactory.create_batch(7, product=product)
        response = client.get(f"/catalog/product/{product.slug}/")

        assert len(response.context["reviews"]) == 5
        assert response.context["has_more_reviews"] is True


class TestProductModel:
    def test_average_rating(self):
        product = ProductFactory()
        ReviewFactory.create_batch(2, product=product, rating=5)
        ReviewFactory.create_batch(1, product=product, rating=1)

        assert product.average_rating == 3.7

    def test_average_rating_no_reviews(self):
        product = ProductFactory()

        assert product.average_rating == 0

    def test_average_rating_inactive_reviews_excluded(self):
        product = ProductFactory()
        ReviewFactory(product=product, rating=5, is_approved=False)

        assert product.average_rating == 0

    def test_reviews_count_only_approved(self):
        product = ProductFactory()
        ReviewFactory(product=product, is_approved=True)
        ReviewFactory(product=product, is_approved=False)

        assert product.reviews_count == 1

    def test_save_creates_slug(self):
        product = Product.objects.create(
            name="Test Product", price=100, stock=5,
            category=CategoryFactory(),
        )

        assert product.slug == "test-product"

    def test_save_creates_unique_slug(self):
        cat = CategoryFactory()
        Product.objects.create(name="Test Product", price=100, stock=5, category=cat)
        product2 = Product.objects.create(name="Test Product", price=100, stock=5, category=cat)

        assert product2.slug == "test-product-1"

    def test_save_creates_attributes_from_category(self):
        category = CategoryFactory()
        attr_group = AttributeGroupFactory(category=category)
        AttributeFactory(group=attr_group)
        product = ProductFactory(category=category)

        assert product.attributes.count() == 1

    def test_inactive_product_detail_shows(self, client):
        product = ProductFactory(is_active=False)
        response = client.get(f"/catalog/product/{product.slug}/")

        assert response.status_code == 200


class TestAttributeGroupModel:
    def test_auto_slug(self):
        category = CategoryFactory()
        group = AttributeGroup.objects.create(category=category, name="Test Group")

        assert group.slug == "test-group"

    def test_unique_slug_per_category(self):
        category = CategoryFactory()
        AttributeGroup.objects.create(category=category, name="Size")
        group2 = AttributeGroup.objects.create(category=category, name="Size")

        assert group2.slug == "size-1"

    def test_slug_unique_across_categories(self):
        cat1 = CategoryFactory()
        cat2 = CategoryFactory()
        g1 = AttributeGroup.objects.create(category=cat1, name="Size")
        g2 = AttributeGroup.objects.create(category=cat2, name="Size")

        assert g1.slug == "size"
        assert g2.slug == "size"


class TestAttributeModel:
    def test_auto_slug(self):
        category = CategoryFactory()
        group = AttributeGroupFactory(category=category)
        attr = Attribute.objects.create(group=group, name="Color")

        assert attr.slug == "color"

    def test_unique_slug_per_group(self):
        category = CategoryFactory()
        group = AttributeGroupFactory(category=category)
        Attribute.objects.create(group=group, name="Red")
        attr2 = Attribute.objects.create(group=group, name="Red")

        assert attr2.slug == "red-1"
