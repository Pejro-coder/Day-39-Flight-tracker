import requests
import datetime

client_API_key = ""
client_API_secret = ""
sheety_authorization = ""

# -------------------------------- AMADEUS FLIGHT PRICES --------------------------------
# get the access token
response = requests.post(url="https://test.api.amadeus.com/v1/security/oauth2/token",
                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                         data=f"grant_type=client_credentials&client_id={client_API_key}&client_secret={client_API_secret}")

# get the "cheap" flights
access_token = response.json()["access_token"]
api_endpoint = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
parameters = {"origin": "PAR",
              "maxPrice": 250}
response = requests.get(url=api_endpoint, headers={"Authorization": f"Bearer {access_token}"}, params=parameters)

flights = response.json()["data"]
# print(flights)

# -------------------------------- SHEETY UPDATE IATA CODES --------------------------------
sheety_endpoint = "https://api.sheety.co/0fd8b882fdcc644ed28a11adcf6f5b4c/flightDeals/prices"

response = requests.get(url=sheety_endpoint, headers={"Authorization": f"Bearer {sheety_authorization}"})
data = response.json()
print("sheety:", data)

# adding IATA codes to empty fields
for row in data["prices"]:
    if row["iataCode"] == "":
        # exception handling, because for some cities I don't get any adata back
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
                                    headers={"Authorization": f"Bearer {sheety_authorization}"},
                                    json={"price": {"iataCode": code}})


        except Exception as e:
            print("------ Exception:", e)
