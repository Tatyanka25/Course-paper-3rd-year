from django.contrib import admin

from .models import (
    Customer,
    Category,
    Product,
    Order,
    OrderItem,
    Review,
    Payment,
    CustomCakeOrder,
    Employee,
    Event,
    EventImage
)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "phone")
    search_fields = ("user__username", "phone")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "slug")
    search_fields = ("name",)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "quantity",
        "count_in_stock",
        "is_popular",
        "type",
        "type_slug",
        "slug"
    )
    list_filter = ("category", "is_popular", "type")
    search_fields = ("name", "description", "short_description")
    list_editable = ("price", "quantity", "count_in_stock", "is_popular")
    prepopulated_fields = {'slug': ('name',), 'type_slug': ('type',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ("price",)
    autocomplete_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "order_date", "total_price", "status")
    list_editable = ("status",)
    list_filter = ("status", "order_date")
    search_fields = ("id", "customer__user__username", "status")
    readonly_fields = ("order_date", "total_price")
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "customer", "rating", "date")
    list_filter = ("rating", "date")
    search_fields = ("product__name", "customer__user__username", "comment")
    readonly_fields = ("date",)
    autocomplete_fields = ["product", "customer"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "payment_date", "amount", "method")
    list_filter = ("method", "payment_date")
    search_fields = ("order__id", "method")
    readonly_fields = ("payment_date",)
    autocomplete_fields = ["order"]


@admin.register(CustomCakeOrder)
class CustomCakeOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "phone_number",
        "filling",
        "weight",
        "event_date",
        "delivery_method",
        "created_at",
    )
    list_filter = (
        "filling",
        "weight",
        "event_date",
        "social_media",
        "delivery_method",
        "created_at",
    )
    search_fields = ("first_name", "last_name", "phone_number", "filling")
    readonly_fields = ("created_at",)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'favorite_dessert', 'favorite_drink')
    list_filter = ('role',)
    search_fields = ('name', 'role', 'quote', 'message', 'about_work')
    fieldsets = (
        (None, {
            'fields': ('name', 'role', 'image_path')
        }),
        ('Профессиональная информация', {
            'fields': ('experience', 'quote', 'message', 'about_work')
        }),
        ('Предпочтения', {
            'fields': ('favorite_dessert', 'favorite_drink')
        }),
    )

class EventImageInline(admin.TabularInline): 
    model = EventImage
    extra = 1 

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description')
    search_fields = ('title', 'description')
    inlines = [EventImageInline] 

    def short_description(self, obj):
        """Создает короткое описание для отображения в списке."""
        if obj.description and len(obj.description) > 75:
            return obj.description[:75] + '...'
        return obj.description
    short_description.short_description = 'Краткое описание'