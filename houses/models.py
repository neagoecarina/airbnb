from django.db import models
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db import models,transaction
from django.db.models import Sum
from django.contrib.auth.models import User

from .utils import get_discounted_price  # Import your discount function

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

# houses/models.py



class House(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='house_photos/', blank=True, null=True)  # Add this line


    def __str__(self):
        return self.name


class Booking(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=255, default="Unknown")
    start_date = models.DateField()
    end_date = models.DateField()
    booking_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # New field for earnings
    #cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))  # Default cleaning fee
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Booking for {self.house.name} by {self.customer_name}"

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
                print("🔵 Starting save operation.")

                # Ensure price_per_night is a Decimal before calculation
                price_per_night = Decimal(self.house.price)
                print(f"✅ House price per night: {price_per_night}")


                # Get the discount period, if any
                discount_period = Discount.objects.filter(
                    house=self.house,
                    start_date__lte=self.end_date,
                    end_date__gte=self.start_date
                ).first()

                total_discounted_earnings = Decimal('0.00')
                total_non_discounted_earnings = Decimal('0.00')

                # Iterate over each day in the booking period and apply the correct pricing
                current_date = self.start_date
                while current_date <= self.end_date:
                    if discount_period and discount_period.start_date <= current_date <= discount_period.end_date:
                        # Apply discount if the current date falls within the discount period
                        discounted_price_per_night = price_per_night * (1 - (discount_period.discount_percentage / Decimal('100')))
                        total_discounted_earnings += discounted_price_per_night
                        print(f"✅ Discount applied on {current_date}: {discounted_price_per_night}")
                    else:
                        # No discount, use the original price
                        total_non_discounted_earnings += price_per_night
                        print(f"✅ No discount on {current_date}: {price_per_night}")

                    # Move to the next day
                    current_date += timedelta(days=1)

                # Total earnings is the sum of both discounted and non-discounted earnings
                self.booking_earnings = total_discounted_earnings + total_non_discounted_earnings
                print(f"✅ Calculated Booking Earnings: {self.booking_earnings}")

                # Ensure the value is correct
                if self.booking_earnings == 0:
                    raise Exception("❌ Booking earnings calculated as zero.")

                # Save the booking after all fields are assigned
                #self.booking.user = request.user
                super().save(*args, **kwargs)
                print("✅ Booking saved successfully.")

                if not self.pk:
                    raise Exception("❌ Booking wasn't saved. No primary key (pk) set.")


                # Create the Cleaning Fee Expense for the booking (Only once!)
                if not BookingExpense.objects.filter(booking=self).exists():
                    booking_expense = BookingExpense.objects.create(
                        booking=self,
                        expense_type="Cleaning Fee",
                        #amount=self.cleaning_fee,
                        amount=CleaningFeeSetting.get_current_fee(),
                        date=self.start_date  # Pass full date here
                    )
                    print(f"✅ Cleaning fee expense created: {booking_expense.amount}")
                else:
                    print("⚠️ Cleaning fee expense already exists for this booking.")


                # Get the first day of the month for consistency
                first_day_of_month = date(self.start_date.year, self.start_date.month, 1)


                # --- Update Monthly Expenses ---
                total_booking_expenses = BookingExpense.objects.filter(
                    booking__house=self.house,
                    date__year=self.start_date.year,  # Use `date__year`
                    date__month=self.start_date.month  # Use `date__month`
                ).aggregate(total=Sum('amount'))['total'] or 0


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
                    print(f"✅ Monthly expenses updated to {total_expenses}")


                # --- Update Earnings ---
                monthly_earnings = MonthlyEarning.get_or_create_earnings_for_month(first_day_of_month.strftime("%Y-%m"))
                monthly_earnings.total_earnings += self.booking_earnings
                monthly_earnings.save()
                print(f"✅ Monthly earnings updated {monthly_earnings.total_earnings}")


                yearly_earnings = YearlyEarning.get_or_create_yearly_earnings(str(self.start_date.year))
                yearly_earnings.total_earnings = Decimal(yearly_earnings.total_earnings)  # Convert to Decimal if needed
                yearly_earnings.total_earnings += self.booking_earnings
                yearly_earnings.save()
                print(f"✅ Yearly earnings updated {yearly_earnings.total_earnings}")


                house_earnings, created = HouseEarning.get_or_create_house_earnings(self.house, first_day_of_month)
                house_earnings.total_price += self.booking_earnings
                house_earnings.save()
                print(f"✅ House earnings updated to {house_earnings.total_price}, booking_earnings = {self.booking_earnings} ")


        except Exception as e:
            print(f"❌ Error during booking save: {e}")
            raise  # Ensure the exception is raised to avoid silent failures




