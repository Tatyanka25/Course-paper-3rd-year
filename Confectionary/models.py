from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.name}"


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
    quantity = models.DecimalField(
        max_digits=10, decimal_places=0
    )  # количество в мл или г
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    is_popular = models.BooleanField(default=False) 
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Product: {self.name}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Order {getattr(self, 'id', 'Unknown')} by {self.customer.name}"


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
        return f"Review for {self.product.name} by {self.customer.name}"


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)

    def __str__(self):
        return f"Payment for Order {self.order.id}"
