# Імпортуємо функцію path для опису URL-маршрутів
from django.urls import path

# Імпортуємо модуль views, де знаходиться логіка обробки запитів
from . import views


# Список маршрутів додатку
urlpatterns = [

    # Сторінка кошика
    # Викликає функцію cart_view, яка зазвичай відображає всі товари в кошику користувача
    path('cart/', views.cart_view, name='cart'),

    # Додавання товару в кошик
    # <int:product_id> означає, що в URL передається числовий ідентифікатор товару
    # Наприклад: /cart/add/5/
    # У view буде доступний параметр product_id
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Видалення позиції з кошика
    # item_id - це ID конкретного об'єкта CartItem
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Оновлення позиції в кошику
    # Зазвичай використовується для зміни кількості товару (quantity)
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),

    # Оформлення замовлення
    # Тут зазвичай створюється Order на основі Cart і очищається кошик
    path('checkout/', views.checkout, name='checkout'),
]