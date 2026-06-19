from django.db.models import Case, When, Value, IntegerField


def approved_reviews_qs(product, user=None):
    qs = (
        product.reviews.filter(is_approved=True)
        .select_related("user")
        .prefetch_related("updates")
    )

    if user and user.is_authenticated:
        qs = qs.annotate(
            is_own=Case(
                When(user_id=user.id, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("is_own", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    return qs
