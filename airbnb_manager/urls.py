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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from houses.decorators import admin_required
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Admin panel URL
    path('admin/', admin.site.urls),

    # Landing page route
    path('', login_required(views.landing_page), name='home'),  # Set the new landing page

    # List of houses
    path('houses/', login_required(views.houses), name='houses_list'),  # List all houses

    # House details route
    path('houses/<int:house_id>/', login_required(views.house_detail), name='details'),  # House details page

    # Routes for managing houses
    path('houses/add/', login_required(views.house_form), name='add_house'),  # Add house
    path('houses/edit/<int:house_id>/', login_required(views.house_form), name='edit_house'),  # Edit house
    path('houses/delete/<int:house_id>/', login_required(views.delete_house), name='delete_house'),  # Delete house

    # Utility expenses route
    path('utility-expenses/', login_required(views.add_utility_expenses), name='utility_expenses'),

    # Manage houses page
    path('houses/manage/', admin_required(views.manage_houses), name='manage_houses'),

    # Financial Overview Page
    path('houses/finance-overview/', login_required(views.financial_overview), name='financial_overview'),
    path('calculate-taxes/', login_required(views.calculate_taxes), name='calculate_taxes'),

    # Expense Overview Page (new path)
    path('houses/expense-overview/', login_required(views.expense_overview), name='expense_overview'),  # New route for expense overview
    #House Compare
    path('houses/house-compare/', login_required(views.house_compare), name='house_compare'),

    #Discounts
    # Discounts Page (Main View)
    path('houses/discounts/', login_required(views.discounts_page), name='discounts_page'),

    # Set a new discount
    path('houses/discounts/set/', login_required(views.set_discount), name='set_discount'),

    # Get discounted price (if needed elsewhere)
    path('houses/get_discounted_price/', views.get_discounted_price, name='get_discounted_price'),

    # Edit discount (opens a new form to update)
    path('houses/discounts/edit/<int:discount_id>/', views.edit_discount, name='edit_discount'),

    # Delete discount (handled via AJAX)
    path('houses/discounts/delete/<int:discount_id>/', views.delete_discount, name='delete_discount'),

    path('houses/get_discounted_price_for_day/', views.get_discounted_price_for_day, name='get_discounted_price_for_day'),

    path('export/csv/', views.export_to_csv, name='export_to_csv'),
    path('export/excel/', views.export_to_excel, name='export_to_excel'),
    path('generate_pdf_report/', views.generate_pdf_report, name='generate_pdf_report'),

    path('bookings/', views.booking_list, name='booking_list'),
    path('generate_invoice/<int:booking_id>/', views.generate_invoice, name='generate_invoice'),
    path('booking/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('booking/<int:booking_id>/add-note/', views.add_note, name='add_note'),

    path('houses/cleaning-fee/', views.edit_cleaning_fee, name='edit_cleaning_fee'),


    path('register/',views.register, name='register'),
    path('login/', views.login_view, name='login'),

    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

