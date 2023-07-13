from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('data/', views.AwsAnnoteView.as_view()),
    path('data/<str:nm>', views.AwsAnnoteView.as_view()),
]




#         python manage.py makemigrations account
#         python manage.py makemigrations alldata
#         python manage.py makemigrations aws
#         python manage.py makemigrations awsdata
#         python manage.py migrate
#         python manage.py createsuperuser