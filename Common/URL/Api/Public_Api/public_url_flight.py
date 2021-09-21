from django.urls import path
from Common.VIEW.Api.Public_Api import public_api_flight_view

urlpatterns = [

path('api/create_flight_booking', public_api_flight_view.create_flight_booking),
path('api/search_flight_booking', public_api_flight_view.get_flight_booking),

]