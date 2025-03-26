from django.shortcuts import render
from Confectionary.models import Category, Product

CATEGORY_ICONS = {
    "Кофе": "img/coffee.png",
    "Чай": "img/tea.png",
    "Горячий шоколад": "img/chocolate.png",
    "Молочные коктейли": "img/milkshake.png",
    "Лимонады и освежающие напитки": "img/lemon.png",
}


def main_page(request):
    category_names = CATEGORY_ICONS.keys()
    categories = Category.objects.prefetch_related("products").filter(
        name__in=category_names
    )
    for category in categories:
        category.icon = CATEGORY_ICONS.get(category.name, "img/default_icon.png")

    popular_products = Product.objects.filter(is_popular=True)

    return render(
        request,
        "main_page.html",
        {"categories": categories, "popular_products": popular_products},
    )


def showcase(request):
    selected_type = request.GET.get("type", "")
    dessert_category = Category.objects.get(name="Десерты")
    dessert_products = (
        Product.objects.filter(category=dessert_category)
        if dessert_category
        else Product.objects.none()
    )
    if selected_type:
        dessert_products = dessert_products.filter(type=selected_type)
    product_types = (
        Product.objects.filter(category=dessert_category)
        .exclude(type__isnull=True)
        .exclude(type__exact="")
        .values_list("type", flat=True)
        .distinct()
        if dessert_category
        else []
    )

    return render(
        request,
        "showcase.html",
        {
            "product_types": product_types,
            "products": dessert_products,
            "selected_type": selected_type,
        },
    )


def photo_album(request):
    return render(request, "photo_album.html")


def custom_cakes(request):
    return render(request, "custom_cakes.html")


def delivery(request):
    return render(request, "delivery.html")


def employees(request):
    return render(request, "employees.html")


def trolley(request):
    return render(request, "trolley.html")


def profile(request):
    return render(request, "profile.html")
