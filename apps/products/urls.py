# Імпортуємо функцію path для створення URL-маршрутів
from django.urls import path

# Імпортуємо views (функції обробки запитів)
from . import views

# Список URL-маршрутів додатку
urlpatterns = [
    # Головна сторінка сайту
    # Порожній шлях '' означає root URL (наприклад /)
    path('', views.home, name='home'),

    # Сторінка каталогу товарів
    path('catalog/', views.product_list, name='product_list'),

    # Сторінка детального перегляду товару
    # <slug:slug> означає, що передається текстовий slug
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]