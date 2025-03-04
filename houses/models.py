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

from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db import transaction

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
                try:
                        with transaction.atomic():
                                print("Starting save operation.")
                                # Ensure price_per_night is a Decimal before calculation
                                price_per_night = Decimal(self.house.price)  # Convert to Decimal
                                total_days = (self.end_date - self.start_date).days + 1
                                print(f"Total Days: {total_days}")  # Debugging line

                                # Calculate booking earnings as Decimal
                                self.booking_earnings = Decimal(total_days * price_per_night)  # Ensure result is Decimal
                                print(f"Calculated Booking Earnings: {self.booking_earnings}")  # Debugging line

                                # Save the booking first
                                super().save(*args, **kwargs)
                                print("Booking saved successfully.")

                                # Create the Cleaning Fee Expense for the booking
                                BookingExpense.objects.create(
                                        booking=self,
                                        expense_type="Cleaning Fee",
                                        amount=self.cleaning_fee,
                                        month=self.start_date.month,
                                        year=self.start_date.year
                                )
                                print("Cleaning fee expense created.")

                                # Get or create the MonthlyExpense for the house and month
                                month_name = self.start_date.strftime("%Y-%m")
                                year = self.start_date.year
                                print(f"Month/Year for MonthlyExpense: {month_name}/{year}")

                                # Update MonthlyExpense (handling cleaning fee)
                                monthly_expense, created = MonthlyExpense.objects.get_or_create(house=self.house, month=month_name, year=year)
                                monthly_expense.total_expense = Decimal(monthly_expense.total_expense) + Decimal(self.cleaning_fee) 
                                monthly_expense.save()
                                print("Monthly expense updated.")

                                # Update MonthlyEarnings (for the current month)
                                earnings = MonthlyEarning.get_or_create_earnings_for_month(month_name)
                                earnings.total_earnings =Decimal(earnings.total_earnings) + Decimal(self.booking_earnings)
                                earnings.save()
                                print("Monthly earnings updated.")

                                # Update YearlyEarnings (for the current year)
                                yearly_earnings = YearlyEarning.get_or_create_yearly_earnings(str(year))
                                yearly_earnings.total_earnings = Decimal(yearly_earnings.total_earnings) + Decimal(self.booking_earnings)
                                yearly_earnings.save()
                                print("Yearly earnings updated.")

                                # Update HouseEarnings (for the house and current month)
                                house_earnings = HouseEarning.get_or_create_house_earnings(self.house, month_name)
                                house_earnings.total_price =Decimal(house_earnings.total_price) + Decimal(self.booking_earnings)  # Already Decimal
                                house_earnings.save()
                                print("House earnings updated.")

                except Exception as e:
                        print(f"Error during transaction: {e}")
                        raise  # Reraise the exception after logging



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
class UtilityExpense(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    year = models.IntegerField(default=datetime.now().year)
    month = models.IntegerField(default=datetime.now().month)
    water_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    electricity_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_expense = self.water_expense + self.electricity_expense
        super().save(*args, **kwargs)

        # Get the month name (YYYY-MM)
        month_name = f"{self.year}-{str(self.month).zfill(2)}"  # Format YYYY-MM

        try:
            # Try to fetch existing MonthlyExpense
            monthly_expense = MonthlyExpense.objects.filter(house=self.house, month=month_name, year=self.year).first()

            if not monthly_expense:
                # If no MonthlyExpense exists, create it
                monthly_expense = MonthlyExpense.objects.create(
                    house=self.house,
                    month=month_name,
                    year=self.year,
                    total_expense=self.total_expense
                )
            else:
                # If MonthlyExpense exists, update the total_expense
                monthly_expense.total_expense += self.total_expense
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


class HouseEarning(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='house_earnings')
    month = models.CharField(max_length=7)  # Format: YYYY-MM
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Earnings for {self.house.name} in {self.month}"

    @property
    def total_price_with_vat(self):
        """Calculate total price including VAT (assuming 19% VAT)."""
        return round(self.total_price * Decimal('1.19'), 2)

    @staticmethod
    def get_or_create_house_earnings(house, month):
        # Get or create earnings for a specific house and month
        earnings, created = HouseEarning.objects.get_or_create(house=house, month=month)
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
    month = models.CharField(max_length=7)  # Format: YYYY-MM
    year = models.IntegerField()
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Total Expenses for {self.house.name} in {self.month}"