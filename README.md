
---

# 📚 ketabgardoon

Ketabgardoon is a Django-based backend for a book social network where users can discover books and authors, rate books, write comments, create reading lists, track reading goals, and search across the platform. The API is built with Django REST Framework and includes features like JWT authentication, email verification, password reset, view counting, and Persian-language support.

---

# ✨ Features

## 👤 User Management

– Registration with email verification (6-digit code)
– JWT authentication (access + refresh tokens)
– Profile management (avatar, bio, public/private)
– Password change and password reset via email

---

## 📖 Books & Authors

– Browse, search, and filter books and authors
– Pagination, search by title/author/category, and custom sorting (by view count, rating, etc.)
– View counts tracked per visitor per day (using Django’s cache)

---

## ⭐ Ratings

– Users can rate books (0–5 stars)
– Aggregate rating stats (count, average) shown on book/author details
– Dedicated endpoints for current user’s ratings

---

## 💬 Comments

– Threaded comments on books (one level of replies)
– Like/unlike comments
– Rate limiting protection (planned)

---

## 📚 Lists

– Users can create custom lists (e.g., “Read”, “Favorites”, “Want to read”)
– Default lists created automatically on signup
– Add/remove books to/from lists
– Public/private visibility control

---

## 🎯 Reading Goal

– Set a yearly target for number of books to read
– Automatic progress tracking based on books added to the default “خوانده شده” list
– Progress percentage calculated automatically

---

## 🔎 Search

– Global search across books, authors, and users
– ISBN search (10/13 digits with optional hyphens)
– Category search returns all books in matching categories
– Persian-alphabet sorting using `pyuca` collator

---

## 📑 API Documentation

– Interactive Swagger UI and ReDoc endpoints

---

# 🧰 Tech Stack

* Python 3.10+
* Django 5.2
* Django REST Framework
* SQLite (default) / PostgreSQL (recommended for production)
* JWT Authentication (Simple JWT)
* Django Filter, CORS Headers
* drf-yasg for Swagger generation
* `pyuca` for Persian-alphabet sorting
* `jalali_date` for Jalali calendar support
* Local memory cache (configurable for Redis/Memcached)

---

# ⚙️ Prerequisites

* Python 3.10 or higher
* pip
* virtualenv (recommended)
* Git

---

# 🚀 Installation

## 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/ketabgardoon.git
cd ketabgardoon
```

---

## 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

---

## 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Apply migrations

```bash
python manage.py migrate
```

---

## 5️⃣ Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

---

## 6️⃣ Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```
http://127.0.0.1:8000/api/v1/
```

Admin interface:

```
http://127.0.0.1:8000/admin/
```

---

# 🔧 Configuration

Key settings are in `ketabgardoon/settings.py`.

For production, override the following using environment variables or a local settings file:

* **SECRET_KEY** – Keep it secret.
* **DATABASES** – Use PostgreSQL or another production database.
* **EMAIL_HOST_PASSWORD** – Use an app password for Gmail.
* **CACHES** – Configure Redis/Memcached for production (see below).
* **ALLOWED_HOSTS**, **CORS_ALLOWED_ORIGINS** – Adjust as needed.

---

## 📧 Email (for verification and password reset)

The project uses Gmail SMTP by default. Update these settings:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## ⚡ Cache for view counting

View counting uses Django’s cache framework. For production, set up Redis:

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

The TTL for view tracking is `DEFAULT_VIEW_TTL` (24 hours by default).

---

# 📘 API Documentation

Interactive API documentation is available when the server is running:

* Swagger UI:
  [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)

* ReDoc:
  [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

---

# 🗂 Project Structure

```
ketabgardoon/
├── api/                      # API versioning root
│   └── v1/                   # Version 1
│       ├── urls.py           # v1 URL routing
│       └── view_cache.py     # View counting utilities
├── authors/                  # Authors app
├── books/                    # Books, publishers, categories, ratings
├── comments/                 # Comments and likes
├── countries/                # Countries for author nationalities
├── custom_users/             # Custom user model and authentication
├── lists/                    # User lists (reading lists)
├── readingGoal/              # Reading target tracking
├── search/                   # Search functionality
├── media/                    # User uploaded files (profile images, book covers, list icons)
├── manage.py
├── requirements.txt
└── ketabgardoon/             # Project settings
    ├── settings.py
    ├── urls.py
    └── ...
