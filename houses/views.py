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
        # ✅ Call update_monthly_expense() after booking is saved
        #update_monthly_expense(house_id, new_booking.start_date.year, new_booking.start_date.month)
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

import datetime
from decimal import Decimal
from django.http import JsonResponse
from .models import UtilityExpense, House
from datetime import datetime  # Ensure this is at the top of the file

from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render

from datetime import date  # Add this import at the top

# Your other views and logic
def add_utility_expenses(request):
    houses = House.objects.all()
    current_year = datetime.now().year  # Get the current year dynamically
    months = range(1, 13)
    years = range(current_year, current_year + 10)  # Start from current year

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

        # Get the first day of the month as a DateField
        first_day_of_month = date(int(year), int(month), 1)

        # Check if an entry already exists for this house and month
        existing_entry = UtilityExpense.objects.filter(house_id=house_id, date=first_day_of_month).first()

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
                    update_monthly_expense(house_id, first_day_of_month)  # Call the update function
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
                date=first_day_of_month,  # Use the full date here
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

def update_monthly_expense(house_id, month_date):  # Use a DateField directly

    from django.db.models import Sum
    from datetime import date

    # Get the first day of the month
    month_date = date(year=int(year), month=int(month), day=1)

    # Sum total utility expenses for this house & month
    total_utilities = UtilityExpense.objects.filter(
        house_id=house_id,
        date=month_date
    ).aggregate(total=Sum('total_expense'))['total'] or 0  # Default to 0 if none

    # Sum total booking expenses (e.g., cleaning fees)
    total_booking_expenses = Booking.objects.filter(
        house_id=house_id,
        start_date__year=year,
        start_date__month=month
    ).aggregate(total=Sum('cleaning_fee'))['total'] or 0  # Default to 0 if none

    # Calculate total expenses
    total_expenses = total_utilities + total_booking_expenses

    # Only create/update MonthlyExpense if there's **any** expense
    if total_expenses > 0:
        monthly_expense, created = MonthlyExpense.objects.get_or_create(
            house_id=house_id,
            date=month_date,
            defaults={"total_expense": total_expenses}
        )
        if not created:
            # Update existing entry
            monthly_expense.total_expense = total_expenses
            monthly_expense.save()




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



from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render

from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render

