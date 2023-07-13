from django.contrib import admin
from .models import *


@admin.register(AwsAnnote)
class AwsAnnoteAdmin(admin.ModelAdmin):
    list_display = ['id','user','image_name']