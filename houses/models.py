from django.db import models
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from django.db import transaction

# Create your models here.
# houses/models.py



class House(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


from decimal import Decimal
from datetime import date
from django.db import transaction

from decimal import Decimal
from django.db import models, transaction
from django.db.models import Sum
from datetime import date

class Booking(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=255, default="Unknown")
    start_date = models.DateField()
    end_date = models.DateField()
    booking_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # New field for earnings
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))  # Default cleaning fee

    def __str__(self):
        return f"Booking for {self.house.name} by {self.customer_name}"

    def save(self, *args, **kwargs):
    # Remove or comment out the debug exception line
    # raise Exception("Debug: Save method is running!")  # Remove this line

        try:
                with transaction.atomic():
                 print("🔵 Starting save operation.")

                # Ensure price_per_night is a Decimal before calculation
                price_per_night = Decimal(self.house.price)
                print(f"✅ House price per night: {price_per_night}")

                total_days = (self.end_date - self.start_date).days + 1  # Include the start day
                print(f"✅ Total Days: {total_days}")

                # Calculate booking earnings
                self.booking_earnings = Decimal(total_days * price_per_night)
                print(f"✅ Calculated Booking Earnings: {self.booking_earnings}")

                # Ensure the value is correct
                if self.booking_earnings == 0:
                        raise Exception("❌ Booking earnings calculated as zero.")

                # Save the booking after all fields are assigned
                super().save(*args, **kwargs)
                print("✅ Booking saved successfully.")

                if not self.pk:
                        raise Exception("❌ Booking wasn't saved. No primary key (pk) set.")

                # Create the Cleaning Fee Expense for the booking
                booking_expense = BookingExpense.objects.create(
                        booking=self,
                        expense_type="Cleaning Fee",
                        amount=self.cleaning_fee,
                        month=self.start_date.month,
                        year=self.start_date.year
                )
                print(f"✅ Cleaning fee expense created: {booking_expense.amount}")

                # Get the first day of the month for consistency
                first_day_of_month = date(self.start_date.year, self.start_date.month, 1)

                # --- Update Monthly Expenses ---
                from django.db.models import Sum

                # Sum all cleaning fees for this house and month
                total_booking_expenses = BookingExpense.objects.filter(
                        booking__house=self.house,
                        month=self.start_date.month,
                        year=self.start_date.year
                ).aggregate(total=Sum('amount'))['total'] or 0

                # Sum all utility expenses for this house and month
                total_utilities = UtilityExpense.objects.filter(
                        house=self.house,
                        date__year=self.start_date.year,
                        date__month=self.start_date.month
                ).aggregate(total=Sum('total_expense'))['total'] or 0

                print(f"✅ Total booking expenses: {total_booking_expenses}")
                print(f"✅ Total utility expenses: {total_utilities}")

                # Calculate total expenses for the month
                total_expenses = total_booking_expenses + total_utilities

                # Create or update MonthlyExpense
                monthly_expense, created = MonthlyExpense.objects.get_or_create(
                        house=self.house,
                        date=first_day_of_month,
                        defaults={"total_expense": total_expenses}
                )

                if not created:
                        monthly_expense.total_expense = total_expenses
                        monthly_expense.save()
                        print("✅ Monthly expenses updated.")

                # --- Update Earnings ---
                # Get or create the MonthlyEarning for the month and house
                monthly_earnings = MonthlyEarning.get_or_create_earnings_for_month(first_day_of_month.strftime("%Y-%m"))
                monthly_earnings.total_earnings += self.booking_earnings
                monthly_earnings.save()
                print("✅ Monthly earnings updated.")

                # Get or create the YearlyEarnings for the year and house
                yearly_earnings = YearlyEarning.get_or_create_yearly_earnings(str(self.start_date.year))
                yearly_earnings.total_earnings = Decimal(yearly_earnings.total_earnings)  # Convert to Decimal if needed
                yearly_earnings.total_earnings += self.booking_earnings
                yearly_earnings.save()
                print("✅ Yearly earnings updated.")

                # Get or create the HouseEarnings for the house and month
                house_earnings = HouseEarning.get_or_create_house_earnings(self.house, first_day_of_month)
                house_earnings.total_price += self.booking_earnings
                house_earnings.save()
                print("✅ House earnings updated.")

        except Exception as e:
                print(f"❌ Error during booking save: {e}")
                raise  # Ensure the exception is raised to avoid silent failures


from decimal import Decimal

class MonthlyEarning(models.Model):
    month_name = models.CharField(max_length=7)  # Format: YYYY-MM
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Earnings for {self.month_name}"

    @property
    def total_earnings_with_vat(self):
        """Calculate total earnings including VAT (assuming 19% VAT)."""
        return round(self.total_earnings * Decimal('1.19'), 2)

    @staticmethod
    def get_or_create_earnings_for_month(month_name):
        # Check if earnings for this month already exist
        earnings, created = MonthlyEarning.objects.get_or_create(month_name=month_name)
        return earnings

from decimal import Decimal   
from datetime import datetime
from django.db import models
from django.utils import timezone

class UtilityExpense(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now().date())  # Use .date() to extract only the date part
    water_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
       
        # Calculate total expense from water and electricity
        self.total_expense = self.water_expense + self.electricity_expense
        super().save(*args, **kwargs)  # Save UtilityExpense first

        # Ensure we're using the first day of the month for consistency
        first_day_of_month = self.date.replace(day=1)

        try:
                # Recalculate total utility expenses for the month
                total_utilities = UtilityExpense.objects.filter(
                house=self.house,
                date__year=self.date.year,
                date__month=self.date.month
                ).aggregate(total=models.Sum('total_expense'))['total'] or 0  # Default to 0

                # Create or update MonthlyExpense
                monthly_expense, created = MonthlyExpense.objects.get_or_create(
                house=self.house,
                date=first_day_of_month,
                defaults={"total_expense": total_utilities}
                )

                if not created:
                        monthly_expense.total_expense = total_utilities
                        monthly_expense.save()

        except Exception as e:
                print(f"Error while updating MonthlyExpense: {e}")

                
class YearlyEarning(models.Model):
    year = models.CharField(max_length=4)  # Format: YYYY
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Earnings for {self.year}"

    @property
    def total_earnings_with_vat(self):
        """Calculate total earnings including VAT (assuming 19% VAT)."""
        return round(self.total_earnings * Decimal('1.19'), 2)

    @staticmethod
    def get_or_create_yearly_earnings(year):
        # Check if earnings for this year already exist
        earnings, created = YearlyEarning.objects.get_or_create(year=year)
        return earnings


from django.utils import timezone
from decimal import Decimal

class HouseEarning(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='house_earnings')
    month = models.DateField()  # Store the date (e.g., first day of the month)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Earnings for {self.house.name} in {self.month.strftime('%B %Y')}"

    @property
    def total_price_with_vat(self):
        """Calculate total price including VAT (assuming 19% VAT)."""
        return round(self.total_price * Decimal('1.19'), 2)

    @staticmethod
    def get_or_create_house_earnings(house, month):
        # Get or create earnings for a specific house and month
        earnings, created = HouseEarning.objects.get_or_create(
            house=house, 
            month=month
        )
        return earnings
    
class BookingExpense(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    expense_type = models.CharField(max_length=255, default="Cleaning Fee")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()  # month of the booking
    year = models.IntegerField()  # year of the booking

    def __str__(self):
        return f"{self.expense_type} for {self.booking.house.name} in {self.month}/{self.year}"
    
class MonthlyExpense(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    date = models.DateField()  # Changed to DateField
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Expense for {self.house.name} in {self.date.strftime('%m-%Y')}"

