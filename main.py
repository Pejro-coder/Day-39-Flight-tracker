import requests
import time
from pprint import pprint

amadeus_flight_client_API_key = "nX7rnwG7X1CdN3uylrYfeGNRleS4kMqp"
amadeus_flight_client_API_secret = "X4qlQ84auK1dU98z"

# -------------------------------- READ GOOGLE SHEET WITH SHEETY --------------------------------
sheety_endpoint = "https://api.sheety.co/0fd8b882fdcc644ed28a11adcf6f5b4c/flightDeals/prices"
sheety_authorization_token = "321adsac"

response = requests.get(url=sheety_endpoint,
                        headers={"Authorization": f"Bearer {sheety_authorization_token}"}
                        )

sheety_data = response.json()

# -------------------------------- AMADEUS FLIGHT PRICES --------------------------------
# ------ Get the ACCESS TOKEN.
# Guide is here: https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/quick-start/#step-2-get-your-api-key
response = requests.post(url="https://test.api.amadeus.com/v1/security/oauth2/token",
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         data=f"grant_type=client_credentials&client_id={amadeus_flight_client_API_key}&client_secret={amadeus_flight_client_API_secret}")

auth_response = response.json()
if "access_token" not in auth_response:
    print("Failed to retrieve access token", auth_response)

amadeus_access_token = auth_response["access_token"]

# ------ Adding IATA codes to empty fields in GOOGLE Sheets with sheety
# API location: https://developers.amadeus.com/self-service/category/flights/api-doc/airport-and-city-search/api-reference
airport_and_city_search_API_endpoint = "https://test.api.amadeus.com/v1/reference-data/locations"

# inserting IATA CODES for each City found in sheety
all_rows_full = True
for row in sheety_data["prices"]:
    if row["iataCode"] == "":
        all_rows_full = False
        # city is used for Amadeus API parameters, to get data for my cities
        city = row["city"].lower()
        # key is used later, to "put" the iatta codes in the correct row
        key = row["id"]
        parameters = {"subType": "AIRPORT",
                      "keyword": city}

        response = requests.get(url=airport_and_city_search_API_endpoint,
                                headers={"Authorization": f"Bearer {amadeus_access_token}"},
                                params=parameters)
        # handling the server timeout
        if response.status_code == 429:
            time.sleep(0.5)
            response = requests.get(url=airport_and_city_search_API_endpoint,
                                    headers={"Authorization": f"Bearer {amadeus_access_token}"},
                                    params=parameters)

        city_airport = response.json()
        iata_code = city_airport["data"][0]["iataCode"]

        # Putting the IATA codes in the sheet
        body = {
            "price": {
                "iataCode": iata_code,
            }
        }
        response = requests.put(url=f"{sheety_endpoint}/{key}",
                                 headers={"Authorization": f"Bearer {sheety_authorization_token}"},
                                 json=body)
        print("Finding the IATA code, updating sheet...", "Adding:", city.title())
        # print("put response status code:", response.status_code)

if all_rows_full:
    print("all IATA codes are already in the sheet")
    # if row["iataCode"] == "":
    #     print(row)




# # ----------  get the "cheap" flights.
# # API location: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-inspiration-search/api-reference
# flight_inspiration_search_API_endpoint = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
# parameters = {"origin": "PAR",
#               "maxPrice": 250}
# response = requests.get(url=flight_inspiration_search_API_endpoint,
#                         headers={"Authorization": f"Bearer {access_token}"},
#                         params=parameters)
#
# flights = response.json()["data"]
# for flight in flights:
#     print(flight)
# # pprint(flights)
#
# print("\n\n---------------------\n\n")
