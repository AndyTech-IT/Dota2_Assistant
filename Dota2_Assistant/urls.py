"""
Definition of urls for Dota2_Starter_Purchase_Assistant.
"""

from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path('', include('home.urls')),
    path('home/', include('home.urls')),
    path('Home/', include('home.urls')),
    path('matches/', include('match_history.urls')),
    path('Matches/', include('match_history.urls')),
    path('admin/', admin.site.urls),
]
