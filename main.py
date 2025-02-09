import requests
import time
import json
from pprint import pprint

amadeus_flight_client_API_key = "nX7rnwG7X1CdN3uylrYfeGNRleS4kMqp"
amadeus_flight_client_API_secret = "X4qlQ84auK1dU98z"

# -------------------------------- READ GOOGLE SHEET WITH SHEETY --------------------------------
sheety_endpoint = "https://api.sheety.co/0fd8b882fdcc644ed28a11adcf6f5b4c/flightDeals/prices"
sheety_authorization_token = "321adsac"

sheety_get_response = requests.get(url=sheety_endpoint,
                        headers={"Authorization": f"Bearer {sheety_authorization_token}"}
                        )

sheety_data = sheety_get_response.json()
print(f"1. getting sheet data. Status code: {sheety_get_response.status_code}\n")

# -------------------------------- AMADEUS ACCESS TOKEN --------------------------------
# Guide is here: https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/quick-start/#step-2-get-your-api-key
amadeus_token_response = requests.post(url="https://test.api.amadeus.com/v1/security/oauth2/token",
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         data=f"grant_type=client_credentials&client_id={amadeus_flight_client_API_key}&client_secret={amadeus_flight_client_API_secret}")

amadeus_response_data = amadeus_token_response.json()
if "access_token" not in amadeus_response_data:
    print("Failed to retrieve access token", amadeus_response_data)

print(f"2. getting amadeus access token. Status code: {amadeus_token_response.status_code}\n")

amadeus_access_token = amadeus_response_data["access_token"]

# ------------ Adding IATA codes to empty fields in Google Sheets with sheety ------------
# API location: https://developers.amadeus.com/self-service/category/flights/api-doc/airport-and-city-search/api-reference
airport_and_city_search_API_endpoint = "https://test.api.amadeus.com/v1/reference-data/locations"

print(f"3. Searching for missing IATA codes, finding cheapest price.\n")

all_rows_full = True
for row in sheety_data["prices"]:
    sheety_price = row["lowestPrice"]
    iata_code = row["iataCode"]
    # key is used later, to "put" the iatta codes in the correct row
    key = row["id"]
    # city is used for Amadeus API parameters, to get data for my cities
    city = row["city"].lower()
    try:
        if iata_code == "":
            all_rows_full = False
            key = row["id"]
            print(f"IATA code missing for row {key}.")
            parameters = {"subType": "AIRPORT",
                          "keyword": city}

            iata_search_API_response = requests.get(url=airport_and_city_search_API_endpoint,
                                                    headers={"Authorization": f"Bearer {amadeus_access_token}"},
                                                    params=parameters)
            # handling the server timeout
            if iata_search_API_response.status_code == 429:
                time.sleep(0.5)
                response = requests.get(url=airport_and_city_search_API_endpoint,
                                        headers={"Authorization": f"Bearer {amadeus_access_token}"},
                                        params=parameters)

            city_airport = iata_search_API_response.json()
            iata_code = city_airport["data"][0]["iataCode"]

            # Putting the IATA codes in the sheet
            body = {
                "price": {
                    "iataCode": iata_code,
                }
            }
            sheety_put_response = requests.put(url=f"{sheety_endpoint}/{key}",
                                    headers={"Authorization": f"Bearer {sheety_authorization_token}"},
                                    json=body)
            print("Finding the IATA code, updating sheet...", "Adding:", city.title(), "as", iata_code)
            # print("put response status code:", response.status_code)
        else:
            print(f"......{iata_code} for {city} already added")

    except Exception as e:
        print(f"An error occurred for row with city '{row.get('city')}': {e}. Possible error reason is missing price "
              f"in sheet or the country not represented in test API.")

    # ------------------------------------ Finding the currently cheapest price ------------------------------------
    flight_offers_API_endpoint = "https://test.api.amadeus.com/v2/shopping/flight-offers"
#
#     # skipping key 2, because in the current sheet key 2 is the departure location
#     if key > 2:
#         print(f"Searching for lowest price, row: {key} iata code : {iata_code}")
#         parameters = {"originLocationCode": "CDG",
#                       "destinationLocationCode": iata_code,
#                       "departureDate": "2025-04-02",
#                       "returnDate": "2025-04-05",
#                       "adults": 1,
#                       "nonStop": "true",
#                       "travelClass": "ECONOMY",
#                       "max": 20,
#                       "currencyCode": "EUR"
#                       }
#
#         amadeus_API_response = requests.get(url=flight_offers_API_endpoint,
#                                 headers={"Authorization": f"Bearer {amadeus_access_token}"},
#                                 params=parameters)
#
#         print("flight offers response:", amadeus_API_response)
#         data = amadeus_API_response.json()
#         print(json.dumps(data, indent=2))
#
#         try:
#             cheapest_price = data["data"][0]["price"]["total"]
#             for item in data["data"]:
#                 price = item["price"]["total"]
#                 # tole pogrutnaj kaj je fora tukaj...če sploh to tu kaj naredi, ker zgoraj iterejtam čez vsak row v shettu, zato timeout potreben
#                 if amadeus_API_response.status_code == 429:
#                     time.sleep(0.5)
#                     response = requests.get(url=flight_offers_API_endpoint,
#                                             headers={"Authorization": f"Bearer {amadeus_access_token}"},
#                                             params=parameters)
#                 if price < cheapest_price:
#                     cheapest_price = price
#
#             print("current price:", cheapest_price)
#             print("sheety price:", sheety_price)
#
#             if float(cheapest_price) < sheety_price:
#                 print("EMAIL!!!!!!!!!!!!!EMAIL!!!!!!!!!!!!!EMAIL!!!!!!!!!!!!!")
#
#         except Exception as e:
#             print(f"{e}, possibly no data for {city.title()} - {iata_code}.")
#     else:
#         print(f"Skipping because this is the depart location: {iata_code}")
#
#     print()
# if all_rows_full:
#     print("\nAll possible IATA codes are already in the sheet, no new IATA code was added.")

# ---- just for testing, delete when checking single iata code is finished
parameters = {"originLocationCode": "CDG",
              "destinationLocationCode": "MUC",
              "departureDate": "2025-04-02",
              "returnDate": "2025-04-05",
              "adults": 1,
              "nonStop": "true",
              "travelClass": "ECONOMY",
              "max": 50,
              "currencyCode": "EUR"
              }

response = requests.get(url=flight_offers_API_endpoint,
                        headers={"Authorization": f"Bearer {amadeus_access_token}"},
                        params=parameters)

print("flight offers response:", response)
data = response.json()

print(data)
# print(json.dumps(data, indent=2))