```

---

# 🔐 Authentication Flow

### 1️⃣ Submit Email

`POST /api/v1/submit-email/`
Creates a temporary user and sends a 6-digit verification code.

### 2️⃣ Verify Email

`POST /api/v1/verify-email/`
Validates the code.

### 3️⃣ Complete Registration

`POST /api/v1/complete-registration/`
Sets username, password, and other profile data; promotes temporary user to permanent; creates default lists.

### 4️⃣ Login

`POST /api/v1/login/`
Returns JWT access and refresh tokens.

### 5️⃣ Token Refresh

`POST /api/v1/token/refresh/`

### 6️⃣ Password Change (authenticated)

`POST /api/v1/change-password/`

### 7️⃣ Password Reset (unauthenticated)

```
POST /api/v1/password-reset/request/
POST /api/v1/password-reset/confirm/
```

---

# 🌐 Main Endpoints

All endpoints are prefixed with `/api/v1/`.

| Resource         | Endpoint                      | Methods                       | Description                                     |
| ---------------- | ----------------------------- | ----------------------------- | ----------------------------------------------- |
| **Users**        | `/users/`                     | GET, POST                     | List users (admin only for all) / create user   |
|                  | `/users/{id}/`                | GET, PUT, PATCH, DELETE       | Retrieve/update/delete user profile             |
|                  | `/users/me/`                  | GET, PATCH                    | Retrieve/update own profile                     |
| **Books**        | `/books/`                     | GET, POST                     | List books (paginated, search, sort) / create   |
|                  | `/books/{id}/`                | GET, PUT, PATCH, DELETE       | Retrieve/update/delete book                     |
|                  | `/books/{book_id}/myrating/`  | GET, POST, PUT, PATCH, DELETE | Manage current user’s rating on a book          |
|                  | `/books/ratings/`             | GET                           | List current user’s ratings                     |
| **Authors**      | `/authors/`                   | GET, POST                     | List authors (paginated, search, sort) / create |
|                  | `/authors/{id}/`              | GET, PUT, PATCH, DELETE       | Retrieve/update/delete author                   |
|                  | `/authors/{author_id}/books/` | GET                           | List books by a specific author                 |
| **Comments**     | `/comments/`                  | GET, POST                     | List comments (filter by book/user) / create    |
|                  | `/comments/{id}/`             | GET, PUT, PATCH, DELETE       | Retrieve/update/delete comment                  |
|                  | `/comments/{id}/like/`        | GET, POST, DELETE             | Like/unlike a comment                           |
| **Lists**        | `/lists/`                     | GET, POST                     | List user’s lists / create new list             |
|                  | `/lists/{id}/`                | GET, PUT, PATCH, DELETE       | Retrieve/update/delete list                     |
|                  | `/lists/{id}/books/`          | GET, POST, DELETE             | List/add/remove books in a list                 |
|                  | `/lists/icons/`               | GET                           | List available icon filenames and URLs          |
| **Reading Goal** | `/reading-target/`            | GET, POST                     | Get or set current year’s reading target        |
| **Search**       | `/search/?q=...`              | GET                           | Global search (books, authors, users)           |
|                  | `/category-search/?q=...`     | GET                           | Search categories and return their books        |

---

# 🧪 Testing

Run all tests with:

```bash
python manage.py test
```

Test files are located inside each app (e.g., `authors/tests.py`, `books/tests.py`). They cover models, serializers, viewsets, authentication, and edge cases.

---

# 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

---

# 🎓 Academic Context

Developed as part of a **Software Engineering course**

📅 Spring 2025

---

# 📄 License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

💬 For questions or support, please open an issue on GitHub.

---
