import requests


class SheetyClient:
    SHEETY_ENDPOINT = "https://api.sheety.co/0fd8b882fdcc644ed28a11adcf6f5b4c/flightDeals/prices"

    def __init__(self, authorization_token):
        self.token = authorization_token
        self.data = None
        self.get_sheety_data()

    def get_sheety_data(self):
        response = requests.get(url=SheetyClient.SHEETY_ENDPOINT,
                                headers={"Authorization": f"Bearer {self.token}"}
                                )

        if response.status_code == 200:
            self.data = response.json()
            print("✅ Retrieved sheety data successfully.")
        else:
            print(f"❌ Failed to get Sheety data: {response.json()}")

    def write_sheety_data(self, iata_code, key, city):
        # Putting the IATA codes in the sheet
        body = {
            "price": {
                "iataCode": iata_code,
            }
        }
        sheety_put_response = requests.put(url=f"{SheetyClient.SHEETY_ENDPOINT}/{key}",
                                           headers={"Authorization": f"Bearer {self.token}"},
                                           json=body)
        print(sheety_put_response.status_code)
        print("Finding the IATA code, updating sheet...", "Adding:", city.title(), "as", iata_code)
        # print("put response status code:", response.status_code)
