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
    categories = Category.objects.prefetch_related("products").filter(name__in=category_names)
    for category in categories:
        category.icon = CATEGORY_ICONS.get(
            category.name, "img/default_icon.png"
        )  

    popular_products = Product.objects.filter(is_popular=True)

    return render(request, "main_page.html", {"categories": categories, "popular_products": popular_products})


def showcase(request):
    return render(request, "showcase.html")


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
