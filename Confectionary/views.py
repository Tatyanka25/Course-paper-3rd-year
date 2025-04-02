from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from Confectionary.models import Category, Product, Customer
from .forms import CustomUserCreationForm, CustomCakeOrderForm, ProfileEditForm

CATEGORY_ICONS = {
    "Кофе": "img/coffee.png",
    "Чай": "img/tea.png",
    "Горячий шоколад": "img/chocolate.png",
    "Молочные коктейли": "img/milkshake.png",
    "Лимонады и освежающие напитки": "img/lemon.png",
}

employees_list = [
    {
        "name": "Илья",
        "role": "Бариста, мастер напитков",
        "experience": "5 лет работы с кофе, чаями и авторскими напитками.",
        "quote": "Настоящий напиток – это маленькая история, рассказанная вкусом.",
        "message": "Я убежден, что хороший напиток может сделать день лучше! Будь то насыщенный эспрессо, ароматный чай или освежающий лимонад – в Whisk & Wonder я подбираю вкусы так, чтобы каждый нашел свой идеальный вариант. Хочется чего-то необычного? Попробуйте наш фирменный малиновый молочный коктейль или цитрусовый чай с медом!",
        "about_work": "Каждое утро здесь начинается с запаха свежей выпечки, тепла капучино и улыбок гостей. Создавать атмосферу уюта и радовать людей вкусными напитками – вот что делает мою работу особенной!",
        "favorite_dessert": "Воздушный чизкейк с карамелью – тает во рту и идеально сочетается с любым напитком.",
        "favorite_drink": "Черничный лимонад – освежающий, с легкой кислинкой и ярким вкусом.",
        "image": "img/barista.jpg",
    },
    {
        "name": "Виктория",
        "role": "Кондитер, мастер десертов",
        "experience": "6 лет в кондитерском искусстве, специализация – авторские торты и французская выпечка.",
        "quote": "Настоящая магия начинается, когда простые ингредиенты превращаются в десерт, который вызывает улыбку.",
        "message": "Привет! Меня зовут Виктория, и я верю, что десерт – это не просто угощение, а целая история. В каждое пирожное, в каждый торт я вкладываю душу, чтобы создать для вас нечто особенное. Люблю экспериментировать с текстурами и вкусами – приходите, я уверена, что вы найдете здесь свой идеальный десерт!",
        "about_work": "Whisk & Wonder – это не просто место работы, это пространство творчества и вдохновения. Здесь ароматы свежей выпечки смешиваются с улыбками гостей, и каждый день хочется создавать что-то новое.",
        "favorite_dessert": "Шоколадный торт с малиной и крем-чизом – нежный, насыщенный и просто идеальный!",
        "favorite_drink": "Миндальное какао – согревает и делает день чуточку уютнее.",
        "image": "img/shef_victoria.jpg",
    },
    {
        "name": "Артем",
        "role": "Кондитер, специалист по пирожным",
        "experience": "4 года в ресторанной кондитерке, виртуозно готовит эклеры, капкейки и чизкейки.",
        "quote": "Идеальное пирожное – это когда с первого укуса понимаешь, что день удался.",
        "message": "Я обожаю готовить десерты, которые дарят радость с первого кусочка! В Whisk & Wonder вы найдете мои любимые сладости – от нежных макаронс до насыщенных шоколадных тартов. Если у вас есть любимый вкус – расскажите, возможно, он станет новым хитом нашего меню!",
        "about_work": "Работать здесь – значит каждый день радовать людей. Вдохновение приходит от улыбок гостей, когда они пробуют что-то новое и говорят: «Это потрясающе!».",
        "favorite_dessert": "Лимонный тарт – хрустящее тесто, шелковистый крем и легкая кислинка. Абсолютное совершенство!",
        "favorite_drink": "Фирменный латте с соленой карамелью – насыщенный, мягкий и идеально дополняющий десерты.",
        "image": "img/shef_artem.jpg",
    },
]

