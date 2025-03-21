from amadeus_client import AmadeusClient
from sheety_client import SheetyClient
from flight_manager import FlightManager
from notification_manager import NotificationManager
from dotenv import load_dotenv
import os



amadeus_flight_client_API_key = "nX7rnwG7X1CdN3uylrYfeGNRleS4kMqp"
amadeus_flight_client_API_secret = "X4qlQ84auK1dU98z"
sheety_authorization_token = "321adsac"

load_dotenv("C:/Users/peter/EnvironmentVariables/.env")
twilio_SID = os.getenv("TWILIO_account_sid")
twilio_auth_token = os.getenv("TWILIO_auth_token")


# -------------------------- GETTING AMADEUS ACCESS TOKEN ----------------------------
amadeus = AmadeusClient(amadeus_flight_client_API_key, amadeus_flight_client_API_secret)
amadeus_access_token = amadeus.access_token

# ------------------------ READING GOOGLE SHEET WITH SHEETY --------------------------
sheety = SheetyClient(sheety_authorization_token)
sheety.get_sheety_data()
sheety_data = sheety.data

# ------------------------ Notification manager ----------------------------
notification_manager = NotificationManager(twilio_SID, twilio_auth_token)

# -------- Adding IATA codes to empty fields in Google Sheets with sheety ------------
print(f"3. Searching for missing IATA codes, finding cheapest price.\n")

rows_with_no_code = 0
for row in sheety_data["prices"]:
    flight_manager = FlightManager(row, amadeus_access_token, sheety, notification_manager)
    rows_with_no_code += flight_manager.search_save_iata_code()
    flight_manager.compare_prices()
    print()

if rows_with_no_code == 0:
    print("\nAll possible IATA codes are already in the sheet, no new IATA code was added.")
