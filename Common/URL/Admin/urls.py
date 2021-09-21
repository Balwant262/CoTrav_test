from django.urls import path,include
from Common.VIEW.Admin import admin_views
from Common.VIEW.Admin import selfbooking_admin_views

urlpatterns = [
    path('Corporate/Admin/logout', admin_views.logout_action),
    path('Corporate/Admin/home', admin_views.homepage),
    path('Corporate/Admin/user_profile', admin_views.user_profile),
    path('Corporate/Admin/company-billing_entities/<int:id>', admin_views.company_billing_entities),
    path('Corporate/Admin/company-rates/<int:id>', admin_views.company_rates),

    path('Corporate/Admin/add-company-rate/<int:id>', admin_views.add_company_rate),
    path('Corporate/Admin/add-company-entity/<int:id>', admin_views.add_company_entity),

    path('Corporate/Admin/company-groups/<int:id>', admin_views.company_groups),
    path('Corporate/Admin/view-company-group/<int:id>', admin_views.view_company_group),
    path('Corporate/Admin/add-company-group/<int:id>', admin_views.add_company_group),
    path('Corporate/Admin/update-company-group/<int:id>', admin_views.update_company_group),
    path('Corporate/Admin/delete-company-group/<int:id>', admin_views.delete_company_group),
    path('Corporate/Admin/add-company-group-auth/<int:id>', admin_views.add_company_group_auth),

    path('Corporate/Admin/company-subgroups/<int:id>', admin_views.company_subgroups),
    path('Corporate/Admin/view-company-subgroup/<int:id>', admin_views.view_company_subgroup),
    path('Corporate/Admin/add-company-subgroup/<int:id>', admin_views.add_company_subgroup),
    path('Corporate/Admin/update-company-subgroup/<int:id>', admin_views.update_company_subgroup),
    path('Corporate/Admin/delete-company-subgroup/<int:id>', admin_views.delete_company_subgroup),
    path('Corporate/Admin/add-company-subgroup-auth/<int:id>', admin_views.add_company_subgroup_auth),

    path('Corporate/Admin/company-admins/<int:id>', admin_views.company_admins),
    path('Corporate/Admin/add-company-admins/<int:id>', admin_views.add_company_admins),

    path('Corporate/Admin/company-spoc/<int:id>', admin_views.company_spocs),
    path('Corporate/Admin/add-spoc/<int:id>', admin_views.add_spocs),

    path('Corporate/Admin/company-employees/<int:id>', admin_views.company_employees),
    path('Corporate/Admin/add-employee/<int:id>', admin_views.add_employee),

    path('Corporate/Admin/assessment_cities/<int:id>', admin_views.assessment_cities),
    path('Corporate/Admin/delete-assessment_cities/<int:id>', admin_views.delete_assessment_cities),
    path('Corporate/Admin/assessment_codes/<int:id>', admin_views.assessment_codes),
    path('Corporate/Admin/delete-assessment_codes/<int:id>', admin_views.delete_assessment_codes),

    path('Corporate/Admin/taxi-bookings/<int:id>', admin_views.taxi_bookings),
    path('Corporate/Admin/add-taxi-booking/<int:id>', admin_views.add_taxi_booking),
    path('Corporate/Admin/view-taxi-booking/<int:id>', admin_views.view_taxi_booking),
    path('Corporate/Admin/accept-taxi-booking/<int:id>', admin_views.accept_taxi_booking),
    path('Corporate/Admin/reject-taxi-booking/<int:id>', admin_views.reject_taxi_booking),

    path('Corporate/Admin/bus-bookings/<int:id>', admin_views.bus_bookings),
    path('Corporate/Admin/add-bus-booking/<int:id>', admin_views.add_bus_booking),
    path('Corporate/Admin/view-bus-booking/<int:id>', admin_views.view_bus_booking),
    path('Corporate/Admin/accept-bus-booking/<int:id>', admin_views.accept_bus_booking),
    path('Corporate/Admin/reject-bus-booking/<int:id>', admin_views.reject_bus_booking),

    path('Corporate/Admin/train-bookings/<int:id>', admin_views.train_bookings),
    path('Corporate/Admin/add-train-booking/<int:id>', admin_views.add_train_booking),
    path('Corporate/Admin/view-train-booking/<int:id>', admin_views.view_train_booking),
    path('Corporate/Admin/accept-train-booking/<int:id>', admin_views.accept_train_booking),
    path('Corporate/Admin/reject-train-booking/<int:id>', admin_views.reject_train_booking),

    path('Corporate/Admin/hotel-bookings/<int:id>', admin_views.hotel_bookings),
    path('Corporate/Admin/add-hotel-booking/<int:id>', admin_views.add_hotel_booking),
    path('Corporate/Admin/view-hotel-booking/<int:id>', admin_views.view_hotel_booking),
    path('Corporate/Admin/accept-hotel-booking/<int:id>', admin_views.accept_hotel_booking),
    path('Corporate/Admin/reject-hotel-booking/<int:id>', admin_views.reject_hotel_booking),

    path('Corporate/Admin/flight-bookings/<int:id>', admin_views.flight_bookings),
    path('Corporate/Admin/add-flight-booking/<int:id>', admin_views.add_flight_booking),
    path('Corporate/Admin/view-flight-booking/<int:id>', admin_views.view_flight_booking),
    path('Corporate/Admin/accept-flight-booking/<int:id>', admin_views.accept_flight_booking),
    path('Corporate/Admin/reject-flight-booking/<int:id>', admin_views.reject_flight_booking),

    path('Corporate/Admin/add-self-flight-booking/<int:id>', admin_views.add_self_flight_booking),
    path('Corporate/Admin/add-self-flight-booking-conformation/<int:id>', admin_views.add_self_flight_booking_conformation),

    path('Corporate/Admin/download-taxi-bookings', admin_views.download_taxi_bookings),
    path('Corporate/Admin/download-bus-bookings', admin_views.download_bus_bookings),
    path('Corporate/Admin/download-train-bookings', admin_views.download_train_bookings),
    path('Corporate/Admin/download-flight-bookings', admin_views.download_flight_bookings),
    path('Corporate/Admin/download-hotel-bookings', admin_views.download_hotel_bookings),

    path('Corporate/Admin/download-billing-entities', admin_views.download_billing_entities),
    path('Corporate/Admin/download-rates', admin_views.download_rates),
    path('Corporate/Admin/download-assessment_cities', admin_views.download_assessment_cities),
    path('Corporate/Admin/download-assessment_codes', admin_views.download_assessment_codes),
    path('Corporate/Admin/download-groups', admin_views.download_groups),
    path('Corporate/Admin/download-subgroups', admin_views.download_subgroups),
    path('Corporate/Admin/download-admins', admin_views.download_admins),
    path('Corporate/Admin/download-spocs', admin_views.download_spocs),
    path('Corporate/Admin/download-employees', admin_views.download_employees),

    path('Corporate/Admin/taxi-billing/<int:id>', admin_views.taxi_billing),
    path('Corporate/Admin/bus-billing/<int:id>', admin_views.bus_billing),
    path('Corporate/Admin/train-billing/<int:id>', admin_views.train_billing),
    path('Corporate/Admin/flight-billing/<int:id>', admin_views.flight_billing),
    path('Corporate/Admin/hotel-billing/<int:id>', admin_views.hotel_billing),
    path('Corporate/Admin/visa-billing/<int:id>', admin_views.visa_billing),
    path('Corporate/Admin/frro-billing/<int:id>', admin_views.frro_billing),
    path('Corporate/Admin/guesthouse-billing/<int:id>', admin_views.guesthouse_billing),

    path('Corporate/Admin/taxi-billing/verify', admin_views.taxi_billing_verify),
    path('Corporate/Admin/bus-billing/verify', admin_views.bus_billing_verify),
    path('Corporate/Admin/train-billing/verify', admin_views.train_billing_verify),
    path('Corporate/Admin/flight-billing/verify', admin_views.flight_billing_verify),
    path('Corporate/Admin/hotel-billing/verify', admin_views.hotel_billing_verify),
    path('Corporate/Admin/visa-billing/verify', admin_views.visa_billing_verify),
    path('Corporate/Admin/frro-billing/verify', admin_views.frro_billing_verify),
    path('Corporate/Admin/guesthouse-billing/verify', admin_views.guesthouse_billing_verify),

    path('Corporate/Admin/bill/<int:id>', admin_views.get_all_generated_bills),
    path('Corporate/Admin/BankAccounts', admin_views.corporate_bank_accounts),
    path('Corporate/Admin/add-corporate-accounts/<int:id>', admin_views.add_company_accounts),
    path('Corporate/Admin/accept-bill', admin_views.accept_bill),

    path('Corporate/Admin/booking-search', admin_views.dashboard_search_admin_api_call),
    path('Corporate/Admin/reports/invoice', admin_views.reports_invoice,name='report-invoice'),
    path('Corporate/Admin/reports/client-billing', admin_views.reports_client_billing),
    path('Corporate/Admin/reports/download-client-billing', admin_views.download_client_bill_reports),
    path('Corporate/Admin/reports/download-invoice-report', admin_views.download_invoice_reports),

    path('Corporate/Admin/add-booking-feedback', admin_views.add_booking_feedback),

    path('Corporate/Admin/visa-bokings', admin_views.visa_bokings),
    path('Corporate/Admin/view-visa-request/<int:id>', admin_views.view_visa_requests),

    path('Corporate/Admin/frro-requests/<int:id>', admin_views.get_all_frro_requests),
    path('Corporate/Admin/add-new-frro-request', admin_views.add_new_frro_request),
    path('Corporate/Admin/view-frro-request/<int:id>', admin_views.view_frro_request),
    path('Corporate/Admin/frro-change-document', admin_views.frro_change_document),
    path('Corporate/Admin/view-employee-frro-details/<int:id>', admin_views.view_employee_frro_details),

    path('Corporate/Admin/travelport_flight_search',admin_views.travelport_flight_search),
    path('Corporate/Admin/travelport_flight_book',admin_views.travelport_flight_details),
    path('Corporate/Admin/travelport_flight_booking_req',admin_views.travelport_flight_booking_req),
    path('Corporate/Admin/travelport_cancle_booking',admin_views.travelport_cancle_booking_req),

    path('Corporate/Admin/guesthouse-bookings/<int:id>', admin_views.guesthouse_bookings),
    path('Corporate/Admin/search-guesthouse/<int:id>', admin_views.search_guesthouse),
    path('Corporate/Admin/get-guesthouse-to-booking/<int:id>', admin_views.get_guesthouse_to_booking),
    path('Corporate/Admin/add-guesthouse-booking/<int:id>', admin_views.add_guesthouse_booking),
    path('Corporate/Admin/view-guesthouse-booking/<int:id>', admin_views.view_guesthouse_booking),
    path('Corporate/Admin/reject-guesthouse-booking/<int:id>', admin_views.reject_guesthouse_booking),
    path('Corporate/Admin/view-guesthouse-details/<int:id>', admin_views.view_guesthouse_details),
    path('Corporate/Admin/download-guesthouse-bookings', admin_views.download_guesthouse_bookings),

    path('Corporate/Admin/add-self-flight-booking/<int:id>', selfbooking_admin_views.add_flight_booking_self),
    path('Corporate/Admin/add-self-flight-booking-conformation/<int:id>', selfbooking_admin_views.add_flight_booking_self_conformation),
    path('Corporate/Admin/add-self-flight-booking-final/<int:id>', selfbooking_admin_views.add_flight_booking_self_final),

    path('Corporate/Admin/add-self-hotel-booking/<int:id>', selfbooking_admin_views.add_hotel_booking_self),

    path('Corporate/Admin/add-self-bus-booking/<int:id>', selfbooking_admin_views.add_bus_booking_self),

]