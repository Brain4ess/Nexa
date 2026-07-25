import factory
from django.conf import settings
from apps.categories.models import Category
from apps.catalog.models import Product, ProductImage, AttributeGroup, Attribute, ProductAttribute
from apps.cart.models import Cart, CartItem
from apps.reviews.models import Review, ReviewUpdate
from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "testpass123")
        instance = super()._create(model_class, *args, **kwargs)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class AttributeGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AttributeGroup

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Group {n}")


class AttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attribute

    group = factory.SubFactory(AttributeGroupFactory)
    name = factory.Sequence(lambda n: f"Attribute {n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    price = 1000.00
    stock = 10
    category = factory.SubFactory(CategoryFactory)
    is_active = True


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(filename="test.png")
    is_main = False


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
    session_key = None


class GuestCartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    session_key = factory.Sequence(lambda n: f"session_key_{n}")
    user = None


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    rating = 5
    title = factory.Sequence(lambda n: f"Review {n}")
    text = factory.Sequence(lambda n: f"Great product {n}!")
    usage_period = Review.UsagePeriod.MORE_THAN_MONTH
    is_approved = True