def financial_overview(request):
    # Get the selected time period from the URL or default to "monthly"
    time_period = request.GET.get('time_period', 'monthly')

    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Determine the date range based on the time period
    if time_period == 'monthly':
        # Start of the current month
        start_date = datetime(current_year, current_month, 1)
        # End of the current month: Take the first day of the next month and subtract 1 day
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_year = current_year if current_month < 12 else current_year + 1
        end_date = datetime(next_month_year, next_month, 1) - timedelta(days=1)
    elif time_period == 'quarterly-q1':
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 3, 31)
    elif time_period == 'quarterly-q2':
        start_date = datetime(current_year, 4, 1)
        end_date = datetime(current_year, 6, 30)
    elif time_period == 'quarterly-q3':
        start_date = datetime(current_year, 7, 1)
        end_date = datetime(current_year, 9, 30)
    elif time_period == 'quarterly-q4':
        start_date = datetime(current_year, 10, 1)
        end_date = datetime(current_year, 12, 31)
    elif time_period == 'yearly':
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)
    else:
        # Default to the current month if the time period is not recognized
        start_date = datetime(current_year, current_month, 1)
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_year = current_year if current_month < 12 else current_year + 1
        end_date = datetime(next_month_year, next_month, 1) - timedelta(days=1)

    # DEBUG: Print the date range for the selected period
    print(f"DEBUG: Time Period - {time_period}")
    print(f"DEBUG: Start Date: {start_date}")
    print(f"DEBUG: End Date: {end_date}")

    # Get total earnings for the selected time period
    total_earnings = MonthlyEarning.objects.filter(
        month_name__gte=start_date, 
        month_name__lte=end_date
    ).aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0.00

    # DEBUG: Print the raw total earnings value
    print(f"DEBUG: Total Earnings from DB: {total_earnings}")

    total_earnings_decimal = Decimal(total_earnings)

    # Calculate total VAT collected (19% of total earnings)
    total_vat_collected = total_earnings_decimal * Decimal('0.19')

    # DEBUG: Print the calculated VAT collected
    print(f"DEBUG: Total VAT Collected: {total_vat_collected}")

    # Get total expenses for the selected time period
    total_expenses = MonthlyExpense.objects.filter(
        date__gte=start_date, 
        date__lte=end_date
    ).aggregate(Sum('total_expense'))['total_expense__sum'] or 0.00

    # DEBUG: Print the raw total expenses value
    print(f"DEBUG: Total Expenses from DB: {total_expenses}")

    # Get total utility expenses for the selected time period
    total_utility_expenses = UtilityExpense.objects.filter(
        date__gte=start_date, 
        date__lte=end_date
    ).aggregate(Sum('total_expense'))['total_expense__sum'] or 0.00

    # DEBUG: Print the raw utility expenses value
    print(f"DEBUG: Total Utility Expenses from DB: {total_utility_expenses}")

    # Get total booking expenses for the selected time period
    total_booking_expenses = BookingExpense.objects.filter(
        date__gte=start_date, 
        date__lte=end_date
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00

    # DEBUG: Print the raw booking expenses value
    print(f"DEBUG: Total Booking Expenses from DB: {total_booking_expenses}")

    # Combine all expenses
    total_net_expenses = Decimal(total_utility_expenses) + Decimal(total_booking_expenses)

    # DEBUG: Print the total combined expenses
    print(f"DEBUG: Total Net Expenses: {total_net_expenses}")

    # Calculate net earnings (total earnings - total expenses)
    total_net_earnings = total_earnings_decimal - total_net_expenses

    # DEBUG: Print the net earnings
    print(f"DEBUG: Total Net Earnings: {total_net_earnings}")

    # Calculate earnings per house (Excluding and Including VAT)
    houses = House.objects.all()
    house_earnings_data = []
    total_earnings_per_house = Decimal('0.00')

    for house in houses:
        house_earnings_excl_vat = HouseEarning.objects.filter(
            house=house, 
            month__year=current_year, 
            month__month=current_month
        ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')

        # DEBUG: Print the earnings for each house
        print(f"DEBUG: Earnings for House {house.name}: {house_earnings_excl_vat}")

        # Calculate earnings including VAT (19% VAT)
        house_earnings_incl_vat = house_earnings_excl_vat * Decimal('1.19')

        house_earnings_data.append({
            'house_name': house.name,
            'total_earnings_excl_vat': house_earnings_excl_vat,
            'total_earnings_incl_vat': house_earnings_incl_vat
        })

        # Add to total earnings across all houses
        total_earnings_per_house += house_earnings_excl_vat

    # Calculate the average earnings per house
    avg_earnings_per_house = total_earnings_per_house / len(houses) if len(houses) > 0 else 0.00

    # DEBUG: Print the total earnings per house and average earnings
    print(f"DEBUG: Total Earnings Across All Houses: {total_earnings_per_house}")
    print(f"DEBUG: Average Earnings Per House: {avg_earnings_per_house}")

    # Get total VAT deductible (e.g., assume 19% for simplicity on total expenses)
    total_vat_deductible = total_net_expenses * Decimal('0.19')

    # DEBUG: Print the VAT deductible
    print(f"DEBUG: Total VAT Deductible: {total_vat_deductible}")

    # Calculate net VAT
    net_vat = total_vat_collected - total_vat_deductible

    # DEBUG: Print the net VAT
    print(f"DEBUG: Net VAT: {net_vat}")

    # Pass all data to the template
    return render(request, 'houses/financial_overview.html', {
        'total_earnings': total_earnings_decimal,
        'total_expenses': total_expenses,
        'total_utility_expenses': total_utility_expenses,
        'total_booking_expenses': total_booking_expenses,
        'total_net_earnings': total_net_earnings,
        'total_vat_collected': total_vat_collected,
        'total_vat_deductible': total_vat_deductible,
        'houses': houses,
        'total_net_expenses': total_net_expenses,
        'net_vat': net_vat,
        'house_earnings_data': house_earnings_data,
        'avg_earnings_per_house': avg_earnings_per_house,  # Make sure this is passed
        'time_period': time_period,  # Pass selected time period to the template
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

import csv
import openpyxl
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import House, MonthlyExpense  # Modify with your actual models

# Export to CSV
def export_to_csv(request):
    # Fetch the data you want to export
    expenses = MonthlyExpense.objects.all()
    
    # Create a response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="monthly_expenses.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['House', 'Date', 'Total Expense'])  # Header
    
    for expense in expenses:
        writer.writerow([expense.house.name, expense.date, expense.total_expense])
    
    return response

# Export to Excel
def export_to_excel(request):
    expenses = MonthlyExpense.objects.all()
    
    # Create an Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['House', 'Date', 'Total Expense'])  # Header
    
    for expense in expenses:
        ws.append([expense.house.name, expense.date, expense.total_expense])
    
    # Save to a BytesIO object to return as response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="monthly_expenses.xlsx"'
    wb.save(response)
    
    return response

# Generate PDF Report
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from datetime import datetime, timedelta
from decimal import Decimal
from .models import MonthlyExpense, MonthlyEarning, UtilityExpense, BookingExpense, House, HouseEarning

def generate_pdf_report(request):
    # Get the selected time period from the URL or default to "monthly"
    time_period = request.GET.get('time_period', 'monthly')

    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Determine the date range based on the time period
    if time_period == 'monthly':
        start_date = datetime(current_year, current_month, 1)
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_year = current_year if current_month < 12 else current_year + 1
        end_date = datetime(next_month_year, next_month, 1) - timedelta(days=1)
    elif time_period == 'quarterly-q1':
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 3, 31)
    elif time_period == 'quarterly-q2':
        start_date = datetime(current_year, 4, 1)
        end_date = datetime(current_year, 6, 30)
    elif time_period == 'quarterly-q3':
        start_date = datetime(current_year, 7, 1)
        end_date = datetime(current_year, 9, 30)
    elif time_period == 'quarterly-q4':
        start_date = datetime(current_year, 10, 1)
        end_date = datetime(current_year, 12, 31)
    elif time_period == 'yearly':
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)
    else:
        start_date = datetime(current_year, current_month, 1)
        next_month = current_month + 1 if current_month < 12 else 1
        next_month_year = current_year if current_month < 12 else current_year + 1
        end_date = datetime(next_month_year, next_month, 1) - timedelta(days=1)

    # Calculate total earnings for the selected time period
    total_earnings = MonthlyEarning.objects.filter(
        month_name__gte=start_date, 
        month_name__lte=end_date
    ).aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0.00
    total_earnings_decimal = Decimal(total_earnings)

    # Calculate total VAT collected (19% of total earnings)
    total_vat_collected = total_earnings_decimal * Decimal('0.19')

    # Get total expenses for the selected time period
    total_expenses = MonthlyExpense.objects.filter(
        date__gte=start_date, 
        date__lte=end_date
    ).aggregate(Sum('total_expense'))['total_expense__sum'] or 0.00

    # Get total utility expenses for the selected time period
    total_utility_expenses = UtilityExpense.objects.filter(
        date__gte=start_date, 
        date__lte=end_date
    ).aggregate(Sum('total_expense'))['total_expense__sum'] or 0.00

    # Get total booking expenses for the selected time period
    total_booking_expenses = BookingExpense.objects.filter(
        date__gte=start_date, 
        date__lte=end_date
    ).aggregate(Sum('amount'))['amount__sum'] or 0.00

    # Combine all expenses
    total_net_expenses = Decimal(total_utility_expenses) + Decimal(total_booking_expenses)

    # Calculate net earnings (total earnings - total expenses)
    total_net_earnings = total_earnings_decimal - total_net_expenses

    # Calculate earnings per house (Excluding and Including VAT)
    houses = House.objects.all()
    house_earnings_data = []
    total_earnings_per_house = Decimal('0.00')

    for house in houses:
        house_earnings_excl_vat = HouseEarning.objects.filter(
            house=house, 
            month__year=current_year, 
            month__month=current_month
        ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')

        # Calculate earnings including VAT (19% VAT)
        house_earnings_incl_vat = house_earnings_excl_vat * Decimal('1.19')

        house_earnings_data.append({
            'house_name': house.name,
            'total_earnings_excl_vat': house_earnings_excl_vat,
            'total_earnings_incl_vat': house_earnings_incl_vat
        })

        # Add to total earnings across all houses
        total_earnings_per_house += house_earnings_excl_vat

    # Calculate the average earnings per house
    avg_earnings_per_house = total_earnings_per_house / len(houses) if len(houses) > 0 else 0.00

    # Get total VAT deductible (e.g., assume 19% for simplicity on total expenses)
    total_vat_deductible = total_net_expenses * Decimal('0.19')

    # Calculate net VAT
    net_vat = total_vat_collected - total_vat_deductible

    # Prepare the context for rendering the PDF
    context = {
        'total_earnings': total_earnings_decimal,
        'total_expenses': total_expenses,
        'total_utility_expenses': total_utility_expenses,
        'total_booking_expenses': total_booking_expenses,
        'total_net_earnings': total_net_earnings,
        'total_vat_collected': total_vat_collected,
        'total_vat_deductible': total_vat_deductible,
        'houses': houses,
        'total_net_expenses': total_net_expenses,
        'net_vat': net_vat,
        'house_earnings_data': house_earnings_data,
        'avg_earnings_per_house': avg_earnings_per_house,
        'time_period': time_period,
    }

    # Render HTML template for the PDF
    html_string = render_to_string('pdf_report_template.html', context)

    # Generate the PDF from HTML string
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    # Return PDF as response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financial_overview_report.pdf"'

    return response
