from django.shortcuts import render

def main_page(request):
    return render(request, 'main_page.html')

def showcase(request):
    return render(request, 'showcase.html')

def photo_album(request):
    return render(request, 'photo_album.html')

def custom_cakes(request):
    return render(request, 'custom_cakes.html')

def delivery(request):
    return render(request, 'delivery.html')

def employees(request):
    return render(request, 'employees.html')

def trolley(request):
    return render(request, 'trolley.html')

def profile(request):
    return render(request, 'profile.html')

