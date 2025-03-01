from django.db import models
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
# Create your models here.
# houses/models.py



class House(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Booking(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=255, default="Unknown")
    start_date = models.DateField()
    end_date = models.DateField()
    booking_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field

    def __str__(self):
        return f"Booking for {self.house.name} by {self.customer_name}"
 
    def save(self, *args, **kwargs):
        #super().save(*args, **kwargs)
        # Calculate total days of the booking
        total_days = (self.end_date - self.start_date).days+1
        # Get the price per night from the associated house
        price_per_night = self.house.price

        # Calculate the earnings from this booking
        booking_earnings = total_days * price_per_night
        # Ensure booking_earnings is Decimal
        self.booking_earnings = Decimal(str(booking_earnings))  # Set the booking_earnings before saving

        super().save(*args, **kwargs)
        # Get the month name (YYYY-MM)
        month_name = self.start_date.strftime("%Y-%m")

        # Get or create the earnings for this month
        earnings = MonthlyEarning.get_or_create_earnings_for_month(month_name)

        # Update the total earnings for the month


# Ensure booking_earnings is Decimal
        booking_earnings = Decimal(str(booking_earnings))  # Convert to Decimal

# Ensure total_earnings is also Decimal before adding
        earnings.total_earnings = Decimal(str(earnings.total_earnings)) + booking_earnings
        earnings.save()

# Get the year from the start date
        year = self.start_date.year

# Get or create the earnings for the given year
        yearly_earnings = YearlyEarning.get_or_create_yearly_earnings(str(year))

# Update the total earnings for the year
        yearly_earnings.total_earnings = Decimal(str(yearly_earnings.total_earnings)) + self.booking_earnings
        yearly_earnings.save()




class MonthlyEarning(models.Model):
    month_name = models.CharField(max_length=7)  # Format: YYYY-MM
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Earnings for {self.month_name}"

    @staticmethod
    def get_or_create_earnings_for_month(month_name):
        # Check if earnings for this month already exist
        earnings, created = MonthlyEarning.objects.get_or_create(month_name=month_name)
        return earnings
    
class UtilityExpense(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    year = models.IntegerField(default=datetime.now().year)  # Default to current year
    month = models.IntegerField(default=datetime.now().month)  # Default to current month
    water_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_expense = self.water_expense + self.electricity_expense
        super().save(*args, **kwargs)

class YearlyEarning(models.Model):
    year = models.CharField(max_length=4)  # Format: YYYY
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Earnings for {self.year}"

    @staticmethod
    def get_or_create_yearly_earnings(year):
        # Check if earnings for this year already exist
        earnings, created = YearlyEarning.objects.get_or_create(year=year)
        return earnings
