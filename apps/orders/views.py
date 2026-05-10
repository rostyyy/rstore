# Імпортуємо допоміжні функції Django
from django.shortcuts import render, redirect, get_object_or_404

# Декоратор для перевірки авторизації
from django.contrib.auth.decorators import login_required

# Система повідомлень (success, error і т.д.)
from django.contrib import messages

# Імпортуємо моделі замовлень і кошика
from .models import Cart, CartItem, Order, OrderItem

# Імпортуємо моделі товарів і їх варіантів
from apps.products.models import Product, Color, MemoryOption, CaseSizeOption, ScreenSizeOption

# ВІДОБРАЖЕННЯ КОШИКА
@login_required
def cart_view(request):

    # Отримуємо кошик користувача або створюємо, якщо його ще немає
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Отримуємо всі позиції кошика
    # select_related - для ForeignKey (оптимізація)
    # prefetch_related - для many-to-many або reverse зв’язків (images)
    items = list(
        cart.items
        .select_related('product', 'color', 'memory', 'case_size')
        .prefetch_related('product__images')
    )

    # Логіка вибору картинки для кожного товару
    for item in items:
        images = list(item.product.images.all())

        # За замовчуванням картинки немає
        item.cart_image = None

        # Якщо вибраний колір - шукаємо картинку з цим кольором
        if item.color:
            item.cart_image = next(
                (img for img in images if img.color_id == item.color_id),
                None
            )

        # Якщо не знайшли - беремо головну або першу
        if item.cart_image is None:
            item.cart_image = (
                next((img for img in images if img.is_main), None)
                or (images[0] if images else None)
            )

    # Загальна сума кошика
    total = cart.total()

    # Рендер шаблону
    return render(request, 'orders/cart.html', {
        'cart': cart,
        'items': items,
        'total': total
    })

# ДОДАТИ В КОШИК
@login_required
def add_to_cart(request, product_id):

    # Отримуємо товар або 404
    product = get_object_or_404(Product, id=product_id)

    # Отримуємо або створюємо кошик
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Отримуємо параметри з POST-запиту
    color_id = request.POST.get('color_id') or None
    memory_id = request.POST.get('memory_id') or None
    case_size_id = request.POST.get('case_size_id') or None
    screen_size_id = request.POST.get('screen_size_id') or None

    # Початково всі опції None
    color = None
    memory = None
    case_size = None
    screen_size = None

    # Отримуємо об'єкти опцій (якщо передані)
    if color_id:
        try:
            color = Color.objects.get(id=color_id)
        except Color.DoesNotExist:
            pass

    if memory_id:
        try:
            memory = MemoryOption.objects.get(id=memory_id)
        except MemoryOption.DoesNotExist:
            pass

    if case_size_id:
        try:
            case_size = CaseSizeOption.objects.get(id=case_size_id)
        except CaseSizeOption.DoesNotExist:
            pass

    if screen_size_id:
        try:
            screen_size = ScreenSizeOption.objects.get(id=screen_size_id)
        except ScreenSizeOption.DoesNotExist:
            pass

    # Отримуємо ціну для конкретного варіанту товару
    unit_price, _ = product.price_for_variant(
        memory=memory,
        case_size=case_size,
        screen_size=screen_size
    )

    # Пошук або створення позиції кошика
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        color=color,
        memory=memory,
        case_size=case_size,
        screen_size=screen_size,
        defaults={'unit_price': unit_price},
    )

    # Якщо така позиція вже є - збільшуємо кількість
    if not created:
        item.unit_price = unit_price
        item.quantity += 1
        item.save()

    # Повідомлення користувачу
    messages.success(request, f'«{product.name}» доданий до кошика!')

    # Повертаємо назад (на попередню сторінку)
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

# ВИДАЛИТИ З КОШИКА
@login_required
def remove_from_cart(request, item_id):

    # Перевіряємо, що item належить саме цьому користувачу
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Видаляємо
    item.delete()

    return redirect('cart')

# ОНОВИТИ КОШИК
@login_required
def update_cart(request, item_id):

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # Отримуємо кількість з POST
    quantity = int(request.POST.get('quantity', 1))

    # Якщо кількість більше 0 - оновлюємо
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        # Якщо 0 або менше - видаляємо позицію
        item.delete()

    return redirect('cart')

# ОФОРМЛЕННЯ ЗАМОВЛЕННЯ
@login_required
def checkout(request):

    # Отримуємо кошик
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Отримуємо всі позиції
    items = cart.items.select_related(
        'product', 'color', 'memory', 'case_size', 'screen_size'
    )

    # Якщо кошик пустий - помилка
    if not items.exists():
        messages.error(request, 'Кошик порожній.')
        return redirect('cart')

    # Дані користувача (з профілю)
    profile = request.user.profile

    user_data = {
        'first_name': request.user.first_name or '',
        'last_name': request.user.last_name or '',
        'phone': profile.phone or '',
        'address': profile.address or '',
    }

    # Якщо форма відправлена
    if request.method == 'POST':

        # Отримуємо адресу
        address = request.POST.get('address', '')

        # Створюємо замовлення
        order = Order.objects.create(
            user=request.user,
            total_price=cart.total(),
            address=address,
        )

        # Створюємо позиції замовлення
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                color=item.color,
                memory=item.memory,
                case_size=item.case_size,
                screen_size=item.screen_size,
                quantity=item.quantity,
                price=item.unit_price if item.unit_price is not None else item.product.price,
            )

        # Очищаємо кошик
        cart.items.all().delete()

        messages.success(request, f'Замовлення #{order.id} оформлено!')

        return redirect('profile')

    # GET-запит - просто показуємо сторінку
    return render(request, 'orders/checkout.html', {
        'items': items,
        'total': cart.total(),
        'user_data': user_data
    })