import requests
from django.conf import settings

# Function to fetch VAT data for a specific country and amount
def fetch_vat_rate(amount, country_code):
    # Construct the API URL
    api_url = 'http://apilayer.net/api/price'
    
    # Parameters to send with the API request
    params = {
        'access_key': settings.VAT_API_KEY,  # Your API key from settings
        'amount': amount,  # The amount you want to calculate the VAT for
        'country_code': country_code,  # Country code (e.g., 'GB' for United Kingdom)
        'type': 'vat'  # We're looking for VAT data
    }
    
    # Make the GET request to the API
    response = requests.get(api_url, params=params)
    
    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()  # Parse the JSON data
        if data.get("success"):
            # Return the calculated VAT amount
            return data.get("price")
        else:
            return None  # If something goes wrong with the API response
    else:
        return None  # If the API request fails
    

    # utils.py

def get_discounted_price(house_id, start_date, end_date):
    # Delay the import to avoid circular import issue
    from .models import Discount, House  # Import inside the function

    # Get the house object to access its price
    house = House.objects.get(id=house_id)
    
    # Original price is the price of the house
    original_price = house.price
    
    # Get all discounts applicable during the given period
    discounts = Discount.objects.filter(
        house_id=house_id,
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    # Apply any discounts if applicable
    for discount in discounts:
        original_price *= (1 - discount.discount_percentage / 100)

    return original_price


from datetime import timedelta
from decimal import Decimal


def calculate_total_booking_price_with_discounts(house_id, start_date, end_date):
    house = House.objects.get(id=house_id)
    base_price = house.price
    total_price = Decimal('0.00')

    # Get all discounts for the house that overlap the booking period
    discounts = Discount.objects.filter(
        house_id=house_id,
        start_date__lte=end_date,
        end_date__gte=start_date
    )

    # Map each discount day to its discount percentage
    discount_days = {}
    for discount in discounts:
        current = discount.start_date
        while current <= discount.end_date:
            if start_date <= current < end_date:
                discount_days[current] = discount.discount_percentage
            current += timedelta(days=1)

    # Calculate total price per night
    current = start_date
    while current < end_date:
        if current in discount_days:
            discount_percent = discount_days[current]
            daily_price = base_price * (1 - discount_percent / 100)
        else:
            daily_price = base_price
        total_price += daily_price
        current += timedelta(days=1)

    return round(total_price, 2)
