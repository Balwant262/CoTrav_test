from django.urls import path
from Common.VIEW.Api.Public_Api import public_api_taxi_view

urlpatterns = [

path('api/get_corporate_auth_token', public_api_taxi_view.get_corporate_auth_token),

path('api/create_taxi_booking', public_api_taxi_view.create_taxi_booking),
path('api/search_taxi_booking', public_api_taxi_view.get_taxi_booking),

]