"""
URL configuration for airbnb_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# airbnb_manager/urls.py
# airbnb_manager/urls.py

from django.contrib import admin
from django.urls import path
from houses import views  # Make sure to import the views from the 'houses' app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.houses, name='home'),  # The homepage for all houses
    path('houses/', views.houses, name='houses_list'),  # List of houses
    path('houses/<int:house_id>/', views.house_detail, name='details'),  # House details page
]