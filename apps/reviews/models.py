# Базові модулі Django для моделей
from django.db import models

# Стандартна модель користувача Django
from django.contrib.auth.models import User

# Модель товару, до якого прив’язуються відгуки
from apps.products.models import Product

# МОДЕЛЬ ВІДГУКУ
class Review(models.Model):

    # Товар, до якого належить відгук
    # related_name='reviews' дозволяє звертатися: product.reviews.all()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    # Користувач, який залишив відгук
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Рейтинг від 1 до 5
    # choices обмежує можливі значення
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=5
    )

    # Основний текст відгуку
    text = models.TextField(verbose_name='Текст відгуку')

    # Плюси товару (необов’язково)
    pros = models.TextField(verbose_name='Плюси', blank=True)

    # Мінуси товару (необов’язково)
    cons = models.TextField(verbose_name='Мінуси', blank=True)

    # Чи пройшов модерацію
    is_approved = models.BooleanField(default=False, verbose_name='Схвалений')

    # Дата створення відгуку
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'

        # Нові відгуки показуються першими
        ordering = ['-created_at']

    # Як об’єкт виглядає в адмінці
    def __str__(self):
        return f'Відгук від {self.user.username} на {self.product.name}'

    # При збереженні відгуку автоматично оновлюється рейтинг товару
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Після збереження оновлюємо середній рейтинг товару
        self.product.update_rating()

    # При видаленні відгуку також оновлюємо рейтинг товару
    def delete(self, *args, **kwargs):
        product = self.product

        super().delete(*args, **kwargs)

        # Перерахунок рейтингу після видалення
        product.update_rating()