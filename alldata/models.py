from django.db import models
from account.models import User

class Annote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default= 1)
    image_name = models.CharField(max_length= 200, blank=False)          # unique=True
    bounding_boxes = models.JSONField(default=list, null= True)
    image_data = models.TextField(max_length=5000000, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)