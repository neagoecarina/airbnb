# houses/urls.py

from django.urls import path
from . import views
from .views import register, login_view
from django.contrib.auth.views import LogoutView


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

     # Financial Overview Page
    path('houses/finance-overview/', views.financial_overview, name='financial_overview'),
    path('calculate-taxes/', views.calculate_taxes, name='calculate_taxes'),

    path('houses/expense-overview/', views.expense_overview, name='expense_overview'),

    #House Compare
    path('houses/house-compare/', views.house_compare, name='house_compare'),

    path('bookings/', views.booking_list, name='booking_list'),
    path('generate_invoice/<int:booking_id>/', views.generate_invoice, name='generate_invoice'),
    path('booking/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('booking/<int:booking_id>/add-note/', views.add_note, name='add_note'),
    #Discounts

     # Discounts Page (Main View)
    path('houses/discounts/', views.discounts_page, name='discounts_page'),

    # Set a new discount
    path('houses/discounts/set/', views.set_discount, name='set_discount'),

    # Get discounted price (if needed elsewhere)
    path('houses/get_discounted_price/', views.get_discounted_price, name='get_discounted_price'),

    # Edit discount (opens a new form to update)
    path('houses/discounts/edit/<int:discount_id>/', views.edit_discount, name='edit_discount'),

    # Delete discount (handled via AJAX)
    path('houses/discounts/delete/<int:discount_id>/', views.delete_discount, name='delete_discount'),
    
    path('houses/cleaning-fee/', views.edit_cleaning_fee, name='edit_cleaning_fee'),

    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/login', http_method_names=['get', 'post']), name='logout'),

]

