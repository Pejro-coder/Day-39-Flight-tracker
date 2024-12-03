import requests
import datetime


# -------------------------------- AMADEUS FLIGHT PRICES --------------------------------
client_id = 'nX7rnwG7X1CdN3uylrYfeGNRleS4kMqp'
client_secret = 'X4qlQ84auK1dU98z'

# Authenticate with Amadeus API
auth_response = requests.post(
    'https://test.api.amadeus.com/v1/security/oauth2/token',
    headers={'Content-Type': 'application/x-www-form-urlencoded'},
    data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
)

auth_data = auth_response.json()
access_token = auth_data['access_token']

# Define the headers for the API request
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Set up the parameters for finding destinations from Paris
origin = 'CDG'  # Paris Charles de Gaulle Airport IATA code
max_price = 300  # Maximum price in EUR
current_date = datetime.datetime.now().date()
end_date = current_date + datetime.timedelta(days=9 * 30)  # 9 months from today
departure_date = current_date.strftime('%Y-%m-%d')
return_date = end_date.strftime('%Y-%m-%d')

# Endpoint for searching for flight offers
url = (f'https://test.api.amadeus.com/v1/shopping/flight-offers?originLocationCode={origin}&departureDate='
       f'{departure_date}&returnDate={return_date}&adults=1&maxPrice={max_price}')

# Get flight offers
response = requests.get(url, headers=headers)

if response.status_code == 200:
    flight_data = response.json()
    # Check and print out destinations within the price limit
    for offer in flight_data.get('data', []):
        destination_code = offer['itineraries'][0]['segments'][0]['destination']['iataCode']
        price = float(offer['price']['total'])

        if price <= max_price:
            print(f"Destination: {destination_code}, Price: €{price}")
else:
    print("Failed to retrieve data:", response.status_code, response.text)
