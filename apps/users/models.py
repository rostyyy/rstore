# Базові моделі Django
from django.db import models

# Стандартна модель користувача Django
from django.contrib.auth.models import User

# Сигнали Django для автоматичних дій після збереження об'єкта
from django.db.models.signals import post_save
from django.dispatch import receiver

# Decimal використовується для фінансових значень (точні обчислення без float помилок)
from decimal import Decimal

# Моделі кольору та пам’яті з додатку продуктів
from apps.products.models import Color, MemoryOption

# ПРОФІЛЬ КОРИСТУВАЧА
class Profile(models.Model):
    # Один до одного зв’язок з користувачем Django
    # related_name='profile' дозволяє: user.profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Аватар користувача (необов’язковий)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    # Телефон користувача
    phone = models.CharField(
        max_length=20,
        blank=True
    )

    # Адреса доставки
    address = models.TextField(
        blank=True,
        verbose_name='Адреса доставки'
    )

    # Баланс користувача
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'

    def __str__(self):
        return f'Профіль: {self.user.username}'

# СИГНАЛИ ДЛЯ ПРОФІЛЮ
# Створення профілю автоматично при створенні користувача
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    # Якщо користувача тільки що створили
    if created:
        Profile.objects.create(user=instance)


# Збереження профілю при оновленні користувача
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):

    # Перевіряємо чи існує профіль перед збереженням
    if hasattr(instance, 'profile'):
        instance.profile.save()

# WISHLIST (ОБРАНІ ТОВАРИ)
class Wishlist(models.Model):

    # Користувач, якому належить "обране"
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )

    # Товар, який додано в обране
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )

    # Обраний колір товару (якщо є варіація)
    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Обрана пам’ять (якщо є варіація)
    memory = models.ForeignKey(
        MemoryOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Дата додавання в wishlist
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        # Заборона дублювання однакових комбінацій
        unique_together = ('user', 'product', 'color', 'memory')

        verbose_name = 'Обране'
        verbose_name_plural = 'Обране'