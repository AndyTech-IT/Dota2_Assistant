from django.urls import path
from home import views

app_name = 'Assistant_Home'

urlpatterns = [
    path('', views.StartPadge, name='StartPadge'),
    ]
