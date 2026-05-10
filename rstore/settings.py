# Імпорт Path для роботи з файловими шляхами
import os
from pathlib import Path
from dotenv import load_dotenv

# БАЗОВА ДИРЕКТОРІЯ ПРОЄКТУ
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# СЕКРЕТНИЙ КЛЮЧ
SECRET_KEY = os.getenv("SECRET_KEY")

# РЕЖИМ ВІДЛАДКИ
DEBUG = os.getenv("DEBUG") == "True"

# ДОЗВОЛЕНІ ХОСТИ
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.onrender.com',
]

# ВСТАНОВЛЕНІ ДОДАТКИ
INSTALLED_APPS = [
    'django.contrib.admin',        # адмін панель
    'django.contrib.auth',         # авторизація
    'django.contrib.contenttypes', # типи контенту
    'django.contrib.sessions',     # сесії
    'django.contrib.messages',     # повідомлення
    'django.contrib.staticfiles',  # статичні файли

    # кастомні додатки проєкту
    'apps.users',
    'apps.products',
    'apps.orders',
    'apps.reviews',
]

# MIDDLEWARE (ПРОМІЖНІ ШАРИ)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',        # безпека
    'whitenoise.middleware.WhiteNoiseMiddleware', # обслуговування статичних файлів у продакшені
    'django.contrib.sessions.middleware.SessionMiddleware', # сесії
    'django.middleware.common.CommonMiddleware',            # загальна обробка запитів
    'django.middleware.csrf.CsrfViewMiddleware',            # CSRF захист
    'django.contrib.auth.middleware.AuthenticationMiddleware', # авторизація
    'django.contrib.messages.middleware.MessageMiddleware',  # messages framework
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # захист від clickjacking
]

# URL ROOT
ROOT_URLCONF = 'rstore.urls'

# ШАБЛОНИ (TEMPLATES)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # папка з глобальними шаблонами
        'DIRS': [BASE_DIR / 'templates'],

        # дозволяє шукати templates всередині apps
        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                # доступ до request у шаблонах
                'django.template.context_processors.request',

                # авторизація користувача в шаблонах
                'django.contrib.auth.context_processors.auth',

                # повідомлення (messages)
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI (ВХІДНА ТОЧКА СЕРВЕРА)
WSGI_APPLICATION = 'rstore.wsgi.application'

# БАЗА ДАНИХ
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # SQLite (dev база)
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ВАЛІДАЦІЯ ПАРОЛІВ
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]

# ЛОКАЛІЗАЦІЯ
LANGUAGE_CODE = 'uk'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True   # переклади
USE_TZ = True     # timezone підтримка

# СТАТИЧНІ ФАЙЛИ
STATIC_URL = '/static/'

# локальні static файли (css, js, images)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA (ФАЙЛИ КОРИСТУВАЧІВ)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REDIRECTS ПІСЛЯ LOGIN/LOGOUT
LOGIN_URL = '/users/login/'        # куди веде login_required
LOGIN_REDIRECT_URL = '/'           # після входу
LOGOUT_REDIRECT_URL = '/'          # після виходу