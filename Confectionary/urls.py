#from django.contrib import admin
from django.urls import path

from . import views

app_name = "Confectionary"

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('main_page/', views.main_page, name='main_page'),
    path('showcase/', views.showcase, name='showcase'),
    path('photo_album/', views.photo_album, name='photo_album'),
    path('custom_cakes/', views.custom_cakes, name='custom_cakes'),
    path('delivery/', views.delivery, name='delivery'),
    path('employees/', views.employees, name='employees'),
    path('trolley/', views.trolley, name='trolley'),
    path('profile/', views.profile, name='profile'),
]
