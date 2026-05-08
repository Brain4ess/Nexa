from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from apps.catalog.models import Product
from .models import Review

def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

@require_GET
def reviews_more_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    try:
        offset = max(int(request.GET.get("offset", 0)), 0)
    except ValueError:
        offset = 0

    limit = 5
    reviews_qs = product.reviews.filter(is_approved=True).select_related("user").order_by("-created_at")
    total = reviews_qs.count()
    reviews = list(reviews_qs[offset:offset + limit])

    html = render_to_string(
        "components/review_items.html",
        {
            "reviews": reviews,
        },
        request=request,
    )

    return JsonResponse({
        "ok": True,
        "html": html,
        "has_more": offset + limit < total,
        "next_offset": offset + len(reviews),
    })

@login_required
@require_POST
def review_create_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    title = (request.POST.get("title") or "").strip()
    text = (request.POST.get("text") or "").strip()
    usage_period = (request.POST.get("usage_period") or "").strip()

    try:
        rating = int(request.POST.get("rating", 0))
    except ValueError:
        rating = 0

    errors = {}

    if Review.objects.filter(user=request.user, product=product).exists():
        errors["non_field"] = "Вы уже оставляли отзыв на этот товар"

    if not (1 <= rating <= 5):
        errors["rating"] = "Выберите оценку от 1 до 5"

    if not title:
        errors["title"] = "Введите заголовок отзыва"
    elif len(title) > 50:
        errors["title"] = "Заголовок не должен превышать 50 символов"

    if not text:
        errors["text"] = "Введите текст отзыва"
    elif len(text) > 3000:
        errors["text"] = "Текст отзыва не должен превышать 3000 символов"

    if usage_period not in dict(Review.UsagePeriod.choices):
        errors["usage_period"] = "Выберите срок использования"

    if errors:
        if _is_ajax(request):
            return JsonResponse({"ok": False, "errors": errors}, status=400)

        for message in errors.values():
            messages.error(request, message)

        return redirect("product", slug=slug)

    review = Review.objects.create(
        user=request.user,
        product=product,
        rating=rating,
        title=title,
        text=text,
        usage_period=usage_period,
        is_approved=True,
    )

    review_html = render_to_string(
        "components/review_item.html",
        {
            "review": review,
        },
        request=request,
    )

    if _is_ajax(request):
        return JsonResponse({
            "ok": True,
            "review_html": review_html,
            "average_rating": f"{product.average_rating:.1f}",
            "reviews_count": product.reviews_count,
        })

    messages.success(request, "Отзыв опубликован")
    return redirect("product", slug=slug)
