import re
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomCakeOrder, Customer, Product, Category


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Адрес электронной почты",
        help_text="Обязательное поле. Введите действительный адрес электронной почты.",
    )
    first_name = forms.CharField(
        max_length=30, required=True, label="Имя", help_text="Обязательное поле."
    )
    last_name = forms.CharField(
        max_length=150, required=True, label="Фамилия", help_text="Обязательное поле."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
        )
        labels = {
            "username": "Логин",
        }
        help_texts = {
            "username": "Обязательное поле. Не более 150 символов. Разрешены буквы, цифры и символы @/./+/-/_.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["password1"].help_text = (
            "Ваш пароль не должен быть слишком похож на другие ваши персональные данные.<br>"
            "Ваш пароль должен содержать не менее 8 символов.<br>"
            "Ваш пароль не может быть обычным паролем.<br>"
            "Ваш пароль не может быть полностью цифровым."
        )
        self.fields["password2"].help_text = (
            "Введите тот же пароль, что и раньше, для подтверждения."
        )
        for field_name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
            if "password" in field_name:
                field.widget = forms.PasswordInput(attrs=field.widget.attrs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Этот адрес электронной почты уже используется."
            )
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            if not first_name[0].isupper():
                raise forms.ValidationError("Имя должно начинаться с заглавной буквы.")
            if not re.fullmatch(r"^[А-Яа-яЁё\-]+$", first_name):
                raise forms.ValidationError(
                    "Имя может содержать только русские буквы и дефис."
                )
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            if not last_name[0].isupper():
                raise forms.ValidationError(
                    "Фамилия должна начинаться с заглавной буквы."
                )
            if not re.fullmatch(r"^[А-Яа-яЁё\-]+$", last_name):
                raise forms.ValidationError(
                    "Фамилия может содержать только русские буквы и дефис."
                )
        return last_name


class CustomAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Имя пользователя (логин)"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Пароль"}
        )

        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"


class CustomCakeOrderForm(forms.ModelForm):
    class Meta:
        model = CustomCakeOrder
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "filling",
            "weight",
            "event_date",
            "social_media",
            "delivery_method",
        ]
        widgets = {
            "filling": forms.RadioSelect,
            "social_media": forms.RadioSelect,
            "delivery_method": forms.RadioSelect,
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "phone_number": forms.TextInput(attrs={"type": "tel"}),
            "weight": forms.NumberInput(attrs={"step": "0.1", "min": "2"}),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        try:
            cake_category = Category.objects.get(name="Торты")
            cakes = Product.objects.filter(category=cake_category)
            filling_choices = [(cake.name, cake.name) for cake in cakes]
            self.fields["filling"].choices = filling_choices
            self.fields["filling"].widget = forms.RadioSelect(choices=filling_choices)

        except (Category.DoesNotExist, Product.DoesNotExist):
            self.fields["filling"].choices = []
            self.fields["filling"].widget = forms.RadioSelect(choices=[])

        placeholders = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone_number": "+7 123 456 78 90",
            "weight": "2",
            "event_date": "",
        }

        for field_name, field in self.fields.items():
            if field_name in placeholders and hasattr(field.widget, "attrs"):
                field.widget.attrs["placeholder"] = placeholders[field_name]

            if field_name not in ["filling", "social_media", "delivery_method"]:
                if hasattr(field.widget, "attrs"):
                    current_class = field.widget.attrs.get("class", "")
                    if "form-control" not in current_class.split():
                        field.widget.attrs["class"] = (
                            current_class + " form-control"
                        ).strip()

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            if not first_name[0].isupper():
                raise forms.ValidationError("Имя должно начинаться с заглавной буквы.")
            if not re.fullmatch(r"^[А-Яа-яЁё\-]+$", first_name):
                raise forms.ValidationError(
                    "Имя может содержать только русские буквы и дефис."
                )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            if not last_name[0].isupper():
                raise forms.ValidationError(
                    "Фамилия должна начинаться с заглавной буквы."
                )
            if not re.fullmatch(r"^[А-Яа-яЁё\-]+$", last_name):
                raise forms.ValidationError(
                    "Фамилия может содержать только русские буквы и дефис."
                )
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number:
            cleaned_phone = re.sub(r"[ \-\(\)]", "", phone_number)

            if cleaned_phone.startswith("+7"):
                if len(cleaned_phone) != 12 or not cleaned_phone[1:].isdigit():
                    raise forms.ValidationError(
                        "Неверный формат номера. После '+7' должно идти 10 цифр."
                    )
            elif cleaned_phone.startswith("8"):
                if len(cleaned_phone) != 11 or not cleaned_phone[1:].isdigit():
                    raise forms.ValidationError(
                        "Неверный формат номера. После '8' должно идти 10 цифр."
                    )
            else:
                raise forms.ValidationError(
                    "Номер телефона должен начинаться с '+7' или '8'."
                )

            return cleaned_phone
        return phone_number

    def clean_event_date(self):
        event_date = self.cleaned_data.get("event_date")
        if event_date:
            today = date.today()
            min_allowed_date = today + timedelta(days=2)
            if event_date < min_allowed_date:
                min_date_str = min_allowed_date.strftime("%d.%m.%Y")
                raise forms.ValidationError(
                    f"Дата мероприятия должна быть не ранее {min_date_str}."
                )
        return event_date


