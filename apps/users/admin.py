# Імпортуємо модуль адміністративної панелі Django
from django.contrib import admin

# Імпортуємо моделі профілю та списку бажань
from .models import Profile, Wishlist

# АДМІНКА ПРОФІЛЮ КОРИСТУВАЧА
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Поля, які відображаються в списку профілів
    list_display = (
        'user',     # пов'язаний користувач
        'phone',    # номер телефону
        'balance'   # баланс користувача
    )

    # Поля, по яких можна шукати профіль
    search_fields = (
        'user__username',  # пошук по імені користувача
        'user__email',     # пошук по email
        'phone'            # пошук по телефону
    )

# АДМІНКА СИСТЕМИ WISHLIST
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    # Поля для відображення в таблиці списку бажань
    list_display = (
        'user',       # користувач
        'product',    # товар
        'color',      # обраний колір
        'memory',     # обраний варіант пам'яті
        'added_at'    # дата додавання
    )

    # Фільтри в правій панелі адмінки
    list_filter = (
        'added_at',   # фільтр по даті
        'color',      # фільтр по кольору
        'memory'      # фільтр по пам’яті
    )

    # Пошук по користувачу і товару
    search_fields = (
        'user__username',  # ім'я користувача
        'product__name'    # назва товару
    )