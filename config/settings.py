"""
Django settings for the HO-ME (Horn of Africa Missions Engagers) project.

Production-aware configuration:
- Secrets and infrastructure config are read from environment variables.
- The admin portal lives on a configurable, non-standard URL.
- Brute-force protection (django-axes),
  secure cookies, strict password validation and short staff sessions are all
  enabled by default and controlled via environment variables.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default="False"):
    return os.environ.get(key, str(default)).strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-only-dev-key-change-me-in-production",
)

DEBUG = env_bool("DJANGO_DEBUG", "True")

ALLOWED_HOSTS = [
    h.strip()
    for h in env(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1,testserver,.onrender.com"
    ).split(",")
    if h.strip()
]
CSRF_TRUSTED_ORIGINS = [o for o in env("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o]

# Non-standard admin route (configurable via env, defaults to /admin-portal/)
ADMIN_SITE_HEADER = env("DJANGO_ADMIN_SITE_HEADER", "HO-ME Admin Portal")
ADMIN_URL = env("DJANGO_ADMIN_URL", "admin-portal/")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "axes",                            # Brute-force / lockout protection
    # Project apps
    "apps.core",
    "apps.cms_content",
    "apps.resources",
    "apps.accounts",
    "apps.security",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Language (English / Amharic / Oromifa): checks session/cookie. Must come
    # after SessionMiddleware and before CommonMiddleware.
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Audit trail: exposes the current request to audit signal receivers
    "apps.security.middleware.AuditRequestMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # django-axes must come after the auth middleware
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",   # LANGUAGE_CODE, LANGUAGES
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": env("DJANGO_DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": env("DJANGO_DB_NAME", BASE_DIR / "db.sqlite3"),
        **(
            {
                key: env(f"DJANGO_DB_{k}")
                for k in ("USER", "PASSWORD", "HOST", "PORT")
                if env(f"DJANGO_DB_{k}")
            }
        ),
    }
}

# ---------------------------------------------------------------------------
# Authentication & brute-force protection
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",          # must be first
    "django.contrib.auth.backends.ModelBackend",
]

# ---- django-axes: lock out after 5 failed attempts ----
AXES_ENABLED = env_bool("AXES_ENABLED", "True")
AXES_FAILURE_LIMIT = int(env("AXES_FAILURE_LIMIT", "5"))
AXES_COOLOFF_TIME = int(env("AXES_COOLOFF_SECONDS", "1800"))  # 30 minutes
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "security/lockout.html"
AXES_NEVER_LOCKOUT_WHITELIST = env_bool("AXES_NEVER_LOCKOUT_WHITELIST", "False")
AXES_ONLY_USER_SUBMITS = False
AXES_LOCKOUT_CALLABLE = None

# ---- Strict password policy ----
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "apps.accounts.models.ComplexityValidator",
    },
]

# ---- Session policy: short staff sessions, secure cookies when behind TLS ----
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = int(env("SESSION_COOKIE_AGE", str(60 * 45)))          # 45 min
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", "False")          # True in production (HTTPS)
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", "False")                # True in production
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", "False")              # True in production
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "0"))                  # e.g. 31536000 in production
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Templates / static / media
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en"

# Supported languages: English, Amharic (አማርኛ), Oromifa (Afaan Oromoo).
# Users switch via the language selector (cookie- or session-persisted).
LANGUAGES = [
    ("en", "English"),
    ("am", "Amharic / አማርኛ"),
    ("om", "Oromifa / Afaan Oromoo"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # remember the choice for a year
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Email (console backend for dev; swap via env for production)
# ---------------------------------------------------------------------------

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend" if env("EMAIL_HOST") else "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", "")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", "True")
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", "False")
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@ho-me.org")
CONTACT_EMAIL = env("CONTACT_EMAIL", "info@ho-me.org")

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
