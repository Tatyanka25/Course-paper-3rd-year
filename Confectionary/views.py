from venv import logger
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from Confectionary.models import Category, Product, Customer, Order, OrderItem, Employee, Event
from .forms import (
    CheckoutForm,
    CustomUserCreationForm,
    CustomCakeOrderForm,
    ProfileEditForm,
)
from decimal import Decimal


CATEGORY_ICONS = {
    "Кофе": "img/coffee.png",
    "Чай": "img/tea.png",
    "Горячий шоколад": "img/chocolate.png",
    "Молочные коктейли": "img/milkshake.png",
    "Лимонады и освежающие напитки": "img/lemon.png",
}

delivery_list = {
    "title": " Доставка заказов Whisk & Wonder ",
    "description": "Мы заботимся о качестве и свежести наших десертов, поэтому предлагаем удобные условия доставки.",
    "options": [
        {
            "type": "Самовывоз",
            "cost": "Бесплатно",
            "details": {
                "address": "г. Дзержинск, ул. Циолковского, д. 16",
                "time": "с 10:00 до 20:00",
                "note": "Уведомим вас, когда заказ будет готов",
            },
        },
        {
            "type": "Доставка по городу",
            "cost": "от 300 ₽ (бесплатно при заказе от 5000 ₽)",
            "details": {
                "time": "с 10:00 до 21:00",
                "min_order": "1500 ₽",
                "delivery_time": "1-3 часа после готовности заказа",
            },
        },
        {
            "type": "Доставка в пригород",
            "cost": "от 500 ₽, рассчитывается индивидуально",
            "details": {
                "range": "30 км от города",
                "min_order": "3000 ₽",
                "delivery_time": "от 3 часов",
            },
        },
    ],
    "conditions": {
        "order": {
            "text": "Оформление заказа",
            "details": [
                "Заказы принимаем за 1-3 дня до желаемой даты доставки",
                "Срочные заказы обсуждаются индивидуально",
                "Оплата: онлайн или наличными при получении",
            ],
        },
        "timing": {
            "text": "Доставка в указанное время",
            "details": [
                "Мы стараемся доставлять в выбранный интервал, но возможны отклонения до 30 минут из-за дорожной ситуации"
            ],
        },
        "handover": {
            "text": "Передача заказа",
            "details": [
                "Заказ передается лично получателю или доверенному лицу",
                "При отсутствии получателя курьер ждет до 15 минут, затем заказ можно забрать самовывозом",
            ],
        },
        "cancellation": {
            "text": "Возврат и отмена",
            "details": [
                "Отменить заказ можно за 24 часа до доставки",
                "Возврат возможен только при выявлении брака",
            ],
        },
    },
}

cake_order = {
    "title": "Торты на заказ для вашего праздника",
    "description": "Ни одно торжество не обходится без вкусного торта! В Whisk & Wonder вы можете заказать торт любого размера и дизайна – от нежных классических вариантов до ярких и креативных шедевров. Наши десерты станут идеальным дополнением к дню рождения, свадьбе или уютному семейному вечеру.",
    "order_terms": {
        "standard": "Мы принимаем заказы заранее: за 5-7 дней до мероприятия (в идеале за 10-14 дней).",
        "urgent": "Если дата свободна, возможны срочные заказы с доплатой.",
    },
    "how_to_order": {
        "instructions": "Заполните форму ниже, и мы свяжемся с вами, чтобы обсудить:",
        "details": ["Начинку", "Декор", "Количество порций / вес торта"],
    },
    "payment": {
        "prepayment": "После финального согласования мы закрепим за вами дату по 100% предоплате."
    },
    "delivery": {
        "options": [
            "В день мероприятия ваш торт будет доставлен по указанному адресу.",
            "Торт будет готов к самовывозу в нашей кондитерской по адресу: ул. Циолковского, 16.",
        ]
    },
    "requirements": {
        "min_weight": "Минимальный вес торта: 2 кг",
        "price_per_kg": "Стоимость: указана за 1 кг",
    },
    "final_message": "Сделаем ваш праздник по-настоящему сладким!",
}


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("Confectionary:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def profile_view(request):
    customer_profile, created = Customer.objects.get_or_create(user=request.user)
    if created:
        messages.info(request, "Создан профиль пользователя.")

    if request.method == "POST":
        form = ProfileEditForm(request.POST, user=request.user)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            user = request.user
            user.first_name = cleaned_data["first_name"]
            user.last_name = cleaned_data["last_name"]
            user.email = cleaned_data["email"]
            user.save()

            customer_profile.phone = cleaned_data["phone"]
            customer_profile.save()

            messages.success(request, "Информация профиля успешно обновлена.")
            return redirect("Confectionary:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")

    else:
        initial_data = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "phone": customer_profile.phone,
        }
        form = ProfileEditForm(initial=initial_data, user=request.user)

    context = {
        "user": request.user,
        "customer": customer_profile,
        "form": form,
    }
    return render(request, "profile_pages/profile.html", context)


