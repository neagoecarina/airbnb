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
