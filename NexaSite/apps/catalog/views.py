from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, Q
from apps.categories.models import Category
from apps.catalog.models import Product
from apps.reviews.models import Review

def get_page_numbers(paginator, current_page_number, window_size=3):
    total_pages = paginator.num_pages

    if total_pages <= window_size:
        return list(range(1, total_pages + 1))

    half_window = window_size // 2
    start = current_page_number - half_window
    end = start + window_size - 1

    if start < 1:
        start = 1
        end = window_size

    if end > total_pages:
        end = total_pages
        start = total_pages - window_size + 1

    return list(range(start, end + 1))

def catalog_view(request, slug=None):
    categories = Category.objects.all()
    current_category = None
    products = []
    page_obj = None
    page_numbers = []

    if slug:
        current_category = get_object_or_404(Category, slug=slug)

        products_qs = Product.objects.filter(
            category=current_category,
            is_active=True
        ).prefetch_related("images").annotate(
            reviews_avg=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
            reviews_total=Count("reviews", filter=Q(reviews__is_approved=True)),
        )

        paginator = Paginator(products_qs, 10)
        page_obj = paginator.get_page(request.GET.get("page"))
        products = page_obj.object_list
        page_numbers = get_page_numbers(paginator, page_obj.number)

        for product in products:
            product.main_image = next(
                (img for img in product.images.all() if img.is_main),
                product.images.first()
            )

    return render(request, "pages/catalog.html", {
        "categories": categories,
        "products": products,
        "current_category": current_category,
        "page_obj": page_obj,
        "page_numbers": page_numbers,
    })

def product_view(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug
    )

    reviews_qs = product.reviews.filter(is_approved=True).select_related("user").order_by("-created_at")
    reviews = list(reviews_qs[:5])
    reviews_count = reviews_qs.count()

    context = {
        "product": product,
        "reviews": reviews,
        "reviews_count": reviews_count,
        "has_more_reviews": reviews_count > 5,
        "review_usage_choices": Review.UsagePeriod.choices,
    }

    return render(request, "pages/product.html", context)
