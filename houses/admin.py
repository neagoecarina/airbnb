from django.contrib import admin
from .models import House
from .models import Booking, MonthlyEarning, UtilityExpense, YearlyEarning, HouseEarning, BookingExpense, MonthlyExpense
from decimal import Decimal

# BookingExpense inline
class BookingExpenseInline(admin.TabularInline):
    model = BookingExpense
    extra = 0  # Do not show extra empty forms


from django.contrib import admin
from django.utils.html import mark_safe
from .models import House

# Check if the model is already registered
if not admin.site.is_registered(House):
    class HouseAdmin(admin.ModelAdmin):
        # Display the house name, address, price, and photo preview in the list view
        list_display = ('name', 'address', 'price', 'image_preview')

        # Add a search bar that allows searching by house name and address
        search_fields = ('name', 'address')

        # Add image preview functionality
        def image_preview(self, obj):
            if obj.photo:  # Check if the house has a photo
                return mark_safe(f'<img src="{obj.photo.url}" width="50" height="50" />')
            return 'No image'  # Return a default text if there is no photo
        image_preview.short_description = 'Image Preview'  # Name of the column for image preview

    # Register the House model and its admin customization
    admin.site.register(House, HouseAdmin)




class BookingAdmin(admin.ModelAdmin):
    list_display = ('house', 'start_date', 'end_date', 'customer_name', 'booking_earnings', 'booking_price_with_vat', 'vat_amount')
    
    search_fields = ['house__name', 'house__address', 'customer_name']  

    inlines = [BookingExpenseInline]

    # Calculate price with VAT (total amount including VAT)
    def booking_price_with_vat(self, obj):
        if obj.booking_earnings:  # Ensure earnings exist
            return round(obj.booking_earnings * Decimal('1.19'), 2)  # ✅ Convert 1.19 to Decimal
        return None  # Return None if no earnings

    booking_price_with_vat.short_description = "Total Price (incl. 19% VAT)"

    # Calculate VAT amount separately
    def vat_amount(self, obj):
        if obj.booking_earnings:  # Ensure earnings exist
            return round(obj.booking_earnings * Decimal('0.19'), 2)  # ✅ Convert 0.19 to Decimal
        return None

    vat_amount.short_description = "VAT (19%)"



@admin.register(MonthlyEarning)
class MonthlyEarningEarningAdmin(admin.ModelAdmin):
    list_display = ('month_name', 'total_earnings', 'total_earnings_with_vat')  # Display month and total earnings
    search_fields = ('month_name',)  # Allow search by month name
    list_filter = ('month_name',)  # Filter by month name


admin.site.register(Booking, BookingAdmin)


from django.contrib import admin
from decimal import Decimal
from .models import UtilityExpense

@admin.register(UtilityExpense)
class UtilityExpenseAdmin(admin.ModelAdmin):
    # Adjust list_display to use 'date' instead of 'month' and 'year'
    list_display = ('house', 'date', 'water_expense', 'electricity_expense', 'total_expense', 'vat_deductible')
    list_filter = ('date', 'house')  # You can filter by 'date' directly now
    search_fields = ('house__name',)

    # Calculate the VAT deductible amount (19% of the total expense)
    def vat_deductible(self, obj):
        if obj.total_expense:  # Ensure total_expense exists
            return round(obj.total_expense * Decimal('0.19'), 2)  # ✅ Convert 0.19 to Decimal
        return None

    vat_deductible.short_description = "VAT Deductible (19%)"


@admin.register(YearlyEarning)
class YearlyEarningAdmin(admin.ModelAdmin):
    list_display = ('year', 'total_earnings', 'total_earnings_with_vat')  # Display year and total earnings
    search_fields = ('year',)  # Allow search by year
    list_filter = ('year',)  # Filter by year

@admin.register(HouseEarning)
class HouseEarningAdmin(admin.ModelAdmin):
    list_display = ('house', 'month', 'total_price', 'total_price_with_vat')  # Display house, month, and total price
    search_fields = ('house__name', 'month')  # Allow search by house name and month
    list_filter = ('month', 'house')  # Filter by month and house
    ordering = ('-month',)  # Order by month in descending order

from django.contrib import admin
from .models import BookingExpense
from decimal import Decimal

@admin.register(BookingExpense)
class BookingExpenseAdmin(admin.ModelAdmin):
    list_display = ('booking', 'expense_type', 'amount', 'vat_deductible', 'month_display', 'year_display')  # ✅ Added 'month_display' and 'year_display'
    search_fields = ('booking__house__name', 'booking__customer_name', 'expense_type')
    list_filter = ('expense_type', 'date')  # ✅ Filter by 'date' instead of 'month' and 'year'
    ordering = ('-date',)  # ✅ Order by 'date' instead of 'year' and 'month'

    # ✅ Calculate VAT deductible (19% of the amount)
    def vat_deductible(self, obj):
        if obj.amount:  # Ensure amount exists
            return round(obj.amount * Decimal('0.19'), 2)  # ✅ Convert 0.19 to Decimal
        return None

    vat_deductible.short_description = "VAT Deductible (19%)"  # ✅ Column header in admin panel

    # ✅ Display month from 'date' field
    def month_display(self, obj):
        return obj.date.strftime('%m')  # Return month as two-digit string (01 to 12)
    month_display.short_description = 'Month'

    # ✅ Display year from 'date' field
    def year_display(self, obj):
        return obj.date.strftime('%Y')  # Return year as four-digit string
    year_display.short_description = 'Year'



from decimal import Decimal

from django.contrib import admin
from decimal import Decimal
from .models import MonthlyExpense

from django.utils import timezone

@admin.register(MonthlyExpense)
class MonthlyExpenseAdmin(admin.ModelAdmin):
    list_display = ('house', 'formatted_month', 'total_expense', 'total_expense_with_vat')
    search_fields = ('house__name', 'date')  # Update to search by 'date'
    list_filter = ('date', 'house')  # Update to filter by 'date'

    def formatted_month(self, obj):
        """Custom method to display the month as YYYY-MM."""
        return obj.date.strftime('%Y-%m')  # Use the 'date' field to display as YYYY-MM
    formatted_month.admin_order_field = 'date'  # Allow sorting by 'date'
    formatted_month.short_description = 'Month'  # Label in the admin

    def total_expense_with_vat(self, obj):
        """Custom method to calculate total expense with VAT."""
        vat_rate = Decimal('0.19')  # Example VAT rate (19%)
        # Convert total_expense to Decimal if it's a float
        total_expense = Decimal(obj.total_expense)  # Ensure total_expense is Decimal
        total = total_expense * (1 + vat_rate)  # Perform multiplication
        return round(total, 2)  # Round the result to 2 decimal places

    total_expense_with_vat.short_description = 'Total Expense with VAT'


