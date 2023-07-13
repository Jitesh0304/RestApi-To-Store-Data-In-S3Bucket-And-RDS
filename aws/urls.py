from django.urls import path
from . import views



urlpatterns = [
    path('cloud/', views.AWSview.as_view()),
]
