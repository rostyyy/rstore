# Імпортуємо адмін-панель Django
from django.contrib import admin

# Імпортуємо модель відгуків
from .models import Review

# Реєстрація моделі Review в адмінці через декоратор
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    # Колонки, які відображаються у списку відгуків
    list_display = [
        'user',          # користувач, який залишив відгук
        'product',       # товар, до якого відноситься відгук
        'rating',        # оцінка
        'is_approved',   # чи схвалений відгук
        'created_at'     # дата створення
    ]

    # Фільтри в правій панелі адмінки
    list_filter = [
        'is_approved',   # фільтр по статусу модерації
        'rating'         # фільтр по рейтингу
    ]

    # Поля, які можна редагувати прямо в списку
    list_editable = [
        'is_approved'
    ]

    # Пошук по полях
    search_fields = [
        'user__username',  # ім'я користувача
        'product__name',   # назва товару
        'text',            # текст відгуку
        'pros',            # плюси
        'cons'             # мінуси
    ]