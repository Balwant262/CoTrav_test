from django.urls import path,include
from Common.VIEW.Spoc import spoc_views

urlpatterns = [
    path('Corporate/Spoc/logout', spoc_views.logout_action),
    path('Corporate/Spoc/home', spoc_views.homepage),
    path('Corporate/Spoc/user_profile', spoc_views.user_profile),
    path('Corporate/Spoc/company-billing_entities/<int:id>', spoc_views.company_billing_entities),
    path('Corporate/Spoc/company-rates/<int:id>', spoc_views.company_rates),
    path('Corporate/Spoc/company-groups/<int:id>', spoc_views.company_groups),
    path('Corporate/Spoc/view-company-group/<int:id>', spoc_views.view_company_group),
    path('Corporate/Spoc/company-subgroups/<int:id>', spoc_views.company_subgroups),
    path('Corporate/Spoc/view-company-subgroup/<int:id>', spoc_views.view_company_subgroup),
    path('Corporate/Spoc/company-admins/<int:id>', spoc_views.company_admins),
    path('Corporate/Spoc/company-spocs/<int:id>', spoc_views.company_spocs),
    path('Corporate/Spoc/company-employees/<int:id>', spoc_views.company_employees),

    path('Corporate/Spoc/taxi-bookings/<int:id>', spoc_views.taxi_bookings),
    path('Corporate/Spoc/add-taxi-booking/<int:id>', spoc_views.add_taxi_booking),
    path('Corporate/Spoc/view-taxi-booking/<int:id>', spoc_views.view_taxi_booking),
    path('Corporate/Spoc/reject-taxi-booking/<int:id>', spoc_views.reject_taxi_booking),

    path('Corporate/Spoc/bus-bookings/<int:id>', spoc_views.bus_bookings),
    path('Corporate/Spoc/add-bus-booking/<int:id>', spoc_views.add_bus_booking),
    path('Corporate/Spoc/view-bus-booking/<int:id>', spoc_views.view_bus_booking),
    path('Corporate/Spoc/reject-bus-booking/<int:id>', spoc_views.reject_bus_booking),

    path('Corporate/Spoc/train-bookings/<int:id>', spoc_views.train_bookings),
    path('Corporate/Spoc/add-train-booking/<int:id>', spoc_views.add_train_booking),
    path('Corporate/Spoc/view-train-booking/<int:id>', spoc_views.view_train_booking),
    path('Corporate/Spoc/reject-train-booking/<int:id>', spoc_views.reject_train_booking),

    path('Corporate/Spoc/hotel-bookings/<int:id>', spoc_views.hotel_bookings),
    path('Corporate/Spoc/add-hotel-booking/<int:id>', spoc_views.add_hotel_booking),
    path('Corporate/Spoc/view-hotel-booking/<int:id>', spoc_views.view_hotel_booking),
    path('Corporate/Spoc/reject-hotel-booking/<int:id>', spoc_views.reject_hotel_booking),

    path('Corporate/Spoc/flight-bookings/<int:id>', spoc_views.flight_bookings),
    path('Corporate/Spoc/add-flight-booking/<int:id>', spoc_views.add_flight_booking),
    path('Corporate/Spoc/view-flight-booking/<int:id>', spoc_views.view_flight_booking),
    path('Corporate/Spoc/reject-flight-booking/<int:id>', spoc_views.reject_flight_booking),

    path('Corporate/Spoc/add-flight-booking-self/<int:id>', spoc_views.add_flight_booking_self),
    path('Corporate/Spoc/add-flight-booking-self-conformation/<int:id>', spoc_views.add_flight_booking_self_conformation),
    path('Corporate/Spoc/add-flight-booking-self-final/<int:id>', spoc_views.add_flight_booking_self_final),
    path('Corporate/Spoc/get-api-flight', spoc_views.razor_charge),

    path('Corporate/Spoc/download-taxi-bookings', spoc_views.download_taxi_bookings),
    path('Corporate/Spoc/download-bus-bookings', spoc_views.download_bus_bookings),
    path('Corporate/Spoc/download-train-bookings', spoc_views.download_train_bookings),
    path('Corporate/Spoc/download-flight-bookings', spoc_views.download_flight_bookings),
    path('Corporate/Spoc/download-hotel-bookings', spoc_views.download_hotel_bookings),

    path('Corporate/Spoc/download-billing-entities', spoc_views.download_billing_entities),
    path('Corporate/Spoc/download-employees', spoc_views.download_employees),
    path('Corporate/Spoc/download-spocs', spoc_views.download_spocs),

    path('Corporate/Spoc/taxi-billing/<int:id>', spoc_views.taxi_billing),
    path('Corporate/Spoc/bus-billing/<int:id>', spoc_views.bus_billing),
    path('Corporate/Spoc/train-billing/<int:id>', spoc_views.train_billing),
    path('Corporate/Spoc/flight-billing/<int:id>', spoc_views.flight_billing),
    path('Corporate/Spoc/hotel-billing/<int:id>', spoc_views.hotel_billing),
    path('Corporate/Spoc/visa-billing/<int:id>', spoc_views.visa_billing),
    path('Corporate/Spoc/frro-billing/<int:id>', spoc_views.frro_billing),
    path('Corporate/Spoc/guesthouse-billing/<int:id>', spoc_views.guesthouse_billing),

    path('Corporate/Spoc/taxi-billing/verify', spoc_views.taxi_billing_verify),
    path('Corporate/Spoc/bus-billing/verify', spoc_views.bus_billing_verify),
    path('Corporate/Spoc/train-billing/verify', spoc_views.train_billing_verify),
    path('Corporate/Spoc/flight-billing/verify', spoc_views.flight_billing_verify),
    path('Corporate/Spoc/hotel-billing/verify', spoc_views.hotel_billing_verify),
    path('Corporate/Spoc/visa-billing/verify', spoc_views.visa_billing_verify),
    path('Corporate/Spoc/frro-billing/verify', spoc_views.frro_billing_verify),
    path('Corporate/Spoc/guesthouse-billing/verify', spoc_views.guesthouse_billing_verify),

    path('Corporate/Spoc/visa-bokings', spoc_views.visa_bokings),
    path('Corporate/Spoc/add-new-visa-request', spoc_views.add_visa_requests),
    path('Corporate/Spoc/view-visa-request/<int:id>', spoc_views.view_visa_requests),
    path('Corporate/Spoc/reject-visa-booking', spoc_views.reject_visa_booking),

    path('Corporate/Spoc/add-booking-feedback', spoc_views.add_booking_feedback),
    path('Corporate/Spoc/cancel-frro-request', spoc_views.cancel_frro_request),
    path('Corporate/Spoc/frro-requests/<int:id>', spoc_views.get_all_frro_requests),
    path('Corporate/Spoc/add-new-frro-request', spoc_views.add_new_frro_request),
    path('Corporate/Spoc/view-frro-request/<int:id>', spoc_views.view_frro_request),
    path('Corporate/Spoc/frro-change-document', spoc_views.frro_change_document),
    path('Corporate/Spoc/view-employee-frro-details/<int:id>', spoc_views.view_employee_frro_details),

    path('Corporate/Spoc/change-frro-booking-office-status', spoc_views.frro_change_office_status),
    path('Corporate/Spoc/change-frro-booking-document-letter', spoc_views.frro_change_document_letter),

    path('Corporate/Spoc/guesthouse-bookings/<int:id>', spoc_views.guesthouse_bookings),
    path('Corporate/Spoc/search-guesthouse/<int:id>', spoc_views.search_guesthouse),
    path('Corporate/Spoc/get-guesthouse-to-booking/<int:id>', spoc_views.get_guesthouse_to_booking),
    path('Corporate/Spoc/add-guesthouse-booking/<int:id>', spoc_views.add_guesthouse_booking),
    path('Corporate/Spoc/view-guesthouse-booking/<int:id>', spoc_views.view_guesthouse_booking),
    path('Corporate/Spoc/reject-guesthouse-booking/<int:id>', spoc_views.reject_guesthouse_booking),
    path('Corporate/Spoc/view-guesthouse-details/<int:id>', spoc_views.view_guesthouse_details),
    path('Corporate/Spoc/download-guesthouse-bookings', spoc_views.download_guesthouse_bookings),

]