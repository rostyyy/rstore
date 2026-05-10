# Імпортуємо базовий клас конфігурації Django-додатку
from django.apps import AppConfig

# Конфігурація додатку reviews
class ReviewsConfig(AppConfig):
    
    # Тип первинного ключа за замовчуванням для моделей у цьому додатку
    # BigAutoField використовується для великих баз даних і є сучасним стандартом Django
    default_auto_field = 'django.db.models.BigAutoField'

    # Повний шлях до додатку в проєкті
    # Вказує Django, де знаходиться цей app (apps/reviews)
    name = 'apps.reviews'