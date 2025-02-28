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



# Function to validate decimal input
def isValidDecimal(value):
    decimalPattern = r'^\d+(\.\d{1,2})?$'  # Pattern for valid decimal (up to two decimal places)
    return bool(re.match(decimalPattern, value))

def add_utility_expenses(request):
    houses = House.objects.all()
    months = range(1, 13)
    years = range(2023, 2034)
    
    if request.method == "POST":
        house_id = request.POST.get('house')
        month = request.POST.get('month')
        year = request.POST.get('year')
        water_expense = request.POST.get('water')
        electricity_expense = request.POST.get('electricity')
        proceed = request.POST.get('proceed')  # Check if user confirmed update

        # Validate input fields (only if they are not empty)
        if water_expense and not isValidDecimal(water_expense):
            return JsonResponse({"message": "Invalid water expense value."}, status=400)
        if electricity_expense and not isValidDecimal(electricity_expense):
            return JsonResponse({"message": "Invalid electricity expense value."}, status=400)

        # Convert only non-empty values to Decimal
        water_expense = Decimal(water_expense) if water_expense else None
        electricity_expense = Decimal(electricity_expense) if electricity_expense else None

        # Check if an entry already exists for this house and month
        existing_entry = UtilityExpense.objects.filter(house_id=house_id, month=month, year=year).first()

        if existing_entry:
            if proceed == "true":  # User confirmed update
                # Update the water and electricity expenses
                existing_entry.water_expense = water_expense if water_expense is not None else existing_entry.water_expense
                existing_entry.electricity_expense = electricity_expense if electricity_expense is not None else existing_entry.electricity_expense

                # Recalculate total expense
                existing_entry.total_expense = float(existing_entry.water_expense) + float(existing_entry.electricity_expense)
                existing_entry.save()

                return JsonResponse({"message": "Expenses updated successfully."})
            else:
                # If either water or electricity has been registered already with a non-zero value, show the modal
                if existing_entry.water_expense > 0 or existing_entry.electricity_expense > 0:
                    return JsonResponse({
                        "message": "Existing expenses found",
                        "existing_water": str(existing_entry.water_expense),
                        "existing_electricity": str(existing_entry.electricity_expense),
                    })

        # Create new entry if none exists
        UtilityExpense.objects.create(
            house_id=house_id,
            month=month,
            year=year,
            water_expense=water_expense or 0,  # Default to 0 if still None
            electricity_expense=electricity_expense or 0,
            total_expense=float((water_expense or 0) + (electricity_expense or 0))
        )
        return JsonResponse({"message": "Expenses added successfully."})

    return render(request, 'houses/utilityexpense.html', {
        'houses': houses,
        'months': months,
        'years': years,
    })
