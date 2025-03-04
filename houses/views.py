from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import House, Booking, UtilityExpense,MonthlyEarning, YearlyEarning, HouseEarning, MonthlyExpense
from datetime import datetime, timedelta
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import re
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import House

def landing_page(request):
    return render(request, 'landing.html')  # This will load landing.html

# List all houses
def houses(request):
    myhouses = House.objects.all()
    return render(request, 'houses/all_houses.html', {'myhouses': myhouses})

# View to manage houses (view all houses)
def manage_houses(request):
    houses = House.objects.all()
    return render(request, 'houses/manage_houses.html', {'houses': houses})

# View to add or edit a house
def house_form(request, house_id=None):  # Use 'house_id' instead of 'id'
    if house_id:
        house = get_object_or_404(House, id=house_id)  # Update this line
    else:
        house = None

    context = {'house': house}

    if request.method == 'POST':
        name = request.POST['name']
        address = request.POST['address']
        price = request.POST['price']

        if house:
            # Update the existing house
            house.name = name
            house.address = address
            house.price = price
            house.save()
        else:
            # Create a new house
            House.objects.create(name=name, address=address, price=price)

        return redirect('manage_houses')

    return render(request, 'houses/house_form.html', context)
# View to delete a house
# View to delete a house
def delete_house(request, house_id):  # Use 'house_id' here as well
    house = get_object_or_404(House, id=house_id)  # Update this line
    house.delete()
    return redirect('manage_houses')  # Redirect after deletion

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

from django.http import JsonResponse
from decimal import Decimal
from .models import UtilityExpense

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
            # Check if the user confirmed update in the modal (proceed == "true")
            if proceed == "true":  # User confirmed update
                # Only update the water expense if provided and not None
                if water_expense is not None:
                    existing_entry.water_expense = water_expense
                
                # Only update the electricity expense if provided and not None
                if electricity_expense is not None:
                    existing_entry.electricity_expense = electricity_expense

                # Recalculate total expense
                existing_entry.total_expense = float(existing_entry.water_expense) + float(existing_entry.electricity_expense)
                existing_entry.save()

                return JsonResponse({"message": "Expenses updated successfully."})

            else:
                modal_message = ""
                
                # Only show the modal if water is being updated and it's already > 0
                if water_expense is not None and existing_entry.water_expense > 0:
                    modal_message += f"Water expense is already €{existing_entry.water_expense}. Do you wish to update it? "

                # Only show the modal if electricity is being updated and it's already > 0
                if electricity_expense is not None and existing_entry.electricity_expense > 0:
                    modal_message += f"Electricity expense is already €{existing_entry.electricity_expense}. Do you wish to update it? "
                
                # If no modal message, proceed with the update automatically (save without modal)
                if not modal_message:
                    # Update the expenses without needing confirmation
                    if water_expense is not None:
                        existing_entry.water_expense = water_expense
                    if electricity_expense is not None:
                        existing_entry.electricity_expense = electricity_expense

                    # Recalculate total expense
                    existing_entry.total_expense = float(existing_entry.water_expense) + float(existing_entry.electricity_expense)
                    existing_entry.save()

                    return JsonResponse({"message": "Expenses updated successfully."})

                # If there is a modal message, return the modal message
                return JsonResponse({
                    "message": "Existing expenses found",
                    "modal_message": modal_message,
                    "existing_water": str(existing_entry.water_expense),
                    "existing_electricity": str(existing_entry.electricity_expense),
                })

        else:
            # If no existing entry for this house, month, and year, create a new entry
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




from django.shortcuts import render
from decimal import Decimal
from .models import MonthlyEarning, YearlyEarning, MonthlyExpense
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from django.shortcuts import render
from django.db.models import Sum
from .models import MonthlyEarning, House, MonthlyExpense, UtilityExpense, HouseEarning, BookingExpense
from django.utils import timezone