def main_page(request):
    category_names = CATEGORY_ICONS.keys()
    categories = Category.objects.prefetch_related("products").filter(
        name__in=category_names
    )
    for category in categories:
        category.icon = CATEGORY_ICONS.get(category.name, "img/default_icon.png")

    popular_products = Product.objects.filter(is_popular=True)

    context = {"categories": categories, "popular_products": popular_products}

    return render(request, "main_page.html", context)


def showcase(request, type_slug=None):
    dessert_products = Product.objects.none()
    product_types_with_slugs = {}
    page_title = "Витрина десертов | Кондитерская Whisk & Wonder"
    meta_description = "Посмотрите наш ассортимент свежих десертов ручной работы: пирожные, эклеры, чизкейки и многое другое в кондитерской Whisk & Wonder."
    current_type_name = None

    try:
        dessert_category = Category.objects.get(name__iexact="Десерты")

        base_in_stock_desserts = Product.objects.filter(
            category=dessert_category, count_in_stock__gt=0
        )
        types_data = (
            base_in_stock_desserts.exclude(type__isnull=True)
            .exclude(type__exact="")
            .exclude(type_slug__isnull=True)
            .exclude(type_slug__exact="")
            .values("type", "type_slug")
            .distinct()
            .order_by("type")
        )

        product_types_with_slugs = {
            item["type"]: item["type_slug"] for item in types_data
        }

        if type_slug:
            dessert_products = base_in_stock_desserts.filter(type_slug=type_slug)
            current_type_name = next(
                (
                    name
                    for name, slug in product_types_with_slugs.items()
                    if slug == type_slug
                ),
                None,
            )

            if current_type_name:
                page_title = f"{current_type_name.capitalize()} - Десерты | Кондитерская Whisk & Wonder"
                meta_description = f"Купить {current_type_name.lower()} десерты онлайн. Свежие {current_type_name.lower()} десерты на заказ от кондитерской Whisk & Wonder."
            else:
                page_title = "Десерты не найдены | Кондитерская Whisk & Wonder"
                meta_description = "Выбранный тип десертов не найден или отсутствует."
                dessert_products = Product.objects.none()

        else:
            dessert_products = base_in_stock_desserts
            current_type_name = None

    except Category.DoesNotExist:
        page_title = "Десерты не найдены | Кондитерская Whisk & Wonder"
        meta_description = "Категория в данный момент недоступна."
        product_types_with_slugs = {}
        dessert_products = Product.objects.none()
        current_type_name = None

    context = {
        "product_types_with_slugs": product_types_with_slugs,
        "products": dessert_products,
        "selected_type_slug": type_slug,
        "page_title": page_title,
        "meta_description": meta_description,
        "current_type_name": current_type_name,
    }

    return render(request, "showcase.html", context)


def photo_album(request):
    all_events = Event.objects.prefetch_related('images').all()

    context = {
        "events": all_events 
    }
    return render(request, "photo_album.html", context)


