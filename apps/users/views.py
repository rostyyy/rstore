# Django shortcuts для роботи з рендером, редіректами та отриманням об'єктів
from django.shortcuts import render, redirect, get_object_or_404

# Функції аутентифікації Django
from django.contrib.auth import login, logout, authenticate

# Декоратор для обмеження доступу тільки авторизованим користувачам
from django.contrib.auth.decorators import login_required

# Система повідомлень Django (success, error, info)
from django.contrib import messages

# Вбудована форма логіну Django
from django.contrib.auth.forms import AuthenticationForm

# Кастомні форми
from .forms import RegisterForm
from .profile_forms import ProfileEditForm

# Моделі замовлень і wishlist
from apps.orders.models import Order
from apps.users.models import Wishlist

# Моделі варіацій товару
from apps.products.models import Color, MemoryOption

# РЕЄСТРАЦІЯ
def register_view(request):

    # Якщо користувач вже залогінений - не даємо реєструватися
    if request.user.is_authenticated:
        return redirect('product_list')

    # POST запит (відправка форми)
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Створюємо користувача
            user = form.save()

            # Автоматичний логін після реєстрації
            login(request, user)

            # Повідомлення про успіх
            messages.success(request, 'Реєстрація пройшла успішно!')

            return redirect('product_list')

    else:
        # Порожня форма
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

# ЛОГІН
def login_view(request):

    # Якщо вже авторизований
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':

        # Вбудована Django форма авторизації
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # Отримуємо користувача
            user = form.get_user()

            # Логін
            login(request, user)

            # Повернення на попередню сторінку або на каталог
            next_url = request.GET.get('next', 'product_list')

            return redirect(next_url)

        else:
            # Помилка авторизації
            messages.error(request, 'Невірний логін або пароль.')

    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})

# ЛОГАУТ
def logout_view(request):

    # Вихід з системи
    logout(request)

    # Повернення на головну/каталог
    return redirect('product_list')

# ПРОФІЛЬ КОРИСТУВАЧА
@login_required
def profile_view(request):

    # Отримуємо профіль (OneToOne з User)
    profile = request.user.profile

    # Отримуємо замовлення користувача з оптимізацією запитів
    orders = request.user.orders.prefetch_related(
        'items__product__images',
        'items__color',
        'items__memory',
        'items__case_size',
    )

    # Отримуємо wishlist користувача
    wishlist = list(
        request.user.wishlist.select_related(
            'product', 'color', 'memory'
        ).prefetch_related('product__images')
    )

    # Підбираємо правильне зображення для кожного wishlist item
    for item in wishlist:
        images = list(item.product.images.all())

        item.display_image = None

        # Спочатку пробуємо знайти по кольору
        if item.color:
            item.display_image = next(
                (img for img in images if img.color_id == item.color_id),
                None
            )

        # Якщо немає - беремо main image
        if item.display_image is None:
            item.display_image = (
                next((img for img in images if img.is_main), None)
                or (images[0] if images else None)
            )

    return render(request, 'users/profile.html', {
        'profile': profile,
        'orders': orders,
        'wishlist': wishlist,
    })

# РЕДАГУВАННЯ ПРОФІЛЮ
@login_required
def profile_edit_view(request):

    profile = request.user.profile

    if request.method == 'POST':

        # Передаємо request.FILES для аватара
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено!')
            return redirect('profile')

    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(request, 'users/profile_edit.html', {
        'form': form,
        'profile': profile
    })

# TOGGLE WISHLIST (додати/видалити)
@login_required
def wishlist_toggle(request, product_id):

    from apps.products.models import Product

    # Отримуємо товар
    product = get_object_or_404(Product, id=product_id)

    color = None
    memory = None

    # Варіації з GET параметрів
    color_id = request.GET.get('color_id') or None
    memory_id = request.GET.get('memory_id') or None

    # Колір
    if color_id:
        try:
            color = Color.objects.get(id=color_id)
        except Color.DoesNotExist:
            pass

    # Пам’ять
    if memory_id:
        try:
            memory = MemoryOption.objects.get(id=memory_id)
        except MemoryOption.DoesNotExist:
            pass

    # Створення або отримання запису wishlist
    obj, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
        color=color,
        memory=memory,
    )

    # Якщо вже існує - видаляємо (toggle логіка)
    if not created:
        obj.delete()
        messages.info(request, 'Видалено з обраного.')
    else:
        messages.success(request, 'Додано до обраного!')

    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

# ДОПОМІЖНА ФУНКЦІЯ ДЛЯ ЗОБРАЖЕНЬ У ЗАМОВЛЕННІ
def _attach_order_item_images(order):

    for item in order.items.all():
        images = list(item.product.images.all())

        item.display_image = None

        # Спочатку пробуємо знайти по кольору
        if item.color:
            item.display_image = next(
                (img for img in images if img.color_id == item.color_id),
                None
            )

        # Якщо немає - беремо головне зображення
        if item.display_image is None:
            item.display_image = (
                next((img for img in images if img.is_main), None)
                or (images[0] if images else None)
            )

# ДЕТАЛІ ЗАМОВЛЕННЯ
@login_required
def order_detail_view(request, order_id):

    # Отримуємо замовлення тільки поточного користувача
    order = get_object_or_404(
        request.user.orders.prefetch_related(
            'items__product__images',
            'items__color',
            'items__memory',
            'items__case_size'
        ),
        id=order_id,
    )

    # Додаємо зображення до кожного item
    _attach_order_item_images(order)

    return render(request, 'users/order_detail.html', {
        'order': order
    })