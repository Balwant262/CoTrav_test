from django.urls import path,include
from Common.VIEW.Approver_2 import approver_2_views

urlpatterns = [
    path('Corporate/Approver_2/logout', approver_2_views.logout_action),
    path('Corporate/Approver_2/home', approver_2_views.homepage),
    path('Corporate/Approver_2/user_profile', approver_2_views.user_profile),
    path('Corporate/Approver_2/company-billing_entities/<int:id>', approver_2_views.company_billing_entities),
    path('Corporate/Approver_2/company-rates/<int:id>', approver_2_views.company_rates),
    path('Corporate/Approver_2/company-groups/<int:id>', approver_2_views.company_groups),
    path('Corporate/Approver_2/view-company-group/<int:id>', approver_2_views.view_company_group),
    path('Corporate/Approver_2/company-subgroups/<int:id>', approver_2_views.company_subgroups),
    path('Corporate/Approver_2/view-company-subgroup/<int:id>', approver_2_views.view_company_subgroup),
    path('Corporate/Approver_2/company-admins/<int:id>', approver_2_views.company_admins),
    path('Corporate/Approver_2/company-spocs/<int:id>', approver_2_views.company_spocs),
    path('Corporate/Approver_2/company-employees/<int:id>', approver_2_views.company_employees),

    path('Corporate/Approver_2/taxi-bookings/<int:id>', approver_2_views.taxi_bookings),
    path('Corporate/Approver_2/view-taxi-booking/<int:id>', approver_2_views.view_taxi_booking),
    path('Corporate/Approver_2/accept-taxi-booking/<int:id>', approver_2_views.accept_taxi_booking),
    path('Corporate/Approver_2/reject-taxi-booking/<int:id>', approver_2_views.reject_taxi_booking),

    path('Corporate/Approver_2/bus-bookings/<int:id>', approver_2_views.bus_bookings),
    path('Corporate/Approver_2/view-bus-booking/<int:id>', approver_2_views.view_bus_booking),
    path('Corporate/Approver_2/accept-bus-booking/<int:id>', approver_2_views.accept_bus_booking),
    path('Corporate/Approver_2/reject-bus-booking/<int:id>', approver_2_views.reject_bus_booking),

    path('Corporate/Approver_2/train-bookings/<int:id>', approver_2_views.train_bookings),
    path('Corporate/Approver_2/view-train-booking/<int:id>', approver_2_views.view_train_booking),
    path('Corporate/Approver_2/accept-train-booking/<int:id>', approver_2_views.accept_train_booking),
    path('Corporate/Approver_2/reject-train-booking/<int:id>', approver_2_views.reject_train_booking),

    path('Corporate/Approver_2/hotel-bookings/<int:id>', approver_2_views.hotel_bookings),
    path('Corporate/Approver_2/view-hotel-booking/<int:id>', approver_2_views.view_hotel_booking),
    path('Corporate/Approver_2/accept-hotel-booking/<int:id>', approver_2_views.accept_hotel_booking),
    path('Corporate/Approver_2/reject-hotel-booking/<int:id>', approver_2_views.reject_hotel_booking),

    path('Corporate/Approver_2/flight-bookings/<int:id>', approver_2_views.flight_bookings),
    path('Corporate/Approver_2/view-flight-booking/<int:id>', approver_2_views.view_flight_booking),
    path('Corporate/Approver_2/accept-flight-booking/<int:id>', approver_2_views.accept_flight_booking),
    path('Corporate/Approver_2/reject-flight-booking/<int:id>', approver_2_views.reject_flight_booking),

    path('Corporate/Approver_2/download-taxi-bookings', approver_2_views.download_taxi_bookings),
    path('Corporate/Approver_2/download-bus-bookings', approver_2_views.download_bus_bookings),
    path('Corporate/Approver_2/download-train-bookings', approver_2_views.download_train_bookings),
    path('Corporate/Approver_2/download-flight-bookings', approver_2_views.download_flight_bookings),
    path('Corporate/Approver_2/download-hotel-bookings', approver_2_views.download_hotel_bookings),

    path('Corporate/Approver_2/download-billing-entities', approver_2_views.download_billing_entities),
    path('Corporate/Approver_2/download-rates', approver_2_views.download_rates),
    path('Corporate/Approver_2/download-employees', approver_2_views.download_employees),

    path('Corporate/Approver_2/visa-bokings', approver_2_views.visa_bokings),
    path('Corporate/Approver_2/view-visa-request/<int:id>', approver_2_views.view_visa_requests),
    path('Corporate/Approver_2/accept-visa-booking', approver_2_views.accept_visa_booking),
    path('Corporate/Approver_2/reject-visa-booking', approver_2_views.reject_visa_booking),

    path('Corporate/Approver_2/frro-requests/<int:id>', approver_2_views.frro_bokings),
    path('Corporate/Approver_2/view-frro-request/<int:id>', approver_2_views.view_frro_requests),
    path('Corporate/Approver_2/accept-frro-request', approver_2_views.accept_frro_booking),
    path('Corporate/Approver_2/reject-frro-request', approver_2_views.reject_frro_booking),
    path('Corporate/Approver_2/view-employee-frro-details/<int:id>', approver_2_views.view_employee_frro_details),

    path('Corporate/Approver_2/guesthouse-bookings/<int:id>', approver_2_views.guesthouse_bookings),
    path('Corporate/Approver_1/view-guesthouse-booking/<int:id>', approver_2_views.view_guesthouse_booking),
    path('Corporate/Approver_2/accept-guesthouse-booking/<int:id>', approver_2_views.accept_guesthouse_booking),
    path('Corporate/Approver_2/reject-guesthouse-booking/<int:id>', approver_2_views.reject_guesthouse_booking),
    path('Corporate/Approver_2/download-guesthouse-bookings', approver_2_views.download_guesthouse_bookings),
]