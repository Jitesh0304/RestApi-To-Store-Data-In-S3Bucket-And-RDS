from django.db import models
from account.models import User


class AwsCredential(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    accessID = models.CharField(max_length= 200, null= False, blank=False)
    secretKey = models.CharField(max_length= 200, null= False, blank=False)
    bucketName = models.CharField(max_length= 100, null=False, blank=False)
    regionName = models.CharField(max_length= 100, null=False, blank=False)

    