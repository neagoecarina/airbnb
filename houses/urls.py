# houses/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Page showing all houses
    path('houses/', views.houses, name='houses_list'),

    # Page showing details for a single house
    path('houses/<int:house_id>/', views.house_detail, name='details'),

    # Page to manage houses
    path('houses/manage/', views.manage_houses, name='manage_houses'),  # Manage houses page

    # Add, edit, and delete house paths
    path('houses/add/', views.house_form, name='add_house'),  # Add a new house
    path('houses/edit/<int:house_id>/', views.house_form, name='edit_house'),  # Rename to house_id
    path('houses/delete/<int:house_id>/', views.delete_house, name='delete_house'),  # Rename to house_id
]
]