from django.urls import path
from Common.VIEW.Api.Self_Booking_Api import self_booking_api_flight_view

urlpatterns = [

path('api/travelport_api_search_flights', self_booking_api_flight_view.travelport_api_search_flights),

]