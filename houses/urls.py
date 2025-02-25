# houses/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('houses/', views.houses, name='houses_list'),  # Page showing all houses
    path('houses/<int:house_id>/', views.house_detail, name='details'),  # Page showing details for a single house
]