from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
def financial_overview(request):
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get total earnings for the current month
    total_earnings = MonthlyEarning.objects.filter(month_name=f'{current_year}-{current_month:02d}').aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0.00

    # Convert total_earnings to Decimal to avoid type errors when performing calculations
    total_earnings_decimal = Decimal(total_earnings)

    # Calculate total VAT collected (19% of total earnings)
    total_vat_collected = total_earnings_decimal * Decimal('0.19')

    # Get total expenses from MonthlyExpense for the current month and year
    # Update the filter to use date__month and date__year
    total_expenses = MonthlyExpense.objects.filter(
        date__month=current_month, 
        date__year=current_year
    ).aggregate(Sum('total_expense'))['total_expense__sum'] or 0.00


    # Get total utility expenses for the current month and year
    total_utility_expenses = UtilityExpense.objects.filter(year=current_year, month=current_month).aggregate(Sum('total_expense'))['total_expense__sum'] or 0.00

    # Get total booking expenses for the current month and year
    total_booking_expenses = BookingExpense.objects.filter(year=current_year, month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0.00

    # Combine all expenses
    # Assuming total_expenses, total_utility_expenses, and total_booking_expenses are the values being calculated.
    total_net_expenses = Decimal(total_expenses) + Decimal(total_utility_expenses) + Decimal(total_booking_expenses)
    # Calculate net earnings (total earnings - total expenses)
    total_net_earnings = total_earnings_decimal - Decimal(total_net_expenses)

    # Calculate average earnings per house for the current month
    houses = House.objects.all()
    total_earnings_per_house = 0.00
    for house in houses:
        house_earnings = HouseEarning.objects.filter(house=house, month=f'{current_year}-{current_month:02d}').aggregate(Sum('total_price'))['total_price__sum'] or 0.00
        total_earnings_per_house += house_earnings

    avg_earnings_per_house = total_earnings_per_house / len(houses) if len(houses) > 0 else 0.00

    # Get total VAT deductible (e.g., assume 19% for simplicity on total expenses)
    total_vat_deductible = total_net_expenses * Decimal('0.19')
    # Pass all data to the template
    return render(request, 'houses/financial_overview.html', {
        'total_earnings': total_earnings_decimal,
        'total_expenses': total_expenses,
        'total_utility_expenses': total_utility_expenses,
        'total_booking_expenses': total_booking_expenses,
        'total_net_earnings': total_net_earnings,
        'avg_earnings_per_house': avg_earnings_per_house,
        'total_vat_collected': total_vat_collected,
        'total_vat_deductible': total_vat_deductible,
        'houses': houses,
        'total_net_expenses': total_net_expenses,
    })


@csrf_exempt
def calculate_taxes(request):
    # Get the latest monthly and yearly earnings or set defaults if no entries
    try:
        total_monthly_earnings = MonthlyEarning.objects.latest('month_name').total_earnings
    except MonthlyEarning.DoesNotExist:
        total_monthly_earnings = Decimal('0.00')

    try:
        total_yearly_earnings = YearlyEarning.objects.latest('year').total_earnings
    except YearlyEarning.DoesNotExist:
        total_yearly_earnings = Decimal('0.00')

    # Fetch total yearly expenses for PFA (from MonthlyExpense)
    try:
        total_yearly_expenses = MonthlyExpense.objects.aggregate(total=Sum('total_expense'))['total'] or Decimal('0.00')
    except MonthlyExpense.DoesNotExist:
        total_yearly_expenses = Decimal('0.00')

    if request.method == 'POST':
        data = json.loads(request.body)
        business_mode = data.get('business_mode')
        num_employees = int(data.get('employees', 0))

        # Initialize response data dictionary
        response_data = {}

        if business_mode == 'PFA':
            # Calculate net profit (earnings - expenses)
            total_profit = total_yearly_earnings - total_yearly_expenses

            # Apply income tax (10% on profit) for PFA
            income_tax = total_profit * Decimal('0.1')  # 10% income tax

            # Apply VAT (9% on profit) for PFA
            vat = total_profit * Decimal('0.09')  # 9% VAT on profit

            # Prepare response data for PFA
            response_data = {
                'income_tax': income_tax.quantize(Decimal('0.01')),
                'vat': vat.quantize(Decimal('0.01'))
            }

        elif business_mode == 'SRL':
            # Use total monthly earnings for SRL
            total_income = total_monthly_earnings

            # Determine microenterprise tax rate based on number of employees (1% or 3%)
            if num_employees == 0:
                micro_tax = total_income * Decimal('0.01')  # 1% tax rate for SRL without employees
            else:
                micro_tax = total_income * Decimal('0.03')  # 3% tax rate for SRL with employees

            # Apply VAT (9% on monthly earnings) for SRL
            vat = total_income * Decimal('0.09')  # 9% VAT for SRL

            # Prepare response data for SRL
            response_data = {
                'micro_tax': micro_tax.quantize(Decimal('0.01')),
                'vat': vat.quantize(Decimal('0.01'))
            }

        # Return the JSON response with calculated taxes
        return JsonResponse(response_data)
