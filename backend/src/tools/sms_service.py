from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class SMSService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def send_sms(self, to_number, message):
        try:

            to_number = self.format_phone_number(to_number)
            

            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                'success': True,
                'sid': message.sid,
                'status': message.status
            }
        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e)
            }
        

    def format_phone_number(self, number):
        
       
        number = ''.join(filter(str.isdigit, number))
        
        if len(number) == 9:
            return f'+963{number}'
        elif len(number) == 10 and number.startswith('0'):
            return f'+963{number[1:]}'
        elif len(number) == 12 and number.startswith('963'):
            return f'+{number}'
        elif len(number) == 13 and number.startswith('+963'):
            return number
        else:
            return f'+{number}'