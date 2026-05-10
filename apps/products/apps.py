# Імпортуємо базовий клас конфігурації Django-додатку
from django.apps import AppConfig


# Клас конфігурації для додатку products
class ProductsConfig(AppConfig):

    # Тип поля за замовчуванням для первинного ключа (id)
    # BigAutoField - 64-бітне автоінкрементне поле
    # Рекомендується Django за замовчуванням для нових проєктів
    default_auto_field = 'django.db.models.BigAutoField'

    # Повне ім’я додатку (шлях у проєкті)
    # Вказує, що додаток знаходиться в папці apps/products
    name = 'apps.products'