events = [
    {
        "title": "День открытых дверей",
        "description": """
        В нашем кондитерском царстве прошел День открытых дверей! Мы пригласили будущих студентов и всех желающих в мир сладких чудес. 
        В этот день гости смогли узнать все тонкости нашего ремесла, посмотреть на процесс создания кондитерских шедевров, 
        а также насладиться свежими угощениями, которые готовятся прямо на глазах. Мы рассказывали о наших курсах, проектах и планах на будущее. 
        Вдохновляющие встречи с единомышленниками, смех и, конечно же, сладости — этот день подарил массу приятных впечатлений!
        """,
        "images": [
            "img/events/open_day_1.jpg",
            "img/events/open_day_2.jpg",
            "img/events/open_day_3.jpg",
            "img/events/open_day_4.jpg",
            "img/events/open_day_5.jpg",
        ],
    },
    {
        "title": "Мастер-класс по выпечке",
        "description": """
        Наши гости окунулись в магию кондитерского искусства на мастер-классе по выпечке. Здесь каждый стал кондитером: мы делились секретами 
        приготовления воздушного бисквита, идеальных кремов и декора. Под чутким руководством нашего шеф-кондитера участники 
        научились работать с тестом и создавать сладкие шедевры. Этот мастер-класс стал не только полезным, но и невероятно увлекательным, 
        ведь у каждого была возможность не только узнать новые техники, но и насладиться вкусом собственноручно приготовленных десертов.
        """,
        "images": [
            "img/events/masterclass_1.jpg",
            "img/events/masterclass_2.jpg",
            "img/events/masterclass_3.jpg",
            "img/events/masterclass_4.jpg",
            "img/events/masterclass_5.jpg",
            "img/events/masterclass_6.jpg",
        ],
    },
    {
        "title": "Новогодний вечер в Whisk & Wonder",
        "description": """
        В нашем уютном уголке прошел незабываемый новогодний вечер, наполненный волшебством, ароматами свежих имбирных печений и 
        горячего какао. Мы встретили Новый год в компании друзей, коллег и, конечно, наших гостей. В этот вечер мы устроили праздничный ужин, 
        где каждому было предложено попробовать новогодние угощения, уникальные для этой зимней поры. Песни, смех, сказочные украшения и 
        атмосфера праздника сделали этот вечер по-настоящему волшебным. Пусть каждый момент этого вечера останется в памяти, как самый 
        теплый и радостный момент уходящего года.
        """,
        "images": [
            "img/events/new_year_1.jpg",
            "img/events/new_year_2.jpg",
            "img/events/new_year_3.jpg",
            "img/events/new_year_4.jpg",
            "img/events/new_year_5.jpg",
        ],
    },
]

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
        profile_form = ProfileEditForm(
            request.POST, instance=customer_profile
        ) 
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Профиль успешно обновлен.")
            return redirect("Confectionary:profile")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        profile_form = ProfileEditForm(instance=customer_profile) 

    context = {
        "user": request.user,
        "customer": customer_profile,
        "profile_form": profile_form, 
    }
    print(profile_form)
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


def showcase(request):
    selected_type = request.GET.get("type", "")
    dessert_products = Product.objects.none() 
    product_types = [] 

    try:
        dessert_category = Category.objects.get(name__iexact="Десерты")

        base_in_stock_desserts = Product.objects.filter(
            category=dessert_category,
            count_in_stock__gt=0  
        )

        product_types = base_in_stock_desserts.exclude(
            type__isnull=True 
        ).exclude(
            type__exact=""     
        ).values_list(
            "type", flat=True
        ).distinct().order_by('type') 

        if selected_type:
            dessert_products = base_in_stock_desserts.filter(type=selected_type)
        else:
            dessert_products = base_in_stock_desserts

    except Category.DoesNotExist:
        pass 

    context = {
        "product_types": product_types,
        "products": dessert_products,
        "selected_type": selected_type,
    }

    return render(request, "showcase.html", context)


def photo_album(request):
    context = {"events": events}
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
            return redirect(
                "Confectionary:custom_cakes"
            ) 
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
    context = {"employees_list": employees_list}
    return render(request, "employees.html", context)


def trolley(request):
    return render(request, "trolley.html")


def profile(request):
    return render(request, "profile_pages/profile.html")


def orders(request):
    return render(request, "profile_pages/orders.html")
