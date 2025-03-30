from twilio.rest import Client

class NotificationManager:
    MOJA_TELEFONSKA = ""


    def __init__(self, twilio_sid, twilio_auth_token):
        self.twilio_SID = twilio_sid
        self.twilio_auth_token = twilio_auth_token

    def send_sms(self, iata_code, city, cheapest_price, sheety_price):
        client = Client(self.twilio_SID, self.twilio_auth_token)

        message_body = (f"Flight deal alert for {city} ({iata_code})! The cheapest price is ${cheapest_price}, "
                        f"but Sheety has a price of ${sheety_price}. Don't miss out!")

        message = client.messages.create(
            body=message_body,
            from_="+17622526914",
            to=NotificationManager.MOJA_TELEFONSKA
        )

        print(message_body)
        print(message.status)
