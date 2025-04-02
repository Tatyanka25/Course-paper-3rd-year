from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Customer(models.Model):
    # Связь один-к-одному с моделью User
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_profile", null=True
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Customer Profile for: {self.user.username}"


@receiver(post_save, sender=User)
def create_user_customer(_sender, instance, created, **_kwargs):
    if created:
        Customer.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_customer(_sender, instance, **_kwargs):
    if hasattr(instance, "customer_profile"):
        instance.customer_profile.save()
    else:
        Customer.objects.create(user=instance)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"Category: {self.name}"


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
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    count_in_stock = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Количество на складе (шт.)"
    )

    def __str__(self):
        return f"Product: {self.name}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        customer_name = "Unknown Customer"
        if self.customer and self.customer.user:
            customer_name = self.customer.user.username
        order_id = getattr(self, "id", "Unsaved")
        return f"Order {order_id} by {customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

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
