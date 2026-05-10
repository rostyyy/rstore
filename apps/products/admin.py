# Імпортуємо адмінку Django
from django.contrib import admin

# Імпортуємо всі моделі, які будемо реєструвати в адмінці
from .models import (
    Brand,
    Category,
    Color,
    Product,
    ProductImage,
    ProductSpec,
    MemoryOption,
    ProductMemoryPrice,
    CaseSizeOption,
    ProductCaseSizePrice,
    ScreenSizeOption,
    ProductScreenSizePrice,
)

# INLINE-МОДЕЛІ (всередині Product)

# Картинки товару
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # кількість порожніх форм для додавання


# Характеристики товару
class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1


# Ціни для варіантів пам’яті
class ProductMemoryPriceInline(admin.TabularInline):
    model = ProductMemoryPrice
    extra = 1


# Ціни для варіантів розміру корпусу
class ProductCaseSizePriceInline(admin.TabularInline):
    model = ProductCaseSizePrice
    extra = 1


# Ціни для варіантів розміру екрану
class ProductScreenSizePriceInline(admin.TabularInline):
    model = ProductScreenSizePrice
    extra = 1

# PRODUCT ADMIN
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    # Поля, які відображаються в списку товарів
    list_display = ['name', 'brand', 'category', 'price', 'is_available', 'created_at']

    # Фільтри справа
    list_filter = ['brand', 'category', 'is_available']

    # Поля для пошуку
    search_fields = ['name', 'description']

    # Автоматичне заповнення slug на основі name
    prepopulated_fields = {'slug': ('name',)}

    # Inline-моделі (редагуються прямо в товарі)
    inlines = [
        ProductImageInline,
        ProductSpecInline,
        ProductMemoryPriceInline,
        ProductCaseSizePriceInline,
        ProductScreenSizePriceInline
    ]

    # Для ManyToMany полів зручний вибір через подвійний список
    filter_horizontal = ['colors', 'memory_options', 'case_size_options', 'screen_size_options']

# BRAND ADMIN
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    # Автогенерація slug
    prepopulated_fields = {'slug': ('name',)}

    # Пошук
    search_fields = ['name']

# CATEGORY ADMIN
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

# COLOR ADMIN
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    search_fields = ['name']

# MEMORY OPTION ADMIN
@admin.register(MemoryOption)
class MemoryOptionAdmin(admin.ModelAdmin):
    search_fields = ['label']

# CASE SIZE OPTION ADMIN
@admin.register(CaseSizeOption)
class CaseSizeOptionAdmin(admin.ModelAdmin):
    search_fields = ['label']

# SCREEN SIZE OPTION ADMIN
@admin.register(ScreenSizeOption)
class ScreenSizeOptionAdmin(admin.ModelAdmin):
    search_fields = ['label']