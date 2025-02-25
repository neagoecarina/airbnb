from django.shortcuts import render
from .models import House

# View for the main page
def main(request):
    return render(request, 'houses/main.html')

# View for displaying all houses
def houses(request):
    all_houses = House.objects.all()  # Fetch all houses from the database
    return render(request, 'houses/houses.html', {'houses': all_houses})

# View for displaying house details
def details(request, id):
    myhouse = House.objects.get(id=id)  # Fetch a specific house by ID
    return render(request, 'houses/details.html', {'myhouse': myhouse})
