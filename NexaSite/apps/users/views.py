from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Неверный логин или пароль")
            return redirect("login")

    return render(request, "pages/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        context = {
            "username": username,
            "email": email
        }

        if not username or len(username) < 3:
            context["error"] = "Имя пользователя должно быть не менее 3 символов"
            return render(request, "pages/register.html", context)

        if " " in username:
            context["error"] = "Имя пользователя не должно содержать пробелы"
            return render(request, "pages/register.html", context)

        if User.objects.filter(username=username).exists():
            context["error"] = "Имя пользователя уже занято"
            return render(request, "pages/register.html", context)

        if User.objects.filter(email=email).exists():
            context["error"] = "Почта уже используется"
            return render(request, "pages/register.html", context)

        if password != password2:
            context["error"] = "Пароли не совпадают"
            return render(request, "pages/register.html", context)

        if len(password) < 8:
            context["error"] = "Пароль должен быть не менее 8 символов"
            return render(request, "pages/register.html", context)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("/")

    return render(request, "pages/register.html")


def logout_view(request):
    logout(request)
    return redirect("/")
