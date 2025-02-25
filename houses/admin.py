from django.contrib import admin
from .models import House

# Customize how the houses are displayed in the admin panel
class HouseAdmin(admin.ModelAdmin):
    # Display the house name, address, and price in the list view
    list_display = ('name', 'address', 'price')

    # Add a search bar that allows searching by house name and address
    search_fields = ('name', 'address')

# Register the House model with the custom admin options
admin.site.register(House, HouseAdmin)
