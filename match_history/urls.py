from django.urls import path, include
from match_history import views

app_name = 'Matches'

urlpatterns = [
	path('Page<int:page_number>', views.GetMatches, name = 'GetMatches'),
	path('update_heroes', views.Update_Hereos, name='update_heroes'),
	path('update_items', views.Update_Items, name='update_items'),
	]
