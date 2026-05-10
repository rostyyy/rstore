# Базові функції Django для рендеру сторінок і отримання об’єктів
from django.shortcuts import render, get_object_or_404

# Q і F потрібні для складних фільтрів у ORM
from django.db.models import Q, F

# Моделі продуктів
from .models import Product, Category, Brand, Color, MemoryOption

# Регулярні вирази для обробки пам’яті
import re

# ДОПОМІЖНА ФУНКЦІЯ СОРТУВАННЯ ПАМ’ЯТІ
def _memory_sort_key(memory):
    # Витягуємо число з label
    match = re.search(r'\d+', memory.label or '')

    if match:
        return int(match.group())

    # Якщо числа немає - ставимо в кінець
    return float('inf')

# СТОРІНКА СПИСКУ ТОВАРІВ (КАТАЛОГ)
def product_list(request):

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    # Базовий queryset товарів
    products_qs = Product.objects.filter(
        is_available=True
    ).select_related('brand', 'category').prefetch_related(
        'images', 'colors', 'memory_options', 'memory_prices'
    )

    # Дані для фільтрів
    categories = Category.objects.all()
    brands = Brand.objects.all().order_by('name')
    colors = Color.objects.all()
    memory_options = MemoryOption.objects.all()

    # Отримання параметрів з URL
    category_slug = request.GET.get('category', '')
    selected_brands = request.GET.getlist('brand')
    selected_colors = request.GET.getlist('color')
    selected_memories = request.GET.getlist('memory')

    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_rating = request.GET.get('min_rating', '')

    in_stock_only = request.GET.get('in_stock') == '1'
    discounts_only = request.GET.get('discounts_only') == '1'

    sort = request.GET.get('sort', 'price_asc')
    search_query = request.GET.get('q', '')

    # ФІЛЬТРАЦІЯ
    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)

    if selected_brands:
        products_qs = products_qs.filter(brand__id__in=selected_brands)

    if selected_colors:
        products_qs = products_qs.filter(colors__id__in=selected_colors)

    if selected_memories:
        products_qs = products_qs.filter(memory_options__id__in=selected_memories)

    if min_price:
        products_qs = products_qs.filter(price__gte=min_price)

    if max_price:
        products_qs = products_qs.filter(price__lte=max_price)

    if min_rating:
        products_qs = products_qs.filter(rating__gte=min_rating)

    if in_stock_only:
        products_qs = products_qs.filter(is_available=True)

    if discounts_only:
        products_qs = products_qs.filter(
            old_price__isnull=False,
            old_price__gt=F('price')
        )

    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # СОРТУВАННЯ
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'rating': '-rating',
        'name_asc': 'name',
        'name_desc': '-name',
    }

    products_qs = products_qs.distinct().order_by(
        sort_map.get(sort, 'price')
    )

    # ПАГІНАЦІЯ
    paginator = Paginator(products_qs, 40)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # ОБРОБКА ДАНИХ ДЛЯ UI
    for product in products:

        # Кольорові зображення
        color_images = {}
        for img in product.images.all():
            if img.color:
                color_images[img.color.id] = img.image.url
        product.color_images = color_images

        # Варіанти пам’яті з цінами
        memory_prices = {
            item.memory_id: item
            for item in product.memory_prices.all()
        }

        product.memory_choices = []

        for memory in sorted(product.memory_options.all(), key=_memory_sort_key):
            memory_price = memory_prices.get(memory.id)

            product.memory_choices.append({
                'id': memory.id,
                'label': memory.label,
                'price': memory_price.price if memory_price else product.price,
                'old_price': memory_price.old_price if memory_price else product.old_price,
            })

    # Контекст для шаблону
    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'colors': colors,
        'memory_options': memory_options,

        'current_category': category_slug,
        'selected_brands': selected_brands,
        'selected_colors': selected_colors,
        'selected_memories': selected_memories,

        'search_query': search_query,
        'current_sort': sort,

        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,

        'in_stock_only': in_stock_only,
        'discounts_only': discounts_only,

        'paginator': paginator,
        'page_obj': products,
    }

    return render(request, 'products/product_list.html', context)

# ПЕРЕГЛЯНУТІ ТОВАРИ
def _get_recently_viewed_products(request, limit=6, exclude_id=None):

    viewed_ids = request.session.get('recently_viewed_product_ids', [])

    if exclude_id:
        viewed_ids = [pid for pid in viewed_ids if pid != exclude_id]

    if not viewed_ids:
        return Product.objects.none()

    products_map = Product.objects.filter(
        id__in=viewed_ids,
        is_available=True,
    ).select_related('brand', 'category').prefetch_related(
        'images', 'colors', 'memory_options'
    ).in_bulk()

    ordered = [
        products_map[pid]
        for pid in viewed_ids
        if pid in products_map
    ]

    return ordered[:limit]

