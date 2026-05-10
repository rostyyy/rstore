# Функції для редиректу та отримання об’єктів або 404 помилки
from django.shortcuts import redirect, get_object_or_404

# Декоратор, який вимагає авторизації користувача
from django.contrib.auth.decorators import login_required

# Система повідомлень Django (success/error messages)
from django.contrib import messages

# Модель відгуку
from .models import Review

# Модель товару
from apps.products.models import Product

# ДОДАВАННЯ ВІДГУКУ
@login_required
def add_review(request, product_id):

    # Отримуємо товар або 404, якщо не існує
    product = get_object_or_404(Product, id=product_id)

    # Обробка тільки POST-запиту (відправка форми)
    if request.method == 'POST':

        # Рейтинг (за замовчуванням 5)
        rating = request.POST.get('rating', 5)

        # Текст відгуку (очищаємо від пробілів)
        text = request.POST.get('text', '').strip()

        # Плюси товару
        pros = request.POST.get('pros', '').strip()

        # Мінуси товару
        cons = request.POST.get('cons', '').strip()

        # Перевірка: хоча б одне поле має бути заповнене
        if text or pros or cons:

            # Створення нового відгуку
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                text=text,
                pros=pros,
                cons=cons,

                # Відгук завжди йде на модерацію
                is_approved=False,
            )

            # Повідомлення про успіх
            messages.success(request, 'Відгук надіслано на модерацію!')

        else:
            # Помилка, якщо нічого не заповнено
            messages.error(
                request,
                'Заповніть відгук: опис, плюси або мінуси.'
            )

    # Після обробки завжди повертаємо на сторінку товару
    return redirect('product_detail', slug=product.slug)