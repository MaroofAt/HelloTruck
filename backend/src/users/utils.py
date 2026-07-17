
import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import User_OTP
from tools.sms_service import SMSService  
from twilio.rest import Client




def generate_otp():
    # TODO if we want to use pyotp package to generate the OTP
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)  # 5 minutes validity
    return totp.now()

def send_otp_email_to_user(email):
    gotp = generate_otp()
    otp_expiry = datetime.now() + timedelta(minutes=5) 

    # user.otp = otp
    # user.otp_created_at = datetime.now()
    # user.save()

    otp_table = User_OTP.objects.create(
        otp = gotp
    )
    otp_table.save()
    
    subject = 'Email Verification OTP'
    message = f'Your OTP for email verification is: {gotp}\nThis OTP is valid for 5 minutes.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    

    send_mail(subject, message,email_from, recipient_list , fail_silently=False)


def send_otp_by_sms(phone_number):
    """Send OTP via SMS"""
    gotp = generate_otp()

    otp_table = User_OTP.objects.create(
        otp = gotp
    )
    otp_table.save()

    message = f'Your OTP for verification is: {otp_table}. Valid for 5 minutes.'
    
    sms_service = SMSService()
    result = SMSService.send_sms(sms_service ,to_number=phone_number , message=message)
    
    if result['success']:
        return True, result
    else:
        return False, result
    

def send_otp_by_whatsapp(phone_number, otp):
    
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        

        from_whatsapp = f'whatsapp:{settings.TWILIO_PHONE_NUMBER}'
        to_whatsapp = f'whatsapp:{phone_number}'
        
        message = client.messages.create(
            body=f'Your OTP for verification is: {otp}. Valid for 5 minutes.',
            from_=from_whatsapp,
            to=to_whatsapp
        )
        
        return True, {'sid': message.sid}
    except Exception as e:
        return False, {'error': str(e)}