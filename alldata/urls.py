from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('annot/', views.AnnoteView.as_view()),
    path('annot/<str:nm>', views.AnnoteView.as_view()),
]
