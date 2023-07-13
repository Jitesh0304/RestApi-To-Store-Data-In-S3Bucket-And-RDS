from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User



def sent_otp_by_email(email):
    subject = "Your account verification email.."
    otp = random.randint(1000,9999)
    message = f"Your OTP for account verification is {otp}"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.otp = otp
    user_obj.save()



def reset_pass_email(email):
    subject = "Your account verification email.."
    otp = random.randint(1000,9999)
    message = f"Your OTP for forgot password is {otp}"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.otp = otp
    user_obj.is_verified = False
    user_obj.save()

    