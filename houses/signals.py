from datetime import date
from django.db.models import F
from django.dispatch import receiver
from django.db.models.signals import post_delete
from .models import Booking, BookingExpense, HouseEarning, MonthlyEarning, YearlyEarning, UtilityExpense, MonthlyExpense

@receiver(post_delete, sender=Booking)
def update_earnings_on_booking_delete(sender, instance, **kwargs):
    house = instance.house
    start_date = instance.start_date
    year = start_date.year
    month = start_date.month
    first_day_of_month = date(year, month, 1)
    first_day_of_year = date(year, 1, 1)

    # Update HouseEarning
    HouseEarning.objects.filter(house=house, month=first_day_of_month).update(
        total_price=F('total_price') - instance.booking_earnings
    )

    # Update MonthlyEarning
    MonthlyEarning.objects.filter(month_name=first_day_of_month).update(
        total_earnings=F('total_earnings') - instance.booking_earnings
    )

    # Update YearlyEarning
    YearlyEarning.objects.filter(year=first_day_of_year).update(
        total_earnings=F('total_earnings') - instance.booking_earnings
    )

    # Delete related expenses
    BookingExpense.objects.filter(booking=instance).delete()
@receiver(post_delete, sender=BookingExpense)
@receiver(post_delete, sender=UtilityExpense)
def update_monthly_expenses_on_delete(sender, instance, **kwargs):
    print(f"🧾 Expense deleted: {instance}")

    if isinstance(instance, BookingExpense):
        house = instance.booking.house
        amount = instance.amount  # presupun că BookingExpense are câmpul amount
    else:
        house = instance.house
        amount = instance.total_expense  # aici folosim total_expense, nu amount

    month_start = instance.date.replace(day=1)

    try:
        monthly_expense = MonthlyExpense.objects.get(house=house, date=month_start)
        monthly_expense.total_expense -= amount
        if monthly_expense.total_expense < 0:
            monthly_expense.total_expense = 0
        monthly_expense.save()
        print(f"✅ Monthly expense updated for {house.name} - {month_start}")
    except MonthlyExpense.DoesNotExist:
        print(f"⚠️ MonthlyExpense entry not found for {house.name} in {month_start}")
