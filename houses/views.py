from django.shortcuts import render, get_object_or_404, redirect
from .models import House, Booking
from django.http import HttpResponse

# View to list all houses
def houses(request):
    myhouses = House.objects.all()  # Query all houses from the database
    return render(request, 'houses/all_houses.html', {'myhouses': myhouses})

# View for house details
def house_detail(request, house_id):
    # Fetch the house using its ID
    myhouse = get_object_or_404(House, id=house_id)

    # Handle the booking form submission
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if start_date and end_date:
            # Create a new booking for the selected house
            booking = Booking(
                house=myhouse,
                customer_name="Anonymous",  # You can extend this for real customer data
                start_date=start_date,
                end_date=end_date
            )
            booking.save()

            # Redirect or show a success message
            return HttpResponse("Booking successfully created!")

    # Render the house detail page with calendar
    return render(request, 'houses/details.html', {'myhouse': myhouse})
