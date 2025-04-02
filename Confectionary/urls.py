from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

app_name = "Confectionary"

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("main_page/", views.main_page, name="main_page"),
    path("showcase/", views.showcase, name="showcase"),
    path("photo_album/", views.photo_album, name="photo_album"),
    path("custom_cakes/", views.custom_cakes, name="custom_cakes"),
    path("delivery/", views.delivery, name="delivery"),
    path("employees/", views.employees, name="employees"),
    path("trolley/", views.trolley, name="trolley"),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='Confectionary:main_page'), name='logout'),
    path("profile/", views.profile, name="profile"),
    path("orders/", views.orders, name="orders"),
]
