from django.db import models
from django.contrib.auth.models import User
from datetime import datetime , timedelta


# Create your models here.
class OtpModel(models.Model):
    otp = models.IntegerField()
    otp_created_at = models.DateTimeField(auto_now_add=datetime.now(), null=True , blank=True)
    user_id = models.OneToOneField(User , on_delete=models.CASCADE)

    def otp_is_valid(self , submitted_otp):
        if self.otp == submitted_otp:
            now = datetime.now()
            return (self.otp_created_at + timedelta(minutes=10)) <= now
        return False