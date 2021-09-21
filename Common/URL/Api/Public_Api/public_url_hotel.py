from django.urls import path
from Common.VIEW.Api.Public_Api import public_api_hotel_view

urlpatterns = [

path('api/create_hotel_booking', public_api_hotel_view.create_hotel_booking),
path('api/search_hotel_booking', public_api_hotel_view.get_hotel_booking),

]