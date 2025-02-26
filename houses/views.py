from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import House, Booking
from datetime import datetime, timedelta
import json
from django.views.decorators.csrf import csrf_exempt

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
