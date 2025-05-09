from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_profile", null=True
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Customer Profile for: {self.user.username}"


@receiver(post_save, sender=User)
def create_user_customer(sender, instance, created, **_kwargs):
    if created:
        Customer.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_customer(sender, instance, **_kwargs):
    if hasattr(instance, "customer_profile"):
        instance.customer_profile.save()
    else:
        Customer.objects.create(user=instance)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=110, unique=True, db_index=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                object_id_part = str(self.id) if self.id else "temp-category"
                base_slug = f"category-{object_id_part}"
            slug = base_slug
            counter = 1
            queryset = Category.objects.all()
            if self.id:
                queryset = queryset.exclude(id=self.id)
            while queryset.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Category: {self.name}"

    def get_absolute_url(self):
        return reverse(
            "Confectionary:category_product", kwargs={"category_slug": self.slug}
        )


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    short_description = models.TextField(default="Описание отсутствует")
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.DecimalField(max_digits=10, decimal_places=0)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    is_popular = models.BooleanField(default=False)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    count_in_stock = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Количество на складе (шт.)"
    )
    slug = models.SlugField(max_length=265, unique=True, db_index=True, blank=True)
    type_slug = models.SlugField(
        max_length=110, db_index=True, blank=True, null=True, unique=False
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                object_id_part = str(self.id) if self.id else "temp-product"
                base_slug = f"product-{object_id_part}"
            slug = base_slug
            counter = 1
            queryset = Product.objects.all()
            if self.id:
                queryset = queryset.exclude(id=self.id)
            while queryset.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if self.type and not self.type_slug:
            self.type_slug = slugify(self.type)
        elif not self.type:
            self.type_slug = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Product: {self.name}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "В ожидании"),
        ("processing", "В обработке"),
        ("ready", "Готов к выдаче"),
        ("received", "Получен"),
        ("cancelled", "Отменен"),
    )
    PAYMENT_CHOICES = [
        ("cash", "Наличными при получении"),
        ("card_on_delivery", "Картой при получении"),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_CHOICES, default="card_on_delivery"
    )
    comment = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        ordering = ("-order_date",)

    def __str__(self):
        customer_name = "Unknown Customer"
        if self.customer and self.customer.user:
            customer_name = self.customer.user.username
        order_id = getattr(self, "id", "Unsaved")
        return f"Заказ {order_id} от {customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_cost(self):
        if self.price is not None:
            return (Decimal(self.price) * self.quantity).quantize(Decimal("0.01"))
        return Decimal("0.00")

    def __str__(self):
        return str(self.id)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        customer_name = "Unknown Customer"
        product_name = "Unknown Product"
        if self.customer and self.customer.user:
            customer_name = self.customer.user.username
        if self.product:
            product_name = self.product.name

        return f"Review for {product_name} by {customer_name}"


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment for Order {self.order.id}"


class CustomCakeOrder(models.Model):
    SOCIAL_MEDIA_CHOICES = [
        ("WhatsApp", "WhatsApp"),
        ("Telegram", "Telegram"),
    ]

    DELIVERY_CHOICES = [
        ("Самовывоз", "Самовывоз"),
        ("Доставка по городу", "Доставка по городу"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    filling = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=10, decimal_places=1)
    event_date = models.DateField()
    social_media = models.CharField(
        max_length=20, choices=SOCIAL_MEDIA_CHOICES, default=SOCIAL_MEDIA_CHOICES
    )
    delivery_method = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES, default=DELIVERY_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id}: {self.first_name} {self.last_name} - {self.filling}, {self.weight} кг"


class Employee(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    role = models.CharField(max_length=150, verbose_name="Должность")
    experience = models.TextField(verbose_name="Опыт")
    quote = models.TextField(verbose_name="Цитата")
    message = models.TextField(verbose_name="Сообщение от сотрудника")
    about_work = models.TextField(verbose_name="О работе в Whisk & Wonder")
    favorite_dessert = models.CharField(max_length=255, verbose_name="Любимый десерт")
    favorite_drink = models.CharField(max_length=255, verbose_name="Любимый напиток")
    image_path = models.CharField(
        max_length=255,
        verbose_name="Путь к изображению (static)",
        help_text="Пример: img/barista.jpg",
    )

    def __str__(self):
        return f"{self.name} - {self.role}"

class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название мероприятия")
    description = models.TextField(verbose_name="Описание мероприятия")
    event_date = models.DateField(verbose_name="Дата мероприятия", help_text="Укажите дату проведения мероприятия")

    def __str__(self):
        return self.title
    
class EventImage(models.Model):
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE, verbose_name="Мероприятие")
    image_path = models.CharField(max_length=255, verbose_name="Путь к изображению (static)", help_text="Пример: img/events/open_day_1.jpg")

    def __str__(self):
        return self.image_path