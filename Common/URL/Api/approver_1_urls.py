from django.urls import path,include
from Common.VIEW.Api import approver_1_api_view

urlpatterns = [
    path('api/approver_1_taxi_bookings', approver_1_api_view.approver_1_taxi_bookings),
    path('api/approver_1_accept_taxi_booking', approver_1_api_view.approver_1_accept_taxi_booking),
    path('api/approver_1_reject_taxi_booking', approver_1_api_view.approver_1_reject_taxi_booking),

    path('api/approver_1_bus_bookings', approver_1_api_view.approver_1_bus_bookings),
    path('api/approver_1_accept_bus_booking', approver_1_api_view.approver_1_accept_bus_booking),
    path('api/approver_1_reject_bus_booking', approver_1_api_view.approver_1_reject_bus_booking),

    path('api/approver_1_train_bookings', approver_1_api_view.approver_1_train_bookings),
    path('api/approver_1_accept_train_booking', approver_1_api_view.approver_1_accept_train_booking),
    path('api/approver_1_reject_train_booking', approver_1_api_view.approver_1_reject_train_booking),

    path('api/approver_1_hotel_bookings', approver_1_api_view.approver_1_hotel_bookings),
    path('api/approver_1_accept_hotel_booking', approver_1_api_view.approver_1_accept_hotel_booking),
    path('api/approver_1_reject_hotel_booking', approver_1_api_view.approver_1_reject_hotel_booking),

    path('api/approver_1_flight_bookings', approver_1_api_view.approver_1_flight_bookings),
    path('api/approver_1_accept_flight_booking', approver_1_api_view.approver_1_accept_flight_booking),
    path('api/approver_1_reject_flight_booking', approver_1_api_view.approver_1_reject_flight_booking),

    path('api/approver_1_accept_visa_booking', approver_1_api_view.approver_2_accept_visa_booking),
    path('api/approver_1_reject_visa_booking', approver_1_api_view.approver_2_reject_visa_booking),

    path('api/approver_1_accept_frro_booking', approver_1_api_view.approver_2_accept_frro_booking),
    path('api/approver_1_reject_frro_booking', approver_1_api_view.approver_2_reject_frro_booking),

    path('api/approver_1_accept_guesthouse_booking', approver_1_api_view.approver_1_accept_guesthouse_booking),
    path('api/approver_1_reject_guesthouse_booking', approver_1_api_view.approver_1_reject_guesthouse_booking),
]