from django.contrib import admin
from .models import House
from .models import Booking

# Customize how the houses are displayed in the admin panel
class HouseAdmin(admin.ModelAdmin):
    # Display the house name, address, and price in the list view
    list_display = ('name', 'address', 'price')

    # Add a search bar that allows searching by house name and address
    search_fields = ('name', 'address')

# Customize how the houses are displayed in the admin panel
class BookingAdmin(admin.ModelAdmin):
    # Display the house name, address, and price in the list view
    list_display = ('house', 'start_date','end_date' ,'customer_name')

  # Add a search bar that allows searching by house name, address, and customer name
    search_fields = ['house__name', 'house__address', 'customer_name']  # Use double underscore to access related model fields


# Register the House model with the custom admin options
admin.site.register(House, HouseAdmin)
admin.site.register(Booking, BookingAdmin)
