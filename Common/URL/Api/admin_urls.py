from django.urls import path,include
from Common.VIEW.Api import admin_api_view

urlpatterns = [
    path('api/admin_taxi_bookings', admin_api_view.admin_taxi_bookings),
    path('api/admin_accept_taxi_booking', admin_api_view.admin_accept_taxi_booking),
    path('api/admin_reject_taxi_booking', admin_api_view.admin_reject_taxi_booking),

    path('api/admin_bus_bookings', admin_api_view.admin_bus_bookings),
    path('api/admin_accept_bus_booking', admin_api_view.admin_accept_bus_booking),
    path('api/admin_reject_bus_booking', admin_api_view.admin_reject_bus_booking),

    path('api/admin_train_bookings', admin_api_view.admin_train_bookings),
    path('api/admin_accept_train_booking', admin_api_view.admin_accept_train_booking),
    path('api/admin_reject_train_booking', admin_api_view.admin_reject_train_booking),

    path('api/admin_hotel_bookings', admin_api_view.admin_hotel_bookings),
    path('api/admin_accept_hotel_booking', admin_api_view.admin_accept_hotel_booking),
    path('api/admin_reject_hotel_booking', admin_api_view.admin_reject_hotel_booking),

    path('api/admin_flight_bookings', admin_api_view.admin_flight_bookings),
    path('api/admin_accept_flight_booking', admin_api_view.admin_accept_flight_booking),
    path('api/admin_reject_flight_booking', admin_api_view.admin_reject_flight_booking),

    path('api/admin_verify_taxi_bookings', admin_api_view.admin_verify_taxi_bookings),
    path('api/admin_revise_taxi_bookings', admin_api_view.admin_revise_taxi_bookings),
    path('api/admin_verify_bus_bookings', admin_api_view.admin_verify_bus_bookings),
    path('api/admin_revise_bus_bookings', admin_api_view.admin_revise_bus_bookings),
    path('api/admin_verify_train_bookings', admin_api_view.admin_verify_train_bookings),
    path('api/admin_revise_train_bookings', admin_api_view.admin_revise_train_bookings),
    path('api/admin_verify_hotel_bookings', admin_api_view.admin_verify_hotel_bookings),
    path('api/admin_revise_hotel_bookings', admin_api_view.admin_revise_hotel_bookings),
    path('api/admin_verify_flight_bookings', admin_api_view.admin_verify_flight_bookings),
    path('api/admin_revise_flight_bookings', admin_api_view.admin_revise_flight_bookings),
    path('api/admin_verify_visa_bookings', admin_api_view.admin_verify_visa_bookings),
    path('api/admin_revise_visa_bookings', admin_api_view.admin_revise_visa_bookings),
    path('api/spoc_verify_frro_bookings', admin_api_view.admin_verify_frro_bookings),
    path('api/spoc_revise_frro_bookings', admin_api_view.admin_revise_frro_bookings),
    path('api/admin_verify_guesthouse_bookings', admin_api_view.admin_verify_guesthouse_bookings),
    path('api/admin_revise_guesthouse_bookings', admin_api_view.admin_revise_guesthouse_bookings),

    path('api/admin_dashboard_sales_by_month', admin_api_view.admin_dashboard_sales_by_month),
    path('api/admin_dashboard_bookings_by_month', admin_api_view.admin_dashboard_bookings_by_month),
    path('api/admin_dashboard_sales_for_six_months', admin_api_view.admin_dashboard_sales_for_six_months),
    path('api/admin_dashboard_bookings_for_six_months', admin_api_view.admin_dashboard_bookings_for_six_months),
    path('api/admin_dashboard_sales_by_city', admin_api_view.admin_dashboard_sales_by_city),
    path('api/admin_dashboard_sales_by_city_for_month', admin_api_view.admin_dashboard_sales_by_city_for_month),
    path('api/admin_dashboard_taxable_amount_table', admin_api_view.admin_dashboard_taxable_amount_table),

    path('api/admin_accept_bill', admin_api_view.accept_bill),
    path('api/admin_reject_bill', admin_api_view.reject_bill),
    path('api/dashboard_search_admin_bookings', admin_api_view.dashboard_search_admin_bookings),
    path('api/admin_report_invoice', admin_api_view.admin_report_invoice),
    path('api/admin_report_client_bills', admin_api_view.admin_report_client_bills),

    path('api/company_frro_request', admin_api_view.admin_frro_request),

]