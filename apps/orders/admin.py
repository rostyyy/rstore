# Імпортуємо стандартний модуль Django admin
from django.contrib import admin

# Імпортуємо моделі, з якими будемо працювати в адмінці
from .models import Cart, CartItem, Order, OrderItem


# Inline-клас для відображення елементів корзини (CartItem)
# прямо всередині корзини (Cart) в адмінці
class CartItemInline(admin.TabularInline):
    model = CartItem  # вказуємо, яку модель відображати
    extra = 0  # не показувати порожні додаткові форми для створення нових записів

    # Поля з автодоповненням (autocomplete) — зручно при великій кількості об'єктів
    autocomplete_fields = ('product', 'color', 'memory', 'case_size')


# Реєструємо модель Cart в адмінці через декоратор
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    # Які поля будуть показані в списку (таблиці) корзин
    list_display = ('id', 'user', 'created_at')

    # Поля для пошуку (можна шукати по username та email користувача)
    search_fields = ('user__username', 'user__email')

    # Додаємо inline (тобто CartItem буде видно прямо в Cart)
    inlines = (CartItemInline,)


# Inline для елементів замовлення (OrderItem)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    # Також автодоповнення для пов'язаних полів
    autocomplete_fields = ('product', 'color', 'memory', 'case_size')


# Реєструємо модель Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # Поля, які видно в списку замовлень
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')

    # Фільтри справа в адмінці (по статусу і даті створення)
    list_filter = ('status', 'created_at')

    # Поля для пошуку
    search_fields = ('id', 'user__username', 'user__email', 'address')

    # Inline елементи замовлення
    inlines = (OrderItemInline,)