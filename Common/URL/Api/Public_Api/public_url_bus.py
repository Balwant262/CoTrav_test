from django.urls import path
from Common.VIEW.Api.Public_Api import public_api_bus_view

urlpatterns = [

path('api/create_bus_booking', public_api_bus_view.create_bus_booking),
path('api/search_bus_booking', public_api_bus_view.get_bus_booking),


]