# ГОЛОВНА СТОРІНКА
def home(request):

    categories = Category.objects.all()

    recommended_products = Product.objects.filter(
        is_available=True
    ).select_related(
        'brand', 'category'
    ).prefetch_related(
        'images', 'colors', 'memory_options', 'memory_prices'
    ).order_by('-rating', '-created_at')[:18]

    recently_viewed_products = _get_recently_viewed_products(
        request,
        limit=14
    )

    context = {
        'categories': categories,
        'recommended_products': recommended_products,
        'recently_viewed_products': recently_viewed_products,
    }

    return render(request, 'products/home.html', context)

# ДЕТАЛІ ТОВАРУ
def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects.prefetch_related(
            'memory_options',
            'memory_prices',
            'case_size_options',
            'case_size_prices',
            'screen_size_options',
            'screen_size_prices'
        ),
        slug=slug,
    )

    specs = product.specs.all()
    reviews = product.reviews.filter(is_approved=True)

    images = product.images.select_related('color')

    images_by_color = {}
    all_image_urls = []

    for img in images:
        all_image_urls.append(img.image.url)

        if img.color_id:
            images_by_color.setdefault(str(img.color_id), []).append(img.image.url)

    memory_prices = {item.memory_id: item for item in product.memory_prices.all()}
    case_size_prices = {item.case_size_id: item for item in product.case_size_prices.all()}
    screen_size_prices = {item.screen_size_id: item for item in product.screen_size_prices.all()}

    # Варіанти case size
    case_size_choices = []
    for case_size in product.case_size_options.all().order_by('label'):
        case_size_price = case_size_prices.get(case_size.id)

        case_size_choices.append({
            'id': case_size.id,
            'label': case_size.label,
            'price': case_size_price.price if case_size_price else product.price,
            'old_price': case_size_price.old_price if case_size_price else product.old_price,
        })

    # Варіанти screen size
    screen_size_choices = []
    for screen_size in product.screen_size_options.all().order_by('label'):
        screen_size_price = screen_size_prices.get(screen_size.id)

        screen_size_choices.append({
            'id': screen_size.id,
            'label': screen_size.label,
            'price': screen_size_price.price if screen_size_price else product.price,
            'old_price': screen_size_price.old_price if screen_size_price else product.old_price,
        })

    # Варіанти memory
    memory_choices = []
    for memory in sorted(product.memory_options.all(), key=_memory_sort_key):
        memory_price = memory_prices.get(memory.id)

        memory_choices.append({
            'id': memory.id,
            'label': memory.label,
            'price': memory_price.price if memory_price else product.price,
            'old_price': memory_price.old_price if memory_price else product.old_price,
        })

    # Рекомендовані товари
    related = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id).select_related(
        'brand', 'category'
    ).prefetch_related('images', 'colors')[:7]

    # Збереження в "переглянуті"
    viewed_ids = request.session.get('recently_viewed_product_ids', [])
    viewed_ids = [pid for pid in viewed_ids if pid != product.id]
    viewed_ids.insert(0, product.id)

    request.session['recently_viewed_product_ids'] = viewed_ids[:20]
    request.session.modified = True

    recently_viewed = _get_recently_viewed_products(
        request,
        limit=7,
        exclude_id=product.id
    )

    # Wishlist логіка
    wishlist_state = {}
    wishlist_combinations = []

    if request.user.is_authenticated:
        from apps.users.models import Wishlist

        variants = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).values('color_id', 'memory_id')

        for variant in variants:
            key = f"{variant['color_id'] or ''}:{variant['memory_id'] or ''}"
            wishlist_state[key] = True
            wishlist_combinations.append(key)

    context = {
        'product': product,
        'specs': specs,
        'reviews': reviews,

        'images': images,
        'images_by_color': images_by_color,
        'all_image_urls': all_image_urls,

        'memory_choices': memory_choices,
        'case_size_choices': case_size_choices,
        'screen_size_choices': screen_size_choices,

        'related': related,
        'recently_viewed': recently_viewed,

        'wishlist_state': wishlist_state,
        'wishlist_combinations': wishlist_combinations,
    }

    return render(request, 'products/product_detail.html', context)

# ПРО КОМПАНІЮ
def about_view(request):
    return render(request, 'products/about.html', {
        'company_name': 'RStore',
        'contact_email': 'contact@rstore.com',
        'contact_phone': '+380442224422',
    })