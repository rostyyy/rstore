# Імпортуємо базу моделей Django
from django.db import models

# Стандартна модель користувача Django
from django.contrib.auth.models import User

# Імпортуємо моделі товарів і їх опцій (колір, пам’ять і т.д.)
from apps.products.models import Product, Color, MemoryOption, CaseSizeOption, ScreenSizeOption

# КОШИК
class Cart(models.Model):

    # Один користувач = один кошик (OneToOne)
    # related_name='cart' дозволяє отримати кошик через user.cart
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    # Дата створення (автоматично встановлюється при створенні)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Назви для адмінки
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошики'

    # Загальна сума кошика
    def total(self):
        # items - це related_name з CartItem
        return sum(item.total_price() for item in self.items.all())

    # Загальна кількість товарів у кошику
    def count(self):
        return sum(item.quantity for item in self.items.all())

# ПОЗИЦІЯ КОШИКА
class CartItem(models.Model):

    # Прив’язка до кошика (один кошик - багато позицій)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

    # Товар
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Опціональні характеристики товару
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    memory = models.ForeignKey(MemoryOption, on_delete=models.SET_NULL, null=True, blank=True)
    case_size = models.ForeignKey(CaseSizeOption, on_delete=models.SET_NULL, null=True, blank=True)
    screen_size = models.ForeignKey(ScreenSizeOption, on_delete=models.SET_NULL, null=True, blank=True)

    # Ціна за одиницю (може зберігатись окремо, щоб не залежати від зміни ціни товару)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Кількість товару
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Позиція кошика'
        verbose_name_plural = 'Позиції кошика'

    # Загальна ціна позиції
    def total_price(self):
        # Якщо unit_price задана - використовуємо її
        # Інакше беремо актуальну ціну товару
        price = self.unit_price if self.unit_price is not None else self.product.price
        return price * self.quantity

# ЗАМОВЛЕННЯ
class Order(models.Model):

    # Варіанти статусів замовлення
    STATUS_CHOICES = [
        ('pending', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    # Користувач, який зробив замовлення
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # Статус замовлення (вибір зі списку)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Загальна ціна замовлення (зазвичай фіксується при створенні)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Адреса доставки
    address = models.TextField(verbose_name='Адрес', blank=True)

    # Дата створення
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

        # Сортування: новіші зверху
        ordering = ['-created_at']

    # Як об'єкт відображається (наприклад, в адмінці)
    def __str__(self):
        return f'Замовлення #{self.id} — {self.user.username}'

# ПОЗИЦІЯ ЗАМОВЛЕННЯ
class OrderItem(models.Model):

    # Прив’язка до замовлення
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')

    # Товар
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Опції (як і в кошику)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    memory = models.ForeignKey(MemoryOption, on_delete=models.SET_NULL, null=True, blank=True)
    case_size = models.ForeignKey(CaseSizeOption, on_delete=models.SET_NULL, null=True, blank=True)
    screen_size = models.ForeignKey(ScreenSizeOption, on_delete=models.SET_NULL, null=True, blank=True)

    # Кількість
    quantity = models.PositiveIntegerField(default=1)

    # Зафіксована ціна на момент покупки
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Загальна ціна позиції
    def total_price(self):
        return self.price * self.quantity