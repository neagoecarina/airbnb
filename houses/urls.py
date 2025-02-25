from django.urls import path
from . import views

urlpatterns = [
    path('', views.houses, name='all_houses'),  # URL for viewing all houses
    path('details/<int:id>/', views.details, name='house_details'),  # URL for house details
]
