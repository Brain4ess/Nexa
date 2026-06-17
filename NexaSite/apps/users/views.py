from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from apps.cart.services import CartService

User = get_user_model()

USERNAME_MAX_LENGTH = 30
EMAIL_MAX_LENGTH = 128
PASSWORD_MAX_LENGTH = 128
LOGIN_IDENTIFIER_MAX_LENGTH = 128

def _clean(value):
    return (value or "").strip()

def login_view(request):
    if request.method == "POST":
        identifier = _clean(request.POST.get("identifier"))
        password = request.POST.get("password") or ""

        context = {
            "identifier": identifier,
        }

        if not identifier:
            context["error"] = "Введите почту или имя пользователя"
            return render(request, "pages/login.html", context)

        if len(identifier) > LOGIN_IDENTIFIER_MAX_LENGTH:
            context["error"] = f"Имя пользователя не должно превышать {LOGIN_IDENTIFIER_MAX_LENGTH} символов"
            return render(request, "pages/login.html", context)

        user = None

        if "@" not in identifier:
            user_obj = User.objects.filter(username__iexact=identifier).first()
            if user_obj:
                user = authenticate(request, username=user_obj.email, password=password)

        if user is None:
            user = authenticate(request, username=identifier, password=password)

        if user is not None:
            CartService.merge_guest_cart_to_user(request, user)
            login(request, user)
            return redirect("/")

        context["error"] = "Неверное имя пользователя или пароль"
        return render(request, "pages/login.html", context)

    return render(request, "pages/login.html")

def register_view(request):
    if request.method == "POST":
        username = _clean(request.POST.get("username"))
        email = _clean(request.POST.get("email"))
        password = request.POST.get("password") or ""
        password2 = request.POST.get("password2") or ""

        context = {
            "username": username,
            "email": email,
        }

        if not username or len(username) < 3:
            context["error"] = "Имя пользователя должно быть не менее 3 символов"
            return render(request, "pages/register.html", context)

        if len(username) > USERNAME_MAX_LENGTH:
            context["error"] = f"Имя пользователя не должно превышать {USERNAME_MAX_LENGTH} символов"
            return render(request, "pages/register.html", context)

        if " " in username:
            context["error"] = "Имя пользователя не должно содержать пробелы"
            return render(request, "pages/register.html", context)

        if not email:
            context["error"] = "Введите почту"
            return render(request, "pages/register.html", context)

        if len(email) > EMAIL_MAX_LENGTH:
            context["error"] = f"Почта не должна превышать {EMAIL_MAX_LENGTH} символов"
            return render(request, "pages/register.html", context)

        if User.objects.filter(username__iexact=username).exists():
            context["error"] = "Имя пользователя уже занято"
            return render(request, "pages/register.html", context)

        if User.objects.filter(email__iexact=email).exists():
            context["error"] = "Почта уже используется"
            return render(request, "pages/register.html", context)

        if password != password2:
            context["error"] = "Пароли не совпадают"
            return render(request, "pages/register.html", context)

        if len(password) < 8:
            context["error"] = "Пароль должен быть не менее 8 символов"
            return render(request, "pages/register.html", context)

        if len(password) > PASSWORD_MAX_LENGTH:
            context["error"] = f"Пароль не должен превышать {PASSWORD_MAX_LENGTH} символов"
            return render(request, "pages/register.html", context)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        CartService.merge_guest_cart_to_user(request, user)
        login(request, user)
        return redirect("/")

    return render(request, "pages/register.html")

def logout_view(request):
    logout(request)
    return redirect("/")

def account_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "change_password":
            current_password = request.POST.get("current_password")
            new_password1 = request.POST.get("new_password1")
            new_password2 = request.POST.get("new_password2")

            if not request.user.check_password(current_password):
                messages.error(request, "Неверный текущий пароль")
                return redirect("account")

            if new_password1 != new_password2:
                messages.error(request, "Новые пароли не совпадают")
                return redirect("account")

            if len(new_password1) < 8:
                messages.error(request, "Пароль должен быть не менее 8 символов")
                return redirect("account")

            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Пароль успешно изменён")
            return redirect("account")

        if action == "change_email":
            current_email = request.user.email
            new_email = request.POST.get("new_email")
            confirm_email = request.POST.get("confirm_email")

            if new_email != confirm_email:
                messages.error(request, "Почты не совпадают")
                return redirect("account")

            if new_email == current_email:
                messages.error(request, "Это уже ваша текущая почта")
                return redirect("account")

            if User.objects.filter(email=new_email).exists():
                messages.error(request, "Эта почта уже используется")
                return redirect("account")

            request.user.email = new_email
            request.user.save()
            messages.success(request, "Почта успешно изменена")
            return redirect("account")
    return render(request, "pages/account.html")
