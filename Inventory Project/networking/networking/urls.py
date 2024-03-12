# networking/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('ups.urls')),  # Set the login page as the default
    path('admin/', admin.site.urls),
]
