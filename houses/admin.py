from django.contrib import admin
from .models import House, Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('get_house_name', 'customer_name', 'start_date', 'end_date')  # Adjusted fields

    def get_house_name(self, obj):
        return obj.house.name  # Get the house name from the related House model

    get_house_name.admin_order_field = 'house'  # Allows sorting by house
    get_house_name.short_description = 'House Name'  # Short label for the admin interface

admin.site.register(House)
admin.site.register(Booking, BookingAdmin)
