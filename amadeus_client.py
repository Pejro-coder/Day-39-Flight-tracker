import requests
# Guide for getting the access_token:
# https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/quick-start/#step-2-get-your-api-key


class AmadeusClient:
    BASE_URL = "https://test.api.amadeus.com"

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.access_token = None
        self.get_access_token()

    def get_access_token(self):
        response = requests.post(url=f"{AmadeusClient.BASE_URL}/v1/security/oauth2/token",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"},
                                 data=f"grant_type=client_credentials&client_id={self.key}&client_secret={self.secret}")

        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            print("✅ Successfully retrieved Amadeus access token.")
        else:
            print(f"❌ Failed to get Amadeus access token: {response.json()}")
