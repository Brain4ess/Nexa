# Nexa

Nexa is a backend for a PC hardware online store built with Django and PostgreSQL.



# Requirements

* Python 3.14+
* PostgreSQL



# Setup

## 1. Clone the repository

```
git clone https://github.com/<your-username>/Nexa.git
cd Nexa
```


## 2. Install dependencies


```
pip install django psycopg[binary] python-dotenv
```

---

# Database Setup

The project uses PostgreSQL.

## 1. Create the database

Windows example:

```
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres
```

Create the database and user:

```
CREATE DATABASE nexa;

CREATE USER nexa_user WITH PASSWORD 'password';

ALTER ROLE nexa_user SET client_encoding TO 'utf8';
ALTER ROLE nexa_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE nexa_user SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE nexa TO nexa_user;
```

Connect to the database and grant schema permissions:

```
\c nexa

GRANT ALL ON SCHEMA public TO nexa_user;
ALTER SCHEMA public OWNER TO nexa_user;

\q
```

---

# Environment Variables

Create a `.env` file in the project root:

```
DJANGO_SECRET_KEY=your_secret_key
POSTGRES_DB_KEY=your_password
```

`POSTGRES_DB_KEY` must match the password used when creating `nexa_user`.

---

# Run Migrations

```
python manage.py migrate
```

---

# Create a Superuser

```
python manage.py createsuperuser
```

---

# Run the Development Server

```
python manage.py runserver
```

The admin panel will be available at:

```
http://127.0.0.1:8000/admin
```
