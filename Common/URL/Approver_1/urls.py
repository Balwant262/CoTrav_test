from django.urls import path,include
from Common.VIEW.Approver_1 import approver_1_views

urlpatterns = [
    path('Corporate/Approver_1/logout', approver_1_views.logout_action),
    path('Corporate/Approver_1/home', approver_1_views.homepage),
    path('Corporate/Approver_1/user_profile', approver_1_views.user_profile),
    path('Corporate/Approver_1/company-billing_entities/<int:id>', approver_1_views.company_billing_entities),
    path('Corporate/Approver_1/company-rates/<int:id>', approver_1_views.company_rates),
    path('Corporate/Approver_1/company-groups/<int:id>', approver_1_views.company_groups),
    path('Corporate/Approver_1/view-company-group/<int:id>', approver_1_views.view_company_group),
    path('Corporate/Approver_1/company-subgroup/<int:id>', approver_1_views.company_subgroups),
    path('Corporate/Approver_1/view-company-subgroup/<int:id>', approver_1_views.view_company_subgroup),
    path('Corporate/Approver_1/company-admins/<int:id>', approver_1_views.company_admins),
    path('Corporate/Approver_1/company-spocs/<int:id>', approver_1_views.company_spocs),
    path('Corporate/Approver_1/company-employees/<int:id>', approver_1_views.company_employees),

    path('Corporate/Approver_1/taxi-bookings/<int:id>', approver_1_views.taxi_bookings),
    path('Corporate/Approver_1/view-taxi-booking/<int:id>', approver_1_views.view_taxi_booking),
    path('Corporate/Approver_1/accept-taxi-booking/<int:id>', approver_1_views.accept_taxi_booking),
    path('Corporate/Approver_1/reject-taxi-booking/<int:id>', approver_1_views.reject_taxi_booking),

    path('Corporate/Approver_1/bus-bookings/<int:id>', approver_1_views.bus_bookings),
    path('Corporate/Approver_1/view-bus-booking/<int:id>', approver_1_views.view_bus_booking),
    path('Corporate/Approver_1/accept-bus-booking/<int:id>', approver_1_views.accept_bus_booking),
    path('Corporate/Approver_1/reject-bus-booking/<int:id>', approver_1_views.reject_bus_booking),

    path('Corporate/Approver_1/train-bookings/<int:id>', approver_1_views.train_bookings),
    path('Corporate/Approver_1/view-train-booking/<int:id>', approver_1_views.view_train_booking),
    path('Corporate/Approver_1/accept-train-booking/<int:id>', approver_1_views.accept_train_booking),
    path('Corporate/Approver_1/reject-train-booking/<int:id>', approver_1_views.reject_train_booking),

    path('Corporate/Approver_1/hotel-bookings/<int:id>', approver_1_views.hotel_bookings),
    path('Corporate/Approver_1/view-hotel-booking/<int:id>', approver_1_views.view_hotel_booking),
    path('Corporate/Approver_1/accept-hotel-booking/<int:id>', approver_1_views.accept_hotel_booking),
    path('Corporate/Approver_1/reject-hotel-booking/<int:id>', approver_1_views.reject_hotel_booking),

    path('Corporate/Approver_1/flight-bookings/<int:id>', approver_1_views.flight_bookings),
    path('Corporate/Approver_1/view-flight-booking/<int:id>', approver_1_views.view_flight_booking),
    path('Corporate/Approver_1/accept-flight-booking/<int:id>', approver_1_views.accept_flight_booking),
    path('Corporate/Approver_1/reject-flight-booking/<int:id>', approver_1_views.reject_flight_booking),

    path('Corporate/Approver_1/download-taxi-bookings', approver_1_views.download_taxi_bookings),
    path('Corporate/Approver_1/download-bus-bookings', approver_1_views.download_bus_bookings),
    path('Corporate/Approver_1/download-train-bookings', approver_1_views.download_train_bookings),
    path('Corporate/Approver_1/download-flight-bookings', approver_1_views.download_flight_bookings),
    path('Corporate/Approver_1/download-hotel-bookings', approver_1_views.download_hotel_bookings),

    path('Corporate/Approver_1/download-billing-entities', approver_1_views.download_billing_entities),
    path('Corporate/Approver_1/download-rates', approver_1_views.download_rates),
    path('Corporate/Approver_1/download-employees', approver_1_views.download_employees),

    path('Corporate/Approver_1/visa-bokings', approver_1_views.visa_bokings),
    path('Corporate/Approver_1/view-visa-request/<int:id>', approver_1_views.view_visa_requests),
    path('Corporate/Approver_1/accept-visa-booking', approver_1_views.accept_visa_booking),
    path('Corporate/Approver_1/reject-visa-booking', approver_1_views.reject_visa_booking),

    path('Corporate/Approver_1/frro-requests/<int:id>', approver_1_views.frro_bokings),
    path('Corporate/Approver_1/view-frro-request/<int:id>', approver_1_views.view_frro_requests),
    path('Corporate/Approver_1/accept-frro-request', approver_1_views.accept_frro_booking),
    path('Corporate/Approver_1/reject-frro-request', approver_1_views.reject_frro_booking),
    path('Corporate/Approver_1/view-employee-frro-details/<int:id>', approver_1_views.view_employee_frro_details),

    path('Corporate/Approver_1/guesthouse-bookings/<int:id>', approver_1_views.guesthouse_bookings),
    path('Corporate/Approver_1/view-guesthouse-booking/<int:id>', approver_1_views.view_guesthouse_booking),
    path('Corporate/Approver_1/accept-guesthouse-booking/<int:id>', approver_1_views.accept_guesthouse_booking),
    path('Corporate/Approver_1/reject-guesthouse-booking/<int:id>', approver_1_views.reject_guesthouse_booking),
    path('Corporate/Approver_2/download-guesthouse-bookings', approver_1_views.download_guesthouse_bookings),

]