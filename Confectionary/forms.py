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


class ProfileEditForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        label="Телефон",
        widget=forms.TextInput(attrs={"class": "form-control", "type": "tel"}),
    )
    address = forms.CharField(
        required=False,
        label="Адрес",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Адрес электронной почты",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_instance = self.instance

        if user_instance and hasattr(user_instance, "customer_profile"):
            customer_profile = user_instance.customer_profile
            self.initial["phone"] = customer_profile.phone
            self.initial["address"] = customer_profile.address
        else:
            self.initial["phone"] = ""
            self.initial["address"] = ""

        original_email = user_instance.email if user_instance else None
        self.fields["email"].validators = [
            v
            for v in self.fields["email"].validators
            if not isinstance(v, ValidationError)
        ]
        self.fields["email"].validators.append(
            lambda email: self.validate_unique_email(email, original_email)
        )

    def validate_unique_email(self, email, original_email):
        if email != original_email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "Этот адрес электронной почты уже используется другим пользователем."
                )

    def save(self, commit=True):
        user = super().save(commit=commit)
        try:
            customer_profile = user.customer_profile
        except Customer.DoesNotExist:
            customer_profile = Customer.objects.create(user=user)

        customer_profile.phone = self.cleaned_data["phone"]
        customer_profile.address = self.cleaned_data["address"]

        if commit:
            customer_profile.save()

        return user


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
