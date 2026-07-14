from django.shortcuts import render, get_object_or_404
from apps.categories.models import Category
from apps.catalog.models import Product

def index(request):
    return render(request, 'pages/index.html')

def about(request):
    return render(request, 'pages/about.html')

def catalog(request, slug=None):
    if slug:
        category = get_object_or_404(Category, slug=slug)

        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related("category").prefetch_related("images")

        return render(request, "pages/catalog.html", {
            "category": category,
            "products": products,
            "is_category_view": True
        })

    categories = Category.objects.filter(parent__isnull=True)

    return render(request, "pages/catalog.html", {
        "categories": categories,
        "is_category_view": False
    })

def custom_404(request, exception):
    return render(request, "404.html", status=404)
