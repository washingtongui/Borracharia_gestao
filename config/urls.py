# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include('gestaoClientes.urls')), # O "include" aponta para o app
]