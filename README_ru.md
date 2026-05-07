<h1 align="center">Nexa</h1>

<p align="center">
  <strong>Minimal ecommerce platform for PC hardware built with Django and PostgreSQL.</strong>
</p>

<p align="center">
  <a href="README.md">English</a> | <em>Русский</em>
</p>

---

## Русский

Nexa - это responsive ecommerce-проект для продажи PC hardware. Проект построен на Django и PostgreSQL, с использованием Django templates, CSS и vanilla JavaScript.

### Стек

- Backend: Django
- База данных: PostgreSQL
- Frontend: Django templates, CSS, vanilla JS
- Авторизация: Django session auth

### Структура проекта

- `core` - общая логика проекта, настройки, static files, кастомная 404
- `users` - вход, регистрация, выход
- `categories` - дерево категорий и изображения категорий
- `catalog` - товары, изображения товаров, группы атрибутов, атрибуты, атрибуты товаров
- `cart` - сервис корзины, элементы корзины, views и AJAX-действия
- `orders` - оформление заказов
- `reviews` - отзывы о товарах

### Требования

- Python 3.14+
- PostgreSQL

### Переменные окружения

Создайте `.env` в корне проекта:

```
DJANGO_SECRET_KEY=your_secret_key
POSTGRES_DB_KEY=your_database_key
```

`POSTGRES_DB_KEY` должен совпадать с паролем пользователя `nexa_user`.

### Установка

#### 1. Установить зависимости

```
pip install -r requirements.txt
```

или через `uv`:

```
uv sync
```

#### 2. Создать базу данных PostgreSQL

Пример для Windows:

```
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres
```

Дальше создайте базу и пользователя, затем выдайте права:

```
CREATE DATABASE nexa;
CREATE USER nexa_user WITH PASSWORD 'password';
ALTER ROLE nexa_user SET client_encoding TO 'utf8';
ALTER ROLE nexa_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE nexa_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nexa TO nexa_user;
\c nexa
GRANT ALL ON SCHEMA public TO nexa_user;
ALTER SCHEMA public OWNER TO nexa_user;
\q
```

#### 3. Выполнить миграции

```
py manage.py migrate
```

#### 4. Создать суперпользователя

```
py manage.py createsuperuser
```

### Запуск проекта

#### Режим разработки

Проект запускается с `DEBUG=True` в режиме разработки.

```
py manage.py runserver
```

Админ-панель:

```
http://127.0.0.1:8000/admin/
```

#### Production-режим

Для production нужно установить `DEBUG=False`, настроить `ALLOWED_HOSTS` и собрать статические файлы перед запуском сервера.

1. Установите `DEBUG=False`.
2. Настройте `ALLOWED_HOSTS`.
3. Выполните:

```
py manage.py collectstatic
```

4. Запустите проект через production WSGI или ASGI сервер.

Для этого режима нужен WhiteNoise для раздачи static files.