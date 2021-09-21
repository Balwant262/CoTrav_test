from django.urls import path,include
from Common.VIEW.Api import api_views
from Common.VIEW.Api import get_app_version_code_view

urlpatterns = [

######################### CORPORATE ADMIN URLS ############################
    path('', include('Common.URL.Api.admin_urls')),
    path('', include('Common.URL.Api.spoc_urls')),
    path('', include('Common.URL.Api.employee_urls')),
    path('', include('Common.URL.Api.approver_1_urls')),
    path('', include('Common.URL.Api.approver_2_urls')),
    path('', include('Common.URL.Api.agent_urls')),
    path('', include('Common.URL.Api.operator_urls')),
    path('', include('Common.URL.Api.self_booking_urls')),
######################### END CORPORATE URLS ####################

    path('api/get_app_version_code', get_app_version_code_view.get_app_version_code),
    path('api/get_public_api_access_token', api_views.get_public_api_access_token),
    path('api/add_api_access_token', api_views.add_api_access_token),
    path('api/update_api_access_token', api_views.update_api_access_token),
    path('api/delete_api_access_token', api_views.delete_api_access_token),



    path('api/login', api_views.login),
    path('api/logout', api_views.logout),
    path('api/get_cotrav_billing_entities', api_views.get_cotrav_billing_entities),
    path('api/add_cotrav_billing_entities', api_views.add_cotrav_billing_entity),
    path('api/update_cotrav_billing_entities', api_views.update_cotrav_billing_entity),
    path('api/delete_cotrav_billing_entities', api_views.delete_cotrav_billing_entity),
    path('api/employee_dashboard', api_views.employee_dashboard),
    path('api/approver_1_dashboard', api_views.approver_1_dashboard),
    path('api/approver_2_dashboard', api_views.approver_2_dashboard),
    path('api/spoc_dashboard', api_views.spoc_dashboard),
    path('api/admin_dashboard', api_views.admin_dashboard),
    path('api/agent_dashboard', api_views.agent_dashboard),
    path('api/agent_dashboard_om', api_views.agent_dashboard_om),
    path('api/agent_dashboard_rm', api_views.agent_dashboard_rm),
    path('api/operator_dashboard', api_views.operator_dashboard),

    path('api/update_fcm_regid', api_views.update_fcm_regid),
    path('api/get_notice', api_views.get_notice),
    path('api/send_broadcast_notification', api_views.send_broadcast_notification),
    path('api/send_message_to_moblies', api_views.send_message_to_moblies),
    path('api/send_mail_to_user', api_views.send_mail_to_user),

    path('api/get_all_leads', api_views.get_all_leads),
    path('api/view_lead', api_views.view_lead),
    path('api/add_lead', api_views.add_lead),
    path('api/update_lead', api_views.update_lead),
    path('api/delete_lead', api_views.delete_lead),
    path('api/delete_lead_document', api_views.delete_lead_document),

    path('api/get_countries', api_views.get_countries),
    path('api/get_states', api_views.get_states),
    path('api/get_cities', api_views.get_cities),
    path('api/city_by_package', api_views.city_by_package),
    path('api/cities', api_views.cities),
    path('api/add_city_name', api_views.add_city_name),
    path('api/add_state_name', api_views.add_state_name),
    path('api/add_country_name', api_views.add_country_name),
    path('api/get_assessment_code', api_views.get_assessment_code),
    path('api/get_assessment_city', api_views.get_assessment_city),

    path('api/corporate_package', api_views.corporate_package),

    path('api/service_types', api_views.service_types),
    path('api/train_types', api_views.train_types),
    path('api/bus_types', api_views.bus_types),
    path('api/irctc_accounts', api_views.irctc_accounts),
    path('api/hotel_types', api_views.hotel_types),
    path('api/get_airports', api_views.get_airports),
    path('api/get_nationality', api_views.get_nationality),
    path('api/visa_types', api_views.visa_types),
    path('api/visa_service_types', api_views.visa_service_types),
    path('api/consulate_office', api_views.consulate_office),

    path('api/hotel_booking_portals', api_views.hotel_booking_portals),
    path('api/view_hotel_portal', api_views.view_hotel_portal),
    path('api/add_hotel_portal', api_views.add_hotel_portal),
    path('api/update_hotel_portal', api_views.update_hotel_portal),
    #path('api/delete_hotel_portal', api_views.delete_hotel_portal),

    path('api/room_types', api_views.room_types),
    path('api/railway_stations', api_views.railway_stations),
    path('api/bus_booking_portals', api_views.bus_booking_portals),

    path('api/corporate_management_fee', api_views.corporate_management_fee),
    path('api/add_corporate_management_fee', api_views.add_corporate_management_fee),
    path('api/update_corporate_management_fee', api_views.update_corporate_management_fee),
    path('api/delete_corporate_management_fee', api_views.delete_corporate_management_fee),
    path('api/service_fee_types', api_views.service_fee_types),

    path('api/get_corporate_management_fee', api_views.corporate_management_fees),

    path('api/taxi_types', api_views.taxi_types),
    path('api/add_taxi_type', api_views.add_taxi_type),
    path('api/update_taxi_type', api_views.update_taxi_type),
    path('api/delete_taxi_type', api_views.delete_taxi_type),

    path('api/taxi_models', api_views.taxi_models),
    path('api/add_taxi_model', api_views.add_taxi_model),
    path('api/update_taxi_model', api_views.update_taxi_model),
    path('api/delete_taxi_model', api_views.delete_taxi_model),

    path('api/taxis', api_views.taxis),
    path('api/add_taxi', api_views.add_taxi),
    path('api/update_taxi', api_views.update_taxi),
    path('api/delete_taxi', api_views.delete_taxi),


    path('api/companies', api_views.companies),
    path('api/view_company', api_views.view_company),
    path('api/add_company', api_views.add_companies),
    path('api/update_company', api_views.update_company),
    path('api/delete_company', api_views.delete_company),
    path('api/add_company_document', api_views.add_company_document),
    path('api/delete_company_document', api_views.delete_company_document),

    path('api/company_rates', api_views.company_rates),
    path('api/add_company_rates', api_views.add_company_rates),
    path('api/update_company_rates', api_views.update_company_rates),
    path('api/delete_company_rates', api_views.delete_company_rates),
    ##sanket added this
    path('api/taxi_packages', api_views.taxi_packages),

    path('api/billing_entities', api_views.billing_entities),
    path('api/view_billing_entitie', api_views.view_billing_entitie),
    path('api/admins', api_views.admins),
    path('api/view_admin', api_views.view_admin),
    path('api/groups', api_views.groups),
    path('api/subgroups', api_views.subgroups),
    path('api/spocs', api_views.spocs),
    path('api/employees', api_views.employee),
    path('api/spoc_employee', api_views.spoc_employee),
    path('api/auth1_spocs', api_views.auth1_spocs),
    path('api/auth2_spocs', api_views.auth2_spocs),

    path('api/add_billing_entity', api_views.add_billing_entity),
    path('api/update_billing_entity', api_views.update_billing_entity),
    path('api/delete_billing_entity', api_views.delete_billing_entity),

    path('api/view_group_auth', api_views.view_group_auth),
    path('api/add_group_auth', api_views.add_group_auth),
    path('api/update_group_auth', api_views.update_group_auth),
    path('api/delete_group_auth', api_views.delete_group_auth),

    path('api/view_group', api_views.view_group),
    path('api/add_group', api_views.add_group),
    path('api/update_group', api_views.update_group),
    path('api/delete_group', api_views.delete_group),

    path('api/view_subgroup', api_views.view_subgroup),
    path('api/add_subgroup', api_views.add_subgroup),
    path('api/update_subgroup', api_views.update_subgroup),
    path('api/delete_subgroup', api_views.delete_subgroup),

    path('api/view_subgroup_auth', api_views.view_subgroup_auth),
    path('api/add_subgroup_auth', api_views.add_subgroup_auth),
    path('api/update_subgroup_auth', api_views.update_subgroup_auth),
    path('api/delete_subgroup_auth', api_views.delete_subgroup_auth),

    path('api/view_auth_1', api_views.view_auth_1),
    path('api/view_auth_2', api_views.view_auth_2),

    path('api/add_admin', api_views.add_admin),
    path('api/update_admin', api_views.update_admin),
    path('api/delete_admin', api_views.delete_admin),

    path('api/view_spoc', api_views.view_spoc),
    path('api/add_spoc', api_views.add_spoc),
    path('api/update_spoc', api_views.update_spoc),
    path('api/delete_spoc', api_views.delete_spoc),
    path('api/active_spoc', api_views.active_spoc),

    path('api/view_employee', api_views.view_employee),
    path('api/view_employee_documents', api_views.view_employee_documents),
    path('api/add_employee', api_views.add_employee),
    path('api/update_employee', api_views.update_employee),
    path('api/delete_employee', api_views.delete_employee),

    path('api/assessment_cities', api_views.assessment_cities),
    path('api/add_assessment_cities', api_views.add_assessment_cities),
    path('api/update_assessment_cities', api_views.update_assessment_cities),
    path('api/delete_assessment_cities', api_views.delete_assessment_cities),

    path('api/assessment_codes', api_views.assessment_codes),
    path('api/add_assessment_codes', api_views.add_assessment_codes),
    path('api/update_assessment_codes', api_views.update_assessment_codes),
    path('api/delete_assessment_codes', api_views.delete_assessment_codes),

    path('api/agents', api_views.get_agents),
    path('api/view_agent', api_views.view_agent),
    path('api/add_agent', api_views.add_agent),
    path('api/update_agent', api_views.update_agent),
    path('api/delete_agent', api_views.delete_agent),
    path('api/activate_agent', api_views.activate_agent),
    path('api/get_operator_package', api_views.get_operator_package),

    ######### TAXI BOOKING API #####################

    path('api/view_taxi_booking', api_views.view_taxi_booking),
    path('api/view_bus_booking', api_views.view_bus_booking),
    path('api/view_train_booking', api_views.view_train_booking),
    path('api/view_hotel_booking', api_views.view_hotel_booking),
    path('api/view_flight_booking', api_views.view_flight_booking),

    path('api/add_taxi_booking', api_views.add_taxi_booking),
    path('api/edit_taxi_booking', api_views.edit_taxi_booking),
    path('api/edit_bus_booking', api_views.edit_bus_booking),
    path('api/add_bus_booking', api_views.add_bus_booking),
    path('api/add_train_booking', api_views.add_train_booking),
    path('api/edit_train_booking', api_views.edit_train_booking),
    path('api/add_hotel_booking', api_views.add_hotel_booking),
    path('api/edit_hotel_booking', api_views.edit_hotel_booking),
    path('api/add_flight_booking', api_views.add_flight_booking),
    path('api/edit_flight_booking', api_views.edit_flight_booking),

    ################ MIS API ######################
    path('api/report_taxi_booking', api_views.report_taxi_booking),
    path('api/report_bus_booking', api_views.report_bus_booking),
    path('api/report_train_booking', api_views.report_train_booking),
    path('api/report_flight_booking', api_views.report_flight_booking),
    path('api/report_hotel_booking', api_views.report_hotel_booking),

    path('api/generate_auth_token', api_views.generate_auth_token),
    path('api/get_flight_access_token', api_views.get_flight_access_token),
    path('api/get_flight_search', api_views.get_flight_search),
    path('api/get_flight_fare_search', api_views.get_flight_fare_search),
    path('api/save_flight_booking', api_views.save_flight_booking),
    path('api/get_flight_pnr_details', api_views.get_flight_pnr_details),

    path('api/cancel_flight_booking_passengers', api_views.get_flight_pnr_details),
    path('api/add_flight_booking_with_invoice', api_views.add_flight_booking_with_invoice),

    path('api/get_emp_passport_details', api_views.get_emp_passport_details),
    path('api/get_phr_detail_assign_booking', api_views.get_phr_detail_assign_booking),
    path('api/get_corporate_management_tax', api_views.corporate_management_tax),
    path('api/get_po_number_by_corporate', api_views.get_po_number_by_corporate),

    path('api/get_country_provided_by_cotrav', api_views.get_country_provided_by_cotrav),
    path('api/get_visa_type_by_country', api_views.get_visa_type_by_country),
    path('api/get_request_visa_type_by_country', api_views.get_request_visa_type_by_country),
    path('api/get_consulate_office_by_country', api_views.get_consulate_office_by_country),
    path('api/get_instruction_and_link', api_views.get_instruction_and_link),

    path('api/add_visa_requests', api_views.add_visa_requests),
    path('api/view_visa_request', api_views.view_visa_request),
    path('api/company_visa_services', api_views.company_visa_services),
    path('api/company_visa_services_bill', api_views.company_visa_services_bill),
    path('api/delete_visa_document', api_views.delete_visa_document),
    path('api/add_new_employee_visa_document', api_views.add_new_employee_visa_document),

    path('api/add_booking_feedback', api_views.add_booking_feedback),
    path('api/agent_dashboard_sales_by_city', api_views.agent_dashboard_sales_by_city),
    path('api/agent_payment_pending_from_client', api_views.agent_payment_pending_from_client),

    path('api/get_all_frro_status', api_views.get_all_frro_status),
    path('api/add_frro_requests', api_views.add_frro_requests),
    path('api/view_frro_request', api_views.view_frro_request),
    path('api/frro_change_document', api_views.frro_change_document),
    path('api/frro_change_office_status', api_views.frro_change_office_status),
    path('api/frro_change_document_letter', api_views.frro_change_document_letter),
    path('api/add_travelport_locator_code', api_views.add_travelport_locator_code),
    path('api/get_travelport_locator_code', api_views.get_travelport_locator_code),
    path('api/upload_document_get_path', api_views.upload_document_get_path),

    path('api/company_frro_services_bill', api_views.company_frro_services_bill),

    path('api/get_guesthouse_by_corporate', api_views.get_guesthouse_by_corporate),
    path('api/get_guesthouse_from_city_area', api_views.get_guesthouse_from_city_area),
    path('api/get_guesthouse_details', api_views.get_guesthouse_details),
    path('api/add_guesthouse_booking', api_views.add_guesthouse_booking),
    path('api/company_guesthouse_booking', api_views.company_guesthouse_booking),
    path('api/view_guesthouse_booking', api_views.view_guesthouse_booking),
    path('api/report_guesthouse_booking', api_views.report_guesthouse_booking),

    path('api/agent_guesthouse_booking', api_views.agent_guesthouse_booking),
    path('api/add_guesthouse', api_views.add_guesthouse),
    path('api/add_guesthouses_amenities', api_views.add_guesthouses_amenities),
    path('api/add_guesthouses_rooms', api_views.add_guesthouses_rooms),
    path('api/get_guesthouse_rooms', api_views.get_guesthouse_rooms),
    path('api/get_guesthouse_rooms_type', api_views.get_guesthouse_rooms_type),
    path('api/add_guesthouses_room_types', api_views.add_guesthouses_room_types),
    path('api/delete_guesthouse', api_views.delete_guesthouse),
    path('api/delete_guesthouseroom', api_views.delete_guesthouseroom),
    path('api/delete_guesthouseroomtype', api_views.delete_guesthouseroomtype),


]