def custom_cakes(request):
    cake_category = Category.objects.get(name="Торты")
    cakes = Product.objects.filter(category=cake_category)
    context = {"cake_order": cake_order, "cakes": cakes}

    if request.method == "POST":
        form = CustomCakeOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Заказ успешно оформлен!")
            return redirect("Confectionary:custom_cakes")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomCakeOrderForm()

    context = {"cake_order": cake_order, "cakes": cakes, "form": form}

    return render(request, "custom_cakes.html", context)


def delivery(request):
    context = {"delivery_list": delivery_list}
    return render(request, "delivery.html", context)


def employees(request):
    all_employees = Employee.objects.all()
    context = {
        "employees_list": all_employees 
    }
    return render(request, "employees.html", context)


@require_POST
def trolley_add(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    trolley_session = request.session.get("trolley", {})
    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    product_id_str = str(product.id)
    available_stock = product.count_in_stock or 0

    if product_id_str not in trolley_session:
        if quantity > available_stock:
            messages.error(
                request,
                f"Невозможно добавить {quantity} шт. товара '{product.name}'. В наличии только {available_stock} шт.",
            )
            return redirect(
                request.META.get("HTTP_REFERER", "Confectionary:showcase_all")
            )
        else:
            trolley_session[product_id_str] = quantity
            messages.success(
                request, f"Товар '{product.name}' ({quantity} шт.) добавлен в тележку."
            )
    else:
        if quantity > available_stock:
            messages.error(
                request,
                f"Невозможно установить количество {quantity} шт. для товара '{product.name}'. В наличии только {available_stock} шт.",
            )
            return redirect(
                request.META.get("HTTP_REFERER", "Confectionary:showcase_all")
            )
        else:
            trolley_session[product_id_str] = quantity
            messages.success(
                request,
                f"Количество товара '{product.name}' в тележке обновлено до {quantity} шт.",
            )

    request.session["trolley"] = trolley_session
    request.session.modified = True
    return redirect("Confectionary:trolley")


def trolley(request):
    trolley_session = request.session.get("trolley", {})
    trolley_items = []
    trolley_total_price = Decimal("0.00")

    product_ids = trolley_session.keys()
    products_in_trolley = Product.objects.filter(id__in=product_ids)
    products_dict = {str(p.id): p for p in products_in_trolley}
    items_to_remove = []

    for product_id, quantity in trolley_session.items():
        product = products_dict.get(product_id)
        if product:
            available_stock = product.count_in_stock or 0
            current_quantity = int(quantity)

            if current_quantity > available_stock:
                if available_stock > 0:
                    current_quantity = available_stock
                    trolley_session[product_id] = current_quantity
                    messages.warning(
                        request,
                        f"Количество товара '{product.name}' уменьшено до {available_stock} шт. (максимум на складе).",
                    )
                else:
                    items_to_remove.append(product_id)
                    messages.warning(
                        request,
                        f"Товар '{product.name}' закончился на складе и был удален из тележки.",
                    )
                    continue

            item_total = product.price * current_quantity
            trolley_items.append(
                {
                    "product": product,
                    "quantity": current_quantity,
                    "total_price": item_total,
                    "available_stock": available_stock,
                }
            )
            trolley_total_price += item_total
        else:
            items_to_remove.append(product_id)
            messages.warning(
                request,
                f"Товар с ID {product_id} больше не существует и был удален из тележки.",
            )

    if items_to_remove:
        for item_id in items_to_remove:
            if item_id in trolley_session:
                del trolley_session[item_id]
        request.session["trolley"] = trolley_session
        request.session.modified = True

    context = {
        "trolley_items": trolley_items,
        "trolley_total_price": trolley_total_price,
    }
    return render(request, "trolley.html", context)


@require_POST
def trolley_update(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    trolley_session = request.session.get("trolley", {})
    product_id_str = str(product.id)

    if product_id_str not in trolley_session:
        messages.error(request, "Товар не найден в тележке.")
        return redirect("Confectionary:trolley_view")

    try:
        quantity = int(request.POST.get("quantity"))
        if quantity < 1:
            del trolley_session[product_id_str]
            messages.success(request, f"Товар '{product.name}' удален из тележки.")
        else:
            available_stock = product.count_in_stock or 0
            if quantity > available_stock:
                messages.error(
                    request,
                    f"Невозможно установить количество {quantity} шт. Максимум на складе: {available_stock} шт.",
                )
            else:
                trolley_session[product_id_str] = quantity
                messages.success(
                    request, f"Количество товара '{product.name}' обновлено."
                )

    except (ValueError, TypeError):
        messages.error(request, "Некорректное количество.")

    request.session["trolley"] = trolley_session
    request.session.modified = True
    return redirect("Confectionary:trolley")


@require_POST
def trolley_remove(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    trolley_session = request.session.get("trolley", {})
    product_id_str = str(product.id)

    if product_id_str in trolley_session:
        del trolley_session[product_id_str]
        messages.success(request, f"Товар '{product.name}' удален из тележки.")
        request.session["trolley"] = trolley_session
        request.session.modified = True

    return redirect("Confectionary:trolley")


@login_required
def orders(request):
    customer = request.user.customer_profile
    user_orders = (
        Order.objects.filter(customer=customer)
        .prefetch_related("orderitem_set", "orderitem_set__product")
        .order_by("-order_date")
    )
    context = {"orders": user_orders}
    return render(request, "profile_pages/orders.html", context)


def checkout_view(request):
    trolley_session = request.session.get("trolley", {})
    if not trolley_session:
        messages.info(request, "Ваша тележка пуста. Нечего оформлять.")
        return redirect("Confectionary:trolley")

    trolley_items = []
    trolley_total_price = Decimal("0.00")
    product_ids = trolley_session.keys()
    products_in_trolley = Product.objects.filter(id__in=product_ids)
    products_dict = {str(p.id): p for p in products_in_trolley}
    has_error = False

    for product_id, quantity in list(trolley_session.items()):
        product = products_dict.get(product_id)
        if product:
            available_stock = product.count_in_stock or 0
            current_quantity = int(quantity)
            if current_quantity > available_stock:
                messages.error(
                    request,
                    f"Товар '{product.name}' закончился или его количество на складе ({available_stock}) меньше заказанного ({current_quantity}). Пожалуйста, обновите тележку.",
                )
                if available_stock > 0:
                    trolley_session[product_id] = available_stock
                else:
                    del trolley_session[product_id]
                request.session.modified = True
                has_error = True
                continue

            item_total = product.price * current_quantity
            trolley_items.append(
                {
                    "product": product,
                    "quantity": current_quantity,
                    "total_price": item_total,
                }
            )
            trolley_total_price += item_total
        else:
            messages.error(
                request,
                f"Товар с ID {product_id} больше не доступен и удален из корзины.",
            )
            if product_id in trolley_session:
                del trolley_session[product_id]
                request.session.modified = True
            has_error = True

    if has_error:
        return redirect("Confectionary:trolley")

    if not trolley_items:
        messages.info(request, "В вашей тележке не осталось доступных товаров.")
        return redirect("Confectionary:trolley")

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            customer, _ = Customer.objects.get_or_create(user=request.user)
            customer.phone = form.cleaned_data["phone"]
            customer.save()

            order = Order.objects.create(
                customer=customer,
                total_price=trolley_total_price,
                payment_method=form.cleaned_data["payment_method"],
                comment=form.cleaned_data["comment"],
            )
            for item_data in trolley_items:
                product = item_data["product"]
                quantity = item_data["quantity"]
                OrderItem.objects.create(
                    order=order, product=product, quantity=quantity, price=product.price
                )
                if product.count_in_stock is not None:
                    product.count_in_stock -= quantity
                    product.save(update_fields=["count_in_stock"])

            del request.session["trolley"]
            request.session.modified = True

            messages.success(
                request,
                f"Ваш заказ №{order.id} успешно оформлен! Мы скоро свяжемся с вами.",
            )
            return redirect("Confectionary:orders")

        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CheckoutForm(user=request.user)

    context = {
        "trolley_items": trolley_items,
        "trolley_total_price": trolley_total_price,
        "form": form,
    }
    return render(request, "checkout.html", context)
