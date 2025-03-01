from django.contrib import admin
from .models import House
from .models import Booking, MonthlyEarning, UtilityExpense, YearlyEarning, HouseEarning

# Customize how the houses are displayed in the admin panel
class HouseAdmin(admin.ModelAdmin):
    # Display the house name, address, and price in the list view
    list_display = ('name', 'address', 'price')

    # Add a search bar that allows searching by house name and address
    search_fields = ('name', 'address')

# Customize how the houses are displayed in the admin panel
class BookingAdmin(admin.ModelAdmin):
    # Display the house name, address, and price in the list view
    list_display = ('house', 'start_date','end_date' ,'customer_name','booking_earnings')

  # Add a search bar that allows searching by house name, address, and customer name
    search_fields = ['house__name', 'house__address', 'customer_name']  # Use double underscore to access related model fields


@admin.register(MonthlyEarning)
class MonthlyEarningEarningAdmin(admin.ModelAdmin):
    list_display = ('month_name', 'total_earnings')  # Display month and total earnings
    search_fields = ('month_name',)  # Allow search by month name
    list_filter = ('month_name',)  # Filter by month name

# Register the House model with the custom admin options
admin.site.register(House, HouseAdmin)
admin.site.register(Booking, BookingAdmin)


@admin.register(UtilityExpense)
class UtilityExpenseAdmin(admin.ModelAdmin):
    list_display = ('house', 'month', 'year', 'water_expense', 'electricity_expense', 'total_expense')
    list_filter = ('month', 'year', 'house')
    search_fields = ('house__name',) 

@admin.register(YearlyEarning)
class YearlyEarningAdmin(admin.ModelAdmin):
    list_display = ('year', 'total_earnings')  # Display year and total earnings
    search_fields = ('year',)  # Allow search by year
    list_filter = ('year',)  # Filter by year

@admin.register(HouseEarning)
class HouseEarningAdmin(admin.ModelAdmin):
    list_display = ('house', 'month', 'total_price')  # Display house, month, and total price
    search_fields = ('house__name', 'month')  # Allow search by house name and month
    list_filter = ('month', 'house')  # Filter by month and house
    ordering = ('-month',)  # Order by month in descending order