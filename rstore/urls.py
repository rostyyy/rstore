# Імпортуємо модуль адміністративної панелі Django
from django.contrib import admin

# Імпортуємо функції для роботи з URL: path - для окремих маршрутів, include - для підключення додатків
from django.urls import path, include

# Імпортуємо налаштування Django для доступу до MEDIA_URL та MEDIA_ROOT
from django.conf import settings

# Імпортуємо функцію static для обробки статичних та медіа-файлів під час розробки
from django.conf.urls.static import static

# Імпортуємо представлення (view) для сторінки "Про нас" з додатку products
from apps.products.views import about_view


# Основний список URL-паттернів проєкту
# Це центральний файл маршрутизації, який визначає, які URL ведуть до яких додатків
urlpatterns = [

    # Адміністративна панель Django
    # Доступна за адресою /admin/
    # Тут адміністратор може керувати товарами, замовленнями, користувачами тощо
    path('admin/', admin.site.urls),

    # Підключення URL-паттернів додатку products (головна сторінка, каталог, товари)
    # '' (порожній рядок) означає кореневу сторінку сайту
    # include() імпортує всі URL з apps/products/urls.py
    path('', include('apps.products.urls')),

    # Підключення URL-паттернів додатку users (реєстрація, вхід, профіль)
    # Всі маршрути цього додатку матимуть префікс /users/
    # Наприклад: /users/login/, /users/register/, /users/profile/
    path('users/', include('apps.users.urls')),

    # Підключення URL-паттернів додатку orders (кошик, замовлення)
    # Всі маршрути матимуть префікс /orders/
    # Наприклад: /orders/cart/, /orders/checkout/
    path('orders/', include('apps.orders.urls')),

    # Підключення URL-паттернів додатку reviews (відгуки)
    # Маршрути матимуть префікс /reviews/
    # Використовується для додавання відгуків до товарів
    path('reviews/', include('apps.reviews.urls')),

    # Сторінка "Про нас"
    # Доступна за адресою /about/
    # name='about' дозволяє використовувати {% url 'about' %} в шаблонах
    path('about/', about_view, name='about'),
]

# Додаємо підтримку медіа-файлів (зображень товарів, аватарів користувачів)
# Це потрібно тільки в режимі DEBUG для зручного тестування
# У продакшені медіа-файли обслуговуються веб-сервером (nginx) або CDN
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)