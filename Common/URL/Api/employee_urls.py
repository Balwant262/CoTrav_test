from django.urls import path,include
from Common.VIEW.Api import employee_api_view

urlpatterns = [
    path('api/employee_taxi_bookings', employee_api_view.employee_taxi_bookings),
    path('api/employee_bus_bookings', employee_api_view.employee_bus_bookings),
    path('api/employee_train_bookings', employee_api_view.employee_train_bookings),
    path('api/employee_hotel_bookings', employee_api_view.employee_hotel_bookings),
    path('api/employee_flight_bookings', employee_api_view.employee_flight_bookings),

    path('api/employee_visa_services', employee_api_view.employee_visa_services),

    path('api/employee_reject_taxi_booking', employee_api_view.employee_reject_taxi_bookings),
    path('api/employee_reject_bus_booking', employee_api_view.employee_reject_bus_bookings),
    path('api/employee_reject_train_booking', employee_api_view.employee_reject_train_bookings),
    path('api/employee_reject_hotel_booking', employee_api_view.employee_reject_hotel_bookings),
    path('api/employee_reject_flight_booking', employee_api_view.employee_reject_flight_bookings),

    path('api/employee_reject_guesthouse_booking', employee_api_view.employee_reject_guesthouse_bookings),

]