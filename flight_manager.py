import requests
import time


class FlightManager:
    # API location: https://developers.amadeus.com/self-service/category/flights/api-doc/airport-and-city-search/api-reference
    AIRPORT_AND_CITY_SEARCH = "https://test.api.amadeus.com/v1/reference-data/locations"
    FLIGHT_OFFERS_API = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def __init__(self, row, amadeus_access_token, sheety_client, notification_manager):
        self.notification_manager = notification_manager
        self.row = row
        self.sheety_client = sheety_client

        self.iata_code = self.row["iataCode"]
        self.sheety_price = self.row["lowestPrice"]
        # key is used later, to "put" the iata codes in the correct row
        self.key = self.row["id"]
        # city is used for Amadeus API parameters, to get data for my cities
        self.city = self.row["city"].lower()
        self.amadeus_access_token = amadeus_access_token

    def search_save_iata_code(self):
        try:
            if self.iata_code == "":
                print(f"IATA code missing for row {self.key}.")
                parameters = {"subType": "AIRPORT",
                              "keyword": self.city}

                iata_search_api_response = requests.get(url=FlightManager.AIRPORT_AND_CITY_SEARCH,
                                                        headers={
                                                            "Authorization": f"Bearer {self.amadeus_access_token}"},
                                                        params=parameters)
                # handling the server timeout
                if iata_search_api_response.status_code == 429:
                    time.sleep(0.5)
                    iata_search_api_response = requests.get(url=FlightManager.AIRPORT_AND_CITY_SEARCH,
                                                            headers={
                                                                "Authorization": f"Bearer {self.amadeus_access_token}"},
                                                            params=parameters)

                city_airport = iata_search_api_response.json()
                self.iata_code = city_airport["data"][0]["iataCode"]

                # Putting the IATA codes in the sheet
                self.sheety_client.write_sheety_data(self.iata_code, self.key, self.city)

                # returning false to use it in main to print a notification for all iata codes already added
                return 1
            else:
                print(f"......{self.iata_code} for {self.city} already added")
                return 0

        except Exception as e:
            print(
                f"❌ An error occurred for row with city '{self.row.get('city')}': {e}. Possible error reason is missing price "
                f"in sheet or the country not represented in test API.")
            return 0

    def compare_prices(self):
        if self.key > 2:
            print(f"Searching for lowest price, row: {self.key} iata code : {self.iata_code}")
            parameters = {"originLocationCode": "CDG",
                          "destinationLocationCode": self.iata_code,
                          "departureDate": "2025-04-02",
                          "returnDate": "2025-04-05",
                          "adults": 1,
                          "nonStop": "true",
                          "travelClass": "ECONOMY",
                          "max": 20,
                          "currencyCode": "EUR"
                          }

            amadeus_api_response = requests.get(url=FlightManager.FLIGHT_OFFERS_API,
                                                headers={"Authorization": f"Bearer {self.amadeus_access_token}"},
                                                params=parameters)

            print("flight offers response:", amadeus_api_response)
            data = amadeus_api_response.json()
            # print(json.dumps(data, indent=2))

            try:
                cheapest_price = data["data"][0]["price"]["total"]
                for item in data["data"]:
                    price = item["price"]["total"]
                    # tole pogrutnaj kaj je fora tukaj...če sploh to tu kaj naredi, ker zgoraj iterejtam čez vsak row v shettu, zato timeout potreben
                    if amadeus_api_response.status_code == 429:
                        time.sleep(0.5)
                        response = requests.get(url=FlightManager.FLIGHT_OFFERS_API,
                                                headers={"Authorization": f"Bearer {self.amadeus_access_token}"},
                                                params=parameters)
                    if price < cheapest_price:
                        cheapest_price = price

                print("current price:", cheapest_price)
                print("sheety price:", self.sheety_price)

                if float(cheapest_price) < self.sheety_price:
                    self.notification_manager.send_sms(iata_code=self.iata_code,
                                                       city=self.city,
                                                       cheapest_price=cheapest_price,
                                                       sheety_price=self.sheety_price)

            except Exception as e:
                print(f"{e}, possibly no data for {self.city.title()} - {self.iata_code}.")
        else:
            print(f"Skipping because this is the depart location: {self.iata_code}")
