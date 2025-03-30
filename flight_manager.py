import requests
import time


class FlightManager:
    # API location: https://developers.amadeus.com/self-service/category/flights/api-doc/airport-and-city-search/api-reference
    AIRPORT_AND_CITY_SEARCH_API = "https://test.api.amadeus.com/v1/reference-data/locations"
    # API location: https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api-reference
    FLIGHT_OFFERS_API = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def __init__(self, amadeus_access_token, sheety_client, notification_manager):
        self.notification_manager = notification_manager
        self.sheety_client = sheety_client
        self.amadeus_access_token = amadeus_access_token

    # method which fills out  missing IATA codes based on "city name"
    def search_save_iata_code(self, row):
        iata_code = row["iataCode"]
        key = row["id"]
        city = row["city"].lower()
        try:
            if iata_code == "":
                print(f"IATA code missing for row {key}.")
                parameters = {"subType": "AIRPORT",
                              "keyword": city}

                iata_search_api_response = requests.get(url=FlightManager.AIRPORT_AND_CITY_SEARCH_API,
                                                        headers={
                                                            "Authorization": f"Bearer {self.amadeus_access_token}"},
                                                        params=parameters)
                # handling the server timeout
                if iata_search_api_response.status_code == 429:
                    time.sleep(0.5)
                    iata_search_api_response = requests.get(url=FlightManager.AIRPORT_AND_CITY_SEARCH_API,
                                                            headers={
                                                                "Authorization": f"Bearer {self.amadeus_access_token}"},
                                                            params=parameters)

                city_airport = iata_search_api_response.json()
                iata_code = city_airport["data"][0]["iataCode"]

                # Putting the IATA codes in the sheet
                self.sheety_client.write_sheety_data(iata_code, key, city)

                # returning false to use it in main to print a notification for all iata codes already added
                return 1
            else:
                print(f"......{iata_code} for {city} already added, row key: {key}")
                return 0

        except Exception as e:
            print(
                f"❌ An error occurred for row with city '{self.row.get('city')}': {e}. Possible error reason is missing price "
                f"in sheet or the country not represented in test API.")
            return 0

    # method whic sends an SMS with notification manager, if there i
    def compare_prices(self, row):
        iata_code = row["iataCode"]
        key = row["id"]
        city = row["city"].lower()
        sheety_price = row["lowestPrice"]
        # key 2 is used as depart location, that's why if key > 2
        if key > 2:
            print(f"Searching for lowest price, row: {key} iata code : {iata_code}")
            parameters = {"originLocationCode": "CDG",
                          "destinationLocationCode": iata_code,
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
                # first cheapest price (gets overwriten if a chepaer price is found later)
                cheapest_price = data["data"][0]["price"]["total"]
                print("--------------------CHEAPEST PRICE:", cheapest_price)
                for item in data["data"]:
                    price = item["price"]["total"]
                    # tole pogrutnaj kaj je fora tukaj...če sploh to tu kaj naredi, ker zgoraj iteriram čez vsak row v shettu, zato timeout potreben
                    if amadeus_api_response.status_code == 429:
                        time.sleep(0.5)
                        response = requests.get(url=FlightManager.FLIGHT_OFFERS_API,
                                                headers={"Authorization": f"Bearer {self.amadeus_access_token}"},
                                                params=parameters)
                    if price < cheapest_price:
                        cheapest_price = price

                print("current price:", cheapest_price)
                print("sheety price:", sheety_price)

                if float(cheapest_price) < sheety_price:
                    print("\nWE FOUND A LOWER PRICE\n")
                    self.notification_manager.send_sms(iata_code=iata_code,
                                                       city=city,
                                                       cheapest_price=cheapest_price,
                                                       sheety_price=sheety_price)

            except Exception as e:
                print(f"❌ {e}, possibly no data for {city.title()} - {iata_code}.")
        else:
            print(f"Skipping because this is the depart location: {iata_code}")
