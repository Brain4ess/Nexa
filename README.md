<h1 align="center">Nexa</h1>

<p align="center">
  <strong>Minimal ecommerce platform for PC hardware built with Django and PostgreSQL.</strong>
</p>

<p align="center">
  <em>English</em> | <a href="README_ru.md">Русский</a>
</p>

---

## English

Nexa is a responsive ecommerce project for PC hardware. It uses Django, PostgreSQL, Django templates, CSS, and vanilla JavaScript.

### Stack

- Backend: Django
- Database: PostgreSQL
- Frontend: Django templates, CSS, vanilla JS
- Auth: Django session authentication

### Project structure

- `core` - shared project logic, settings, static files, custom 404
- `users` - login, register, logout
- `categories` - category tree and category images
- `catalog` - products, product images, attribute groups, attributes, product attributes
- `cart` - cart service, cart items, cart views, AJAX actions
- `orders` - order flow
- `reviews` - product reviews

### Requirements

- Python 3.14+
- PostgreSQL

### Environment variables

Create a `.env` file in the project root:

```
DJANGO_SECRET_KEY=your_secret_key
POSTGRES_DB_KEY=your_database_key
```

`POSTGRES_DB_KEY` must match the password used for `nexa_user`.

### Setup

#### 1. Install dependencies

```
pip install -r requirements.txt
```

or, if you use `uv`:

```
uv sync
```

#### 2. Create the PostgreSQL database

Windows example:

```
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres
```

Then create the database and user, grant permissions, and exit:

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

#### 3. Run migrations

```
py manage.py migrate
```

#### 4. Create a superuser

```
py manage.py createsuperuser
```

### Run the project

#### Development mode

The project is configured to run with `DEBUG=True` during development.

```
py manage.py runserver
```

Admin panel:

```
http://127.0.0.1:8000/admin/
```

#### Production mode

For production, set `DEBUG=False`, configure `ALLOWED_HOSTS`, and collect static files before starting the server.

1. Set `DEBUG=False`.
2. Configure `ALLOWED_HOSTS`.
3. Run:

```
py manage.py collectstatic
```

4. Start the project with a production WSGI or ASGI server.

WhiteNoise is required for serving static files in this mode.