class MonthlyEarning(models.Model):
    month_name = models.DateField()  # Store as DateField, e.g., the first day of the month
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Earnings for {self.month_name}"

    @property
    def total_earnings_with_vat(self):
        """Calculate total earnings including VAT (assuming 19% VAT)."""
        return round(self.total_earnings * Decimal('1.19'), 2)

    @staticmethod
    def get_or_create_earnings_for_month(month_name):
        # Ensure month_name is converted to a valid date (e.g., "2025-03" -> "2025-03-01")
        first_day_of_month = datetime.strptime(month_name, "%Y-%m")
        # Use the first day of the month as the valid date
        earnings, created = MonthlyEarning.objects.get_or_create(month_name=first_day_of_month.date())
        return earnings



class UtilityExpense(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Use .date() to extract only the date part
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
                # If the MonthlyExpense already exists, add the new total_utilities to the existing one
                monthly_expense.total_expense += total_utilities
                

        except Exception as e:
            print(f"Error while updating MonthlyExpense: {e}")

                


class YearlyEarning(models.Model):
    year = models.DateField()  # Store as DateField, e.g., the first day of the year
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        # Ensure that 'year' is not None
        return f"Earnings for {self.year.year if self.year else 'Unknown Year'}"

    @property
    def total_earnings_with_vat(self):
        """Calculate total earnings including VAT (assuming 19% VAT)."""
        return round(self.total_earnings * Decimal('1.19'), 2)

    @staticmethod
    def get_or_create_yearly_earnings(year):
        # Convert year to the first day of that year (e.g., "2025" -> "2025-01-01")
        first_day_of_year = datetime.strptime(year, "%Y")
        earnings, created = YearlyEarning.objects.get_or_create(year=first_day_of_year.date())
        return earnings




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
        return earnings, created
    


class BookingExpense(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    expense_type = models.CharField(max_length=255, default="Cleaning Fee")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)  # Default to current date

    def __str__(self):
        return f"{self.expense_type} for {self.booking.house.name} in {self.date.strftime('%m/%Y')}"

    


class MonthlyExpense(models.Model):
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    date = models.DateField()  # Using DateField to store the date (first of the month)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Expense for {self.house.name} in {self.date.strftime('%m-%Y')}"

    @staticmethod
    def update_expenses(house, expense_value, date):
        # Set the date to the first day of the month
        month_start_date = date.replace(day=1)  # Ensure it's the first day of the month

        # Try to get the monthly expense for the house and month
        monthly_expense, created = MonthlyExpense.objects.get_or_create(
            house=house, date=month_start_date
        )

        if not created:  # If the entry already exists, add the new expense to the total
            monthly_expense.total_expense += expense_value
            monthly_expense.save()
        else:  # If it's a new entry, set the total expense to the value of the new expense
            monthly_expense.total_expense = expense_value
            monthly_expense.save()

        return monthly_expense



class Discount(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="discounts")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Discount for {self.house.name} from {self.start_date} to {self.end_date}"

    # Check if the discount is active for a given date
    def is_active(self, check_date=None):
        if not check_date:
            check_date = timezone.now().date()
        return self.start_date <= check_date <= self.end_date

class CleaningFeeSetting(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))

    def __str__(self):
        return f"Cleaning Fee: {self.amount} RON"

    @staticmethod
    def get_current_fee():
        setting, _ = CleaningFeeSetting.objects.get_or_create(id=1)
        return setting.amount
