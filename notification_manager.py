twilio_SID = ""
twilio_auth_token = ""
from twilio.rest import Client


class SendSMS:

    def __init__(self, twilio_sid, twilio_auth_token, iata_code, city, cheapest_price, sheety_price):
        self.twilio_SID = twilio_sid
        self.twilio_auth_token = twilio_auth_token
        self.iata_code = iata_code
        self.city = city
        self.cheapest_price = cheapest_price
        self.sheety_price = sheety_price

    def send_sms(self):
        client = Client(self.twilio_SID, self.twilio_auth_token)

        message_body = f"Flight deal alert for {self.city} ({self.iata_code})! The cheapest price is ${
        self.cheapest_price}, but Sheety has a price of ${self.sheety_price}. Don't miss out!"

        message = client.messages.create(
            body=message_body,
            from_="+17622526914",
            to="+38640555904",
        )

        print(message.status)


send_sms = SendSMS(twilio_SID, twilio_auth_token, "123", "Paris", "50", "100")
send_sms.send_sms()
