import requests

sheety_endpoint = "https://api.sheety.co/0fd8b882fdcc644ed28a11adcf6f5b4c/flightDeals/prices"
sheety_authorization_token = "321adsac"


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

