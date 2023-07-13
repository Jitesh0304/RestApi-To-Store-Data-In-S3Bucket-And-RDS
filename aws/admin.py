from django.contrib import admin
from .models import AwsCredential


@admin.register(AwsCredential)
class AwsAdmin(admin.ModelAdmin):
    list_display = ['user','accessID','secretKey','bucketName','regionName']