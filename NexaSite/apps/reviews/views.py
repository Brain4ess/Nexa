from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from apps.catalog.models import Product
from .models import Review, ReviewUpdate

def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

def _approved_reviews_qs(product):
    return (
        product.reviews.filter(is_approved=True)
        .select_related("user")
        .prefetch_related("updates")
        .order_by("-created_at")
    )

def _render_review_card(request, review):
    review = (
        Review.objects.select_related("user", "product")
        .prefetch_related("updates")
        .get(pk=review.pk)
    )
    return render_to_string(
        "components/review_item.html",
        {"review": review},
        request=request,
    )

@require_GET
def reviews_more_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    try:
        offset = max(int(request.GET.get("offset", 0)), 0)
    except ValueError:
        offset = 0

    limit = 5
    reviews_qs = _approved_reviews_qs(product)
    total = reviews_qs.count()
    reviews = list(reviews_qs[offset:offset + limit])

    html = render_to_string(
        "components/review_items.html",
        {"reviews": reviews},
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

    if Review.objects.filter(user=request.user, product=product).exists():
        if _is_ajax(request):
            return JsonResponse(
                {"ok": False, "errors": {"non_field": "Вы уже оставляли отзыв на этот товар"}},
                status=400
            )

        messages.error(request, "Вы уже оставляли отзыв на этот товар")
        return redirect("product", slug=slug)

    errors = {}

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
    elif len(text.splitlines()) > 15:
        errors["text"] = "Текст отзыва не должен превышать 15 строк"

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

    review_html = _render_review_card(request, review)

    if _is_ajax(request):
        return JsonResponse({
            "ok": True,
            "review_html": review_html,
            "average_rating": f"{product.average_rating:.1f}",
            "reviews_count": _approved_reviews_qs(product).count(),
        })

    messages.success(request, "Отзыв опубликован")
    return redirect("product", slug=slug)

@login_required
@require_POST
def review_update_view(request, slug, review_id):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    review = get_object_or_404(Review, pk=review_id, product=product, user=request.user, is_approved=True)

    text = (request.POST.get("text") or "").strip()

    errors = {}

    if not text:
        errors["text"] = "Введите текст дополнения"
    elif len(text) > 3000:
        errors["text"] = "Текст дополнения не должен превышать 3000 символов"

    if review.updates.count() >= 5:
        errors["limit"] = "Достигнут лимит дополнений"

    last_update = review.updates.order_by("-created_at").first()
    if last_update and timezone.now() - last_update.created_at < timedelta(days=3):
        errors["cooldown"] = "Дополнение можно добавить не чаще одного раза в 3 дня"

    if errors:
        if _is_ajax(request):
            return JsonResponse({"ok": False, "errors": errors}, status=400)

        for message in errors.values():
            messages.error(request, message)

        return redirect("product", slug=slug)

    ReviewUpdate.objects.create(
        review=review,
        user=request.user,
        text=text,
    )

    review_html = _render_review_card(request, review)

    if _is_ajax(request):
        return JsonResponse({
            "ok": True,
            "review_html": review_html,
        })

    messages.success(request, "Дополнение добавлено")
    return redirect("product", slug=slug)

@login_required
@require_POST
def review_delete_view(request, slug, review_id):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    review = get_object_or_404(Review, pk=review_id, product=product, user=request.user, is_approved=True)

    review.delete()

    if _is_ajax(request):
        reviews_count = _approved_reviews_qs(product).count()
        return JsonResponse({
            "ok": True,
            "average_rating": f"{product.average_rating:.1f}",
            "reviews_count": reviews_count,
        })

    messages.success(request, "Отзыв удален")
    return redirect("product", slug=slug)
