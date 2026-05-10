# Імпортуємо базовий клас для конфігурації додатку в Django
from django.apps import AppConfig


# Клас конфігурації для додатку orders
class OrdersConfig(AppConfig):

    # Вказуємо тип поля за замовчуванням для первинного ключа (id)
    # BigAutoField - це великий автоінкрементний integer (64-bit)
    # Використовується замість стандартного AutoField (32-bit)
    # Це важливо для проєктів, де може бути дуже багато записів
    default_auto_field = 'django.db.models.BigAutoField'

    # Повне ім’я додатку (шлях до нього в проєкті)
    # apps.orders означає, що додаток лежить у папці apps/orders
    name = 'apps.orders'