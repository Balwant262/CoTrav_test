from django.urls import path,include
from Common.VIEW.Employee import employee_views

urlpatterns = [
    path('Corporate/Employee/logout', employee_views.logout_action),
    path('Corporate/Employee/home', employee_views.homepage),
    path('Corporate/Employee/user_profile', employee_views.user_profile),
    path('Corporate/Employee/company-billing_entities/<int:id>', employee_views.company_billing_entities),
    path('Corporate/Employee/company-rates/<int:id>', employee_views.company_rates),
    path('Corporate/Employee/company-groups/<int:id>', employee_views.company_groups),
    path('Corporate/Employee/view-company-group/<int:id>', employee_views.view_company_group),
    path('Corporate/Employee/company-subgroups/<int:id>', employee_views.company_subgroups),
    path('Corporate/Employee/view-company-subgroup/<int:id>', employee_views.view_company_subgroup),
    path('Corporate/Employee/company-admins/<int:id>', employee_views.company_admins),
    path('Corporate/Employee/company-spocs/<int:id>', employee_views.company_spocs),
    path('Corporate/Employee/company-employees/<int:id>', employee_views.company_employees),

    path('Corporate/Employee/taxi-bookings/<int:id>', employee_views.taxi_bookings),
    path('Corporate/Employee/add-taxi-booking/<int:id>', employee_views.add_taxi_booking),
    path('Corporate/Employee/view-taxi-booking/<int:id>', employee_views.view_taxi_booking),
    path('Corporate/Employee/reject-taxi-booking/<int:id>', employee_views.reject_taxi_booking),

    path('Corporate/Employee/bus-bookings/<int:id>', employee_views.bus_bookings),
    path('Corporate/Employee/add-bus-booking/<int:id>', employee_views.add_bus_booking),
    path('Corporate/Employee/view-bus-booking/<int:id>', employee_views.view_bus_booking),
    path('Corporate/Employee/reject-bus-booking/<int:id>', employee_views.reject_bus_booking),

    path('Corporate/Employee/train-bookings/<int:id>', employee_views.train_bookings),
    path('Corporate/Employee/add-train-booking/<int:id>', employee_views.add_train_booking),
    path('Corporate/Employee/view-train-booking/<int:id>', employee_views.view_train_booking),
    path('Corporate/Employee/reject-train-booking/<int:id>', employee_views.reject_train_booking),

    path('Corporate/Employee/hotel-bookings/<int:id>', employee_views.hotel_bookings),
    path('Corporate/Employee/add-hotel-booking/<int:id>', employee_views.add_hotel_booking),
    path('Corporate/Employee/view-hotel-booking/<int:id>', employee_views.view_hotel_booking),
    path('Corporate/Employee/reject-hotel-booking/<int:id>', employee_views.reject_hotel_booking),

    path('Corporate/Employee/flight-bookings/<int:id>', employee_views.flight_bookings),
    path('Corporate/Employee/add-flight-booking/<int:id>', employee_views.add_flight_booking),
    path('Corporate/Employee/view-flight-booking/<int:id>', employee_views.view_flight_booking),
    path('Corporate/Employee/reject-flight-booking/<int:id>', employee_views.reject_flight_booking),

    path('Corporate/Employee/download-taxi-bookings', employee_views.download_taxi_bookings),
    path('Corporate/Employee/download-bus-bookings', employee_views.download_bus_bookings),
    path('Corporate/Employee/download-train-bookings', employee_views.download_train_bookings),
    path('Corporate/Employee/download-flight-bookings', employee_views.download_flight_bookings),
    path('Corporate/Employee/download-hotel-bookings', employee_views.download_hotel_bookings),

    path('Corporate/Employee/visa-bokings', employee_views.visa_bokings),
    path('Corporate/Employee/view-visa-request/<int:id>', employee_views.view_visa_requests),
    path('Corporate/Employee/add-new-visa-request', employee_views.add_visa_requests),

    path('Corporate/Employee/add-booking-feedback', employee_views.add_booking_feedback),

    path('Corporate/Employee/frro-requests/<int:id>', employee_views.get_all_frro_requests),
    path('Corporate/Employee/add-new-frro-request', employee_views.add_new_frro_request),
    path('Corporate/Employee/view-frro-request/<int:id>', employee_views.view_frro_request),
    path('Corporate/Employee/frro-change-document', employee_views.frro_change_document),
    path('Corporate/Employee/view-employee-frro-details/<int:id>', employee_views.view_employee_frro_details),
    path('Corporate/Employee/change-frro-booking-office-status', employee_views.frro_change_office_status),
    path('Corporate/Employee/change-frro-booking-document-letter', employee_views.frro_change_document_letter),

    path('Corporate/Employee/guesthouse-bookings/<int:id>', employee_views.guesthouse_bookings),
    path('Corporate/Employee/search-guesthouse/<int:id>', employee_views.search_guesthouse),
    path('Corporate/Employee/get-guesthouse-to-booking/<int:id>', employee_views.get_guesthouse_to_booking),
    path('Corporate/Employee/add-guesthouse-booking/<int:id>', employee_views.add_guesthouse_booking),
    path('Corporate/Employee/view-guesthouse-booking/<int:id>', employee_views.view_guesthouse_booking),
    path('Corporate/Employee/reject-guesthouse-booking/<int:id>', employee_views.reject_guesthouse_booking),
    path('Corporate/Employee/view-guesthouse-details/<int:id>', employee_views.view_guesthouse_details),
    path('Corporate/Employee/download-guesthouse-bookings', employee_views.download_guesthouse_bookings),
]