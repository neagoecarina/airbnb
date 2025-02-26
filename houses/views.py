from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import House, Booking
from datetime import datetime, timedelta
import json
# View to list all houses
def houses(request):
    myhouses = House.objects.all()  # Query all houses from the database
    return render(request, 'houses/all_houses.html', {'myhouses': myhouses})

# View for house details
def house_detail(request, house_id):
    myhouse = get_object_or_404(House, id=house_id)

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            Booking.objects.create(
                house=myhouse,
                customer_name="Anonymous",
                start_date=start_date,
                end_date=end_date
            )
            return JsonResponse({"success": True})

    # Get all booked dates for this house
    booked_ranges = Booking.objects.filter(house=myhouse)
    booked_dates = []
    for booking in booked_ranges:
        current_date = booking.start_date
        while current_date <= booking.end_date:
            booked_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

    # Pass booked_dates to the template
    return render(request, 'houses/details.html', {'myhouse': myhouse, 'booked_dates': json.dumps(booked_dates)})