from django.contrib import admin
from .models import *


@admin.register(Annote)
class AnnoteAdmin(admin.ModelAdmin):
    list_display = ['id','user']    ## 'obj_class'