class CheckoutForm(forms.Form):
    phone = forms.CharField(
        label="Контактный телефон",
        widget=forms.TextInput(attrs={"class": "form-control", "type": "tel"}),
        required=True,
    )
    PAYMENT_CHOICES = [
        ("cash", "Наличными при получении"),
        ("card_on_delivery", "Картой при получении"),
    ]
    payment_method = forms.ChoiceField(
        label="Способ оплаты",
        choices=PAYMENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )
    comment = forms.CharField(
        label="Комментарий к заказу (необязательно)",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            customer_profile = getattr(user, "customer_profile", None)
            if customer_profile:
                if not self.initial.get("phone") and customer_profile.phone:
                    self.initial["phone"] = customer_profile.phone

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            cleaned_phone = re.sub(r"[ \-\(\)]", "", phone)

            if cleaned_phone.startswith("+7"):
                if len(cleaned_phone) != 12 or not cleaned_phone[1:].isdigit():
                    raise forms.ValidationError(
                        "Неверный формат номера. После '+7' должно идти 10 цифр."
                    )
            elif cleaned_phone.startswith("8"):
                if len(cleaned_phone) != 11 or not cleaned_phone[1:].isdigit():
                    raise forms.ValidationError(
                        "Неверный формат номера. После '8' должно идти 10 цифр."
                    )
            else:
                raise forms.ValidationError(
                    "Номер телефона должен начинаться с '+7' или '8'."
                )

            return cleaned_phone
        return phone

    def save(self, user):
        customer = Customer.objects.get_or_create(user=user)
        customer.phone = self.cleaned_data["phone"]
        customer.save()
        return customer

class ProfileEditForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=True, 
        label="Имя",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True, 
        label="Фамилия",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True, 
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Пожалуйста, введите ваш email.',
            'invalid': 'Пожалуйста, введите корректный адрес электронной почты.', 
        }
    )
    phone = forms.CharField(
        max_length=20,
        required=False, 
        label="Телефон",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7XXXXXXXXXX'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
             return None
        
        email = email.lower()
        if self.user and User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
             raise forms.ValidationError("Этот email уже используется другим пользователем.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            cleaned_phone = re.sub(r"[ \-\(\)]", "", phone)

            if cleaned_phone.startswith("+7"):
                if len(cleaned_phone) != 12 or not cleaned_phone[1:].isdigit():
                    raise forms.ValidationError(
                        "Неверный формат номера. После '+7' должно идти 10 цифр."
                    )
            elif cleaned_phone.startswith("8"):
                if len(cleaned_phone) != 11 or not cleaned_phone[1:].isdigit():
                    raise forms.ValidationError(
                        "Неверный формат номера. После '8' должно идти 10 цифр."
                    )
            else:
                raise forms.ValidationError(
                    "Номер телефона должен начинаться с '+7' или '8'."
                )

            return cleaned_phone
        return phone
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            if not first_name[0].isupper():
                raise forms.ValidationError("Имя должно начинаться с заглавной буквы.")
            if not re.fullmatch(r"^[А-Яа-яЁё\-]+$", first_name):
                raise forms.ValidationError(
                    "Имя может содержать только русские буквы и дефис."
                )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            if not last_name[0].isupper():
                raise forms.ValidationError(
                    "Фамилия должна начинаться с заглавной буквы."
                )
            if not re.fullmatch(r"^[А-Яа-яЁё\-]+$", last_name):
                raise forms.ValidationError(
                    "Фамилия может содержать только русские буквы и дефис."
                )
        return last_name