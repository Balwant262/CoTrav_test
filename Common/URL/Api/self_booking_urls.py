from django.urls import path,include
from Common.VIEW.Api import api_self_booking_view

urlpatterns = [

path('api/get_bus_booking_search_result', api_self_booking_view.get_bus_booking_search_result),


]