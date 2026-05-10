# Базові модулі Django для моделей
from django.db import models

# Агрегатна функція (для середнього значення рейтингу)
from django.db.models import Avg

# Для генерації slug з назви
from django.utils.text import slugify

# Для генерації випадкового значення (fallback для slug)
import uuid

# BRAND
class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назва')
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренди'

    def __str__(self):
        return self.name

# CATEGORY
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назва')
    slug = models.SlugField(unique=True)

    # Іконка (наприклад emoji або короткий символ)
    icon = models.CharField(max_length=10, blank=True, default='📦')

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name

# COLOR
class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name='Назва')

    # HEX-код кольору (#FFFFFF)
    hex_code = models.CharField(max_length=7, default='#000000')

    class Meta:
        verbose_name = 'Колір'
        verbose_name_plural = 'Кольори'

    def __str__(self):
        return self.name

# PRODUCT
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Назва')

    slug = models.SlugField(unique=True, blank=True)

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категорія')

    description = models.TextField(verbose_name='Опис', blank=True)

    # Базова ціна
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')

    # Стара ціна (для знижки)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стара ціна')

    # Варіанти товару
    colors = models.ManyToManyField(Color, blank=True, verbose_name='Кольори')
    memory_options = models.ManyToManyField('MemoryOption', blank=True, verbose_name='Внутрішня пам\'ять')
    case_size_options = models.ManyToManyField('CaseSizeOption', blank=True, verbose_name='Розміри корпусу')
    screen_size_options = models.ManyToManyField('ScreenSizeOption', blank=True, verbose_name='Діагональ екрана')

    # Рейтинг
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name='Рейтинг')

    is_available = models.BooleanField(default=True, verbose_name='В наявності')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']

    # Автоматична генерація slug
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            # Якщо slug не вийшов
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]

            slug = base_slug
            counter = 1

            # Забезпечуємо унікальність slug
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # Відсоток знижки
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0

    # Основне зображення товару
    def main_image(self):
        img = self.images.filter(is_main=True).first()
        if not img:
            img = self.images.first()
        return img

    # Отримання ціни для варіанту товару
    def price_for_variant(self, memory=None, case_size=None, screen_size=None):

        if screen_size:
            screen_size_price = self.screen_size_prices.filter(screen_size=screen_size).first()
            if screen_size_price:
                return screen_size_price.price, screen_size_price.old_price

        if case_size:
            case_size_price = self.case_size_prices.filter(case_size=case_size).first()
            if case_size_price:
                return case_size_price.price, case_size_price.old_price

        if memory:
            memory_price = self.memory_prices.filter(memory=memory).first()
            if memory_price:
                return memory_price.price, memory_price.old_price

        # Якщо варіанту немає - повертаємо базову ціну
        return self.price, self.old_price

    # Обгортка для пам’яті
    def price_for_memory(self, memory=None):
        return self.price_for_variant(memory=memory)

    # Оновлення рейтингу на основі відгуків
    def update_rating(self):
        avg_rating = self.reviews.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg'] or 0

        self.rating = round(avg_rating, 1)

        # Оновлюємо тільки поле rating
        self.save(update_fields=['rating'])

    def __str__(self):
        return self.name

# PRODUCT IMAGE
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    image = models.ImageField(upload_to='products/')

    # Чи є головним зображенням
    is_main = models.BooleanField(default=False)

    # Прив’язка до кольору
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Зображення'
        verbose_name_plural = 'Зображення'

# PRODUCT SPEC
class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs')

    key = models.CharField(max_length=100, verbose_name='Характеристика')
    value = models.CharField(max_length=200, verbose_name='Значення')

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'

# OPTIONS
class MemoryOption(models.Model):
    label = models.CharField(max_length=50, unique=True, verbose_name='Об\'єм внутрішньої пам\'яті')

    class Meta:
        verbose_name = 'Внутрішня пам\'ять'
        verbose_name_plural = 'Внутрішня пам\'ять'
        ordering = ['label']

    def __str__(self):
        return self.label


class CaseSizeOption(models.Model):
    label = models.CharField(max_length=50, unique=True, verbose_name='Размір корпуса')

    class Meta:
        verbose_name = 'Размір корпуса'
        verbose_name_plural = 'Разміри корпуса'
        ordering = ['label']

    def __str__(self):
        return self.label


class ScreenSizeOption(models.Model):
    label = models.CharField(max_length=50, unique=True, verbose_name='Діагональ екрана')

    class Meta:
        verbose_name = 'Діагональ екрана'
        verbose_name_plural = 'Діагоналі екрана'
        ordering = ['label']

    def __str__(self):
        return self.label

# ЦІНИ ДЛЯ ВАРІАНТІВ
class ProductMemoryPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='memory_prices')
    memory = models.ForeignKey(MemoryOption, on_delete=models.CASCADE, related_name='product_prices')

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стара ціна')

    class Meta:
        verbose_name = 'Ціна по пам\'яті'
        verbose_name_plural = 'Ціни по пам\'яті'
        unique_together = ('product', 'memory')

    def __str__(self):
        return f'{self.product.name} - {self.memory.label}'

class ProductCaseSizePrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='case_size_prices')
    case_size = models.ForeignKey(CaseSizeOption, on_delete=models.CASCADE, related_name='product_prices')

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стара ціна')

    class Meta:
        verbose_name = 'Ціна по розміру корпуса'
        verbose_name_plural = 'Ціни по розміру корпуса'
        unique_together = ('product', 'case_size')

    def __str__(self):
        return f'{self.product.name} - {self.case_size.label}'

class ProductScreenSizePrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='screen_size_prices')
    screen_size = models.ForeignKey(ScreenSizeOption, on_delete=models.CASCADE, related_name='product_prices')

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Ціна')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стара ціна')

    class Meta:
        verbose_name = 'Ціна по діагоналі екрана'
        verbose_name_plural = 'Ціни по діагоналі екрана'
        unique_together = ('product', 'screen_size')

    def __str__(self):
        return f'{self.product.name} - {self.screen_size.label}'