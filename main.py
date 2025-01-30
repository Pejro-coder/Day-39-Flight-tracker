import requests
import datetime
from pprint import pprint


# -------------------------------- READ GOOGLE SHEET WITH SHEETY --------------------------------
sheety_endpoint = "https://api.sheety.co/0fd8b882fdcc644ed28a11adcf6f5b4c/flightDeals/prices"
sheety_authorization_token = "321adsac"

response = requests.get(url=sheety_endpoint, headers={"Authorization": f"Bearer {sheety_authorization_token}"})
data = response.json()
for row in data["prices"]:
    print(row)

# -------------------------------- AMADEUS FLIGHT PRICES --------------------------------
amadeus_flight_client_API_key = "nX7rnwG7X1CdN3uylrYfeGNRleS4kMqp"
amadeus_flight_client_API_secret = "X4qlQ84auK1dU98z"

# Get the ACCESS TOKEN.
# Guide is here: https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/quick-start/#step-2-get-your-api-key
response = requests.post(url="https://test.api.amadeus.com/v1/security/oauth2/token",
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         data=f"grant_type=client_credentials&client_id={amadeus_flight_client_API_key}&client_secret={amadeus_flight_client_API_secret}")

print("\nAmadeus access token response code:", response)
access_token = response.json()["access_token"]
print("access token:", access_token)

# get the "cheap" flights
api_endpoint = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
parameters = {"origin": "PAR",
              "maxPrice": 250}
response = requests.get(url=api_endpoint, headers={"Authorization": f"Bearer {access_token}"}, params=parameters)

flights = response.json()["data"]
pprint(flights)

print("\n\n---------------------\n\n")

# adding IATA codes to empty fields in SHEET with sheety
for row in data["prices"]:
    if row["iataCode"] == "":
        # exception handling, because for some cities I don't get any data back
        try:
            city = row["city"].lower()
            id = row["id"]
            print(id, city)

            # get IATA code based on the "city" parameter
            parameters = {"subType": "CITY",
                          "keyword": city}
            response = requests.get(url="https://test.api.amadeus.com/v1/reference-data/locations",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    params=parameters)
            print(response.json())
            code = response.json()["data"][0]["iataCode"]

            # add missing codes to the sheet with a put method
            response = requests.put(url=f"{sheety_endpoint}/{row['id']}",
                                    headers={"Authorization": f"Bearer {sheety_authorization_token}"},
                                    json={"price": {"iataCode": code}})


        except Exception as e:
            print("------ Exception:", e)
