from django.urls import path,include
from Common.VIEW.Api import operator_api_view

urlpatterns = [
    path('api/operator_taxi_bookings', operator_api_view.operator_taxi_bookings),
    path('api/operator_bus_bookings', operator_api_view.operator_bus_bookings),
    path('api/operator_train_bookings', operator_api_view.operator_train_bookings),
    path('api/operator_hotel_bookings', operator_api_view.operator_hotel_bookings),
    path('api/operator_flight_bookings', operator_api_view.operator_flight_bookings),

    path('api/operator_reject_taxi_booking', operator_api_view.operator_reject_taxi_bookings),

    path('api/driver_taxi_bookings', operator_api_view.driver_taxi_bookings),

    path('api/started_from_garage', operator_api_view.started_from_garage),
    path('api/arrived_at_pickup', operator_api_view.arrived_at_pickup),
    path('api/started_from_pickup', operator_api_view.started_from_pickup),
    path('api/arrived_at_drop', operator_api_view.arrived_at_drop),
    path('api/update_encoded_polyline', operator_api_view.update_encoded_polyline),

    path('api/send_tracking_link', operator_api_view.send_tracking_link),
    path('api/request_for_tracking', operator_api_view.request_for_tracking),

    path('api/operator-accept-bill', operator_api_view.operator_accept_bill),
    path('api/operator-reject-bill', operator_api_view.operator_reject_bill),
    path('api/get_all_operator_bill_payment_status_for_operator', operator_api_view.get_all_operator_bill_payment_status),
    path('api/get_cotrav_accounts_for_operator', operator_api_view.get_cotrav_accounts),
    path('api/get_operator_accounts_for_operator', operator_api_view.get_operator_accounts),
    path('api/operator_verify_vendor_bookings', operator_api_view.operator_verify_vendor_bookings),
    path('api/operator_revise_vendor_bookings', operator_api_view.operator_revise_vendor_bookings),
    path('api/operator_update_vendor_bookings', operator_api_view.operator_update_vendor_bookings),

    path('api/operator_dashboard-taxable-amount-table', operator_api_view.dashboard_taxable_amount_table),
    path('api/operator_dashboard_sales_for_six_months', operator_api_view.operator_dashboard_sales_for_six_months),
    path('api/operator_dashboard_bookings_for_six_months',operator_api_view.operator_dashboard_bookings_for_six_months),

]