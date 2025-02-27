from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import House, Booking, UtilityExpense
from datetime import datetime, timedelta
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import re
from decimal import Decimal

# View to list all houses
def houses(request):
    myhouses = House.objects.all()  # Query all houses from the database
    return render(request, 'houses/all_houses.html', {'myhouses': myhouses})

# View for house details
# View for house details
@csrf_exempt  # Temporarily disable CSRF for debugging
def house_detail(request, house_id):
    myhouse = get_object_or_404(House, id=house_id)

    if request.method == "POST":
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        customer_name = request.POST.get('customer_name', 'Anonymous')

        if not start_date_str or not end_date_str:
            return JsonResponse({"success": False, "message": "Please select start and end dates."})

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if start_date >= end_date:
            return JsonResponse({"success": False, "message": "End date must be after start date."})

        # Overlapping booking check
        if Booking.objects.filter(house=myhouse, start_date__lt=end_date, end_date__gt=start_date).exists():
            return JsonResponse({"success": False, "message": "The selected dates are already booked."})

        # Create booking
        new_booking = Booking.objects.create(
            house=myhouse,
            customer_name=customer_name,
            start_date=start_date,
            end_date=end_date
        )

        return JsonResponse({"success": True, "message": "Booking successful!", "customer_name": new_booking.customer_name})

    # Get booked dates **(Move this inside the function)**
    booked_ranges = Booking.objects.filter(house=myhouse)
    booked_dates = []

    for booking in booked_ranges:
        current_date = booking.start_date
        while current_date <= booking.end_date:  # Include every date in the range
            booked_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)  # Move to the next day

    # Pass booked_dates as a JSON-safe list to the template
    return render(request, 'houses/details.html', {'myhouse': myhouse, 'booked_dates': json.dumps(booked_dates)})



# Define a function to check if the input is a valid decimal
def isValidDecimal(value):
    decimalPattern = r'^\d+(\.\d{1,2})?$'  # Pattern for valid decimal (up to two decimal places)
    return bool(re.match(decimalPattern, value))


def add_utility_expenses(request):
    houses = House.objects.all()
    months = range(1, 13)
    years = range(2023, 2034)
    selected_house = request.POST.get('house') if request.method == "POST" else None
    selected_month = request.POST.get('month') if request.method == "POST" else None
    selected_year = request.POST.get('year') if request.method == "POST" else None

    if request.method == "POST":
        house_id = request.POST.get('house')
        month = request.POST.get('month')
        year = request.POST.get('year')
        water_expense = request.POST.get('water')
        electricity_expense = request.POST.get('electricity')

        # Print values for debugging purposes
        print(f"House ID: {house_id}, Month: {month}, Year: {year}, Water Expense: {water_expense}, Electricity Expense: {electricity_expense}")

        # Set water and electricity to 0 if they are empty
        if not water_expense:
            water_expense = '0'
        if not electricity_expense:
            electricity_expense = '0'

        # Validate the decimal input fields
        if not (isValidDecimal(water_expense) or isValidDecimal(electricity_expense)):
            messages.error(request, "Invalid expense values entered.")
            return redirect('utility_expenses')  # Redirect to the form page if invalid

        # Ensure the values are Decimal for calculation
        water_expense = Decimal(water_expense)
        electricity_expense = Decimal(electricity_expense)

        # Look for an existing entry for this house, month, and year
        existing_entry = UtilityExpense.objects.filter(
            house_id=house_id, 
            month=month,
            year=year
        ).first()

        if existing_entry:
            # If an existing entry is found, update the fields if they are not zero
            if water_expense != 0:
                existing_entry.water_expense = water_expense
            if electricity_expense != 0:
                existing_entry.electricity_expense = electricity_expense

            # Recalculate total_expense based on updated values
            existing_entry.total_expense = float(existing_entry.water_expense) + float(existing_entry.electricity_expense)
            existing_entry.save()
            messages.success(request, "Expenses updated successfully.")
        else:
            # Create a new entry if no existing one is found
            UtilityExpense.objects.create(
                house_id=house_id,
                month=month,
                year=year,
                water_expense=water_expense,
                electricity_expense=electricity_expense,
                total_expense=float(water_expense + electricity_expense)  # Convert to float for total
            )
            messages.success(request, "Expenses added successfully.")
        
        return redirect('utility_expenses')  # Redirect after saving

    return render(request, 'houses/utilityexpense.html', {
        'houses': houses,
        'months': months,
        'years': years,
        'selected_house': selected_house,
        'selected_month': selected_month,
        'selected_year': selected_year,
    })
