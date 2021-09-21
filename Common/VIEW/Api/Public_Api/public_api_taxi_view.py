import json
import traceback
from threading import Thread

from django.http import JsonResponse
from django.db import connection
from Common.VIEW.Api.api_views import getUserinfoFromAccessToken, dictfetchall
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime
from django.utils import timezone
import pytz

from Common.email_settings import FCM, AddBooking_Email


def get_corporate_auth_token(request):
    received_json_data = json.loads(request.body)
    if not all(k in received_json_data for k in ("corporate_id", "user_id", "user_password")):
        data = {'success': 0, 'message': "Missing Parameter Value Try Again"}
        return JsonResponse(data)

    corporate_id = received_json_data['corporate_id']
    user_id = received_json_data['user_id']
    user_password = received_json_data['user_password']
    if corporate_id and user_id and user_password:
        cursor = connection.cursor()
        cursor.callproc('getApiCorporateDetails', [corporate_id, user_id])
        user = dictfetchall(cursor)
        if user:
            if user[0]['is_active']:
                password = check_password(user_password, user[0]['corporate_user_password'])
                if password:
                    data = {'success': 1, 'message': 'user details match successfully', 'access_token':user[0]['access_token']}
                    return JsonResponse(data)
                else:
                    data = {'success': 0, 'message': 'Invalid User Name Or Password'}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'message': 'User Expire Please Contact to Admin'}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'message': 'Invalid User'}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'message': 'Invalid User Name Or Password'}
        return JsonResponse(data)


def create_taxi_booking(request):
    if 'AUTHORIZATION' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = '14'
        user_id = '1'
        booking_email = None
        assessment_code =0
        reporting_manager =0
        received_json_data = json.loads(request.body)
        if not all (k in received_json_data for k in ("travel_request_number","tour_type", "pickup_city", "pickup_location","drop_location","pickup_date",
            "pickup_time","taxi_type","package_name","no_of_days","reason_booking","project_city","ProjectCode","Passengers")):
            data = {'success': 0, 'message': "Missing Parameter Value Try Again"}
            return JsonResponse(data)
        if received_json_data:
            bta_code_travel_req_no = received_json_data['travel_request_number']
            tour_type = received_json_data['tour_type']
            pickup_city = received_json_data['pickup_city']
            pickup_location = received_json_data['pickup_location']
            drop_location = received_json_data['drop_location']
            pickup_date = received_json_data['pickup_date']
            pickup_time = received_json_data['pickup_time']
            taxi_type = received_json_data['taxi_type']
            package_name = received_json_data['package_name']
            no_of_days = received_json_data['no_of_days']
            reason_booking = received_json_data['reason_booking']
            no_of_seats = 1
            checkin_datetime = ''
            checkout_datetime = ''
            assessment_city_id = received_json_data['project_city']
            employees = list()

            if not ('Passengers' in received_json_data):
                data = {'success': 0, 'message': "Missing Passengers Information"}
                return JsonResponse(data)

            if bta_code_travel_req_no and tour_type and pickup_city and pickup_location and drop_location and pickup_date and pickup_time and taxi_type and package_name and no_of_days:
                if booking_email:
                    pass
                else:
                    booking_email = ''
                user_token = req_token.split()
                if user_token[0] == 'Token':
                    user = {}
                    try:
                        cursor2 = connection.cursor()
                        cursor2.callproc('getApiCorporateDetailsByAccessToken', [user_token[1]])
                        user = dictfetchall(cursor2)
                        cursor2.close()
                    except Exception as e:
                        data = {'success': 0, 'message': "Please Send Employee Information"}
                        return JsonResponse(data)
                    if user:

                        try:
                            if pickup_date and pickup_time :
                                pickup_datetime = datetime.strptime(pickup_date + " " + pickup_time, '%d-%m-%Y %H:%M')

                            else:
                                data = {'success': 0, 'message': "Incorrect Date/Time format, should be DD-MM-YYYY/HH:MM"}
                                return JsonResponse(data)
                        except ValueError:
                            data = {'success': 0, 'message': "Incorrect Date/Time format, should be DD-MM-YYYY/HH:MM"}
                            return JsonResponse(data)

                        corporate_id = user[0]['corporate_id']
                        billing_entity_id = user[0]['billing_entity_id']
                        spoc_id = user[0]['spoc_id']
                        no_of_seats = len(received_json_data['Passengers'])
                        group_id = 0
                        subgroup_id = 0
                        timezone.activate(pytz.timezone("Asia/Kolkata"))
                        booking_datetime = timezone.localtime(timezone.now())
                        cursor = connection.cursor()

                        if pickup_city:
                            cursor3 = connection.cursor()
                            cursor3.callproc('getCityId', [pickup_city])
                            from_city = dictfetchall(cursor3)
                            if not from_city:
                                data = {'success': 0, 'message': "Your input City not added in our database please contact to admin"}
                                return JsonResponse(data)
                            else:
                                pickup_city = from_city[0]['id']

                            cursor3.close()

                        if package_name and int(tour_type) != 1 :
                            cursor3 = connection.cursor()
                            cursor3.callproc('getPackageIdByPackageName', [package_name])
                            from_city = dictfetchall(cursor3)
                            if not from_city:
                                data = {'success': 0, 'message': "Your input package not added in our database please contact to admin"}
                                return JsonResponse(data)
                            else:
                                package_name = from_city[0]['id']
                            cursor3.close()


                        if ('ProjectCode' in received_json_data) :
                            for ass in received_json_data['ProjectCode']:
                                cursor3 = connection.cursor()
                                if ass['project_code'] and ass['valid_from_date'] and ass['valid_to_date']:
                                    valid_from_date = datetime.strptime(ass['valid_from_date'], '%d-%m-%Y')
                                    valid_to_date = datetime.strptime(ass['valid_to_date'], '%d-%m-%Y')
                                    service_from_date = datetime.strptime(ass['valid_from_date'], '%d-%m-%Y')
                                    service_to_date = datetime.strptime(ass['valid_to_date'], '%d-%m-%Y')
                                    cursor3.callproc('getAssessmentCodeIDByName', [corporate_id, ass['project_code'], ass['code_description'],valid_from_date,
                                    valid_to_date,service_from_date,service_to_date])
                                    assessment_code = dictfetchall(cursor3)
                                    cursor3.close()
                                    print(assessment_code)
                                    assessment_code = assessment_code[0]['id']
                                else:
                                    data = {'success': 0, 'message': "Please Provide Assessment Code Service Date"}
                                    return JsonResponse(data)
                        else:
                            assessment_code = 0
                        if assessment_city_id:
                            cursor3 = connection.cursor()
                            cursor3.callproc('getAssessmentCityIDByName', [assessment_city_id, corporate_id])
                            assessment_city_id = dictfetchall(cursor3)
                            cursor3.close()
                            assessment_city_id = assessment_city_id[0]['id']
                        else:
                            assessment_city_id = 0

                        for pa in received_json_data['Passengers']:

                            if pa['is_cxo']:
                                assistant_id=0
                                for paa in pa['assistant_id']:
                                    if paa['employee_id'] and paa['employee_name'] and paa['employee_email'] and paa['employee_contact']:
                                        cursor3 = connection.cursor()
                                        cursor3.callproc('updateEmployeeAndGetEmployeeID',
                                                         [paa['employee_id'], paa['payroll_employee_id'], paa['title'], paa['employee_name'],
                                                          paa['employee_email'], paa['employee_contact'], paa['age'], paa['gender'],
                                                          paa['id_proof_type'], paa['id_proof_no'], paa['is_cxo'],
                                                          paa['designation'], paa['home_city_id'], paa['home_address'],
                                                          0, paa['employee_band'], 0, paa['date_of_birth'],
                                                          make_password("taxi123"), corporate_id, spoc_id, billing_entity_id])
                                        room_type = dictfetchall(cursor3)
                                        assistant_id = str(room_type[0]['id'])
                                        cursor3.close()
                                    else:
                                        data = {'success': 0, 'message': "Employee Basic Fields Required.."}
                                        return JsonResponse(data)
                            else:
                                assistant_id =0

                            for paar in pa['reporting_manager']:
                                if paar['employee_id'] and paar['employee_name'] and paar['employee_email'] and paar['employee_contact']:
                                    cursor3 = connection.cursor()
                                    cursor3.callproc('updateEmployeeAndGetEmployeeID',
                                                     [paar['employee_id'], paar['payroll_employee_id'], paar['title'],paar['employee_name'],
                                                      paar['employee_email'], paar['employee_contact'], paar['age'], paar['gender'],
                                                      paar['id_proof_type'], paar['id_proof_no'], paar['is_cxo'], paar['designation'], paar['home_city_id'], paar['home_address'],
                                                      0, paar['employee_band'], 0, paar['date_of_birth'], make_password("taxi123"), corporate_id, spoc_id,
                                                      billing_entity_id])
                                    room_type = dictfetchall(cursor3)
                                    reporting_manager = str(room_type[0]['id'])
                                    cursor3.close()
                                else:
                                    data = {'success': 0, 'message': "Employee Basic Fields Required.."}
                                    return JsonResponse(data)

                            if pa['employee_id'] and pa['employee_name'] and pa['employee_email'] and pa['employee_contact']:
                                cursor3 = connection.cursor()
                                cursor3.callproc('updateEmployeeAndGetEmployeeID',[pa['employee_id'], pa['payroll_employee_id'], pa['title'], pa['employee_name'],
                                pa['employee_email'], pa['employee_contact'], pa['age'], pa['gender'],pa['id_proof_type'], pa['id_proof_no'], pa['is_cxo'],
                                pa['designation'], pa['home_city_id'], pa['home_address'], reporting_manager, pa['employee_band'], assistant_id, pa['date_of_birth'],
                                make_password("taxi123"), corporate_id, spoc_id, billing_entity_id])
                                room_type = dictfetchall(cursor3)
                                employees.append(str(room_type[0]['id']))
                                cursor3.close()

                        employees = set(employees)
                        employees = ','.join(employees)

                        try:
                            booking_reference_no = ''
                            cursor.callproc('addTaxiBooking',
                                            [user_type, user_id, billing_entity_id, corporate_id, spoc_id, group_id, subgroup_id, tour_type, pickup_city, pickup_location, drop_location,
                                             pickup_datetime,taxi_type, package_name, no_of_days, reason_booking, no_of_seats, assessment_code, assessment_city_id, employees, booking_datetime,
                                             booking_email, '@last_booking_id', '@booking_reference_no', bta_code_travel_req_no])
                            booking_id = dictfetchall(cursor)
                            if booking_id:
                                data = {'success': 0, 'message': "Error in Data Insert Please Contact To Admin"}
                                return JsonResponse(data)
                            else:
                                cursor.execute("SELECT @last_booking_id")
                                last_booking_id = cursor.fetchone()[0]
                                cursor.close()

                                cursor12 = connection.cursor()
                                cursor12.execute("SELECT @booking_reference_no")
                                booking_reference_no = cursor12.fetchone()[0]
                                cursor12.close()

                                cursor2 = connection.cursor()
                                cursor2.callproc('viewTaxiBooking', [last_booking_id])
                                emp = dictfetchall(cursor2)
                                cursor2.close()

                                cursor1 = connection.cursor()
                                cursor1.callproc('getAllTaxiBookingPassangers', [last_booking_id])
                                passanger = dictfetchall(cursor1)
                                emp[0]['Passangers'] = passanger
                                cursor1.close()

                                cursor3 = connection.cursor()
                                cursor3.callproc('getAllApproverByBookingID', [last_booking_id, 1])
                                approvers = dictfetchall(cursor3)
                                cursor3.close()

                                fcm = FCM()
                                thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Taxi"))
                                thread.start()

                                add_booking_email = AddBooking_Email()
                                thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Taxi"))
                                thread.start()
                                thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Taxi"))
                                thread.start()
                                #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Taxi")

                            data = {'success': 1, 'message': "Taxi Booking Added Successfully..! Your Booking ID is : " + str(booking_reference_no), 'booking_id': booking_reference_no}
                            return JsonResponse(data)

                        except Exception as e:
                            print("EXCEPTION")
                            print(e)
                            data = {'success': 0, 'message': "Error in Data Insert Please Contact To Admin"}
                            return JsonResponse(data)

                    else:
                        data = {'success': 0, 'message': "User Information Not Found"}
                        return JsonResponse(data)
                else:
                    data = {'success': 0, 'message': "Token Not Found"}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'message': "Please Send Data in JSON Format.."}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_taxi_booking(request):
    if 'AUTHORIZATION' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        received_json_data = json.loads(request.body)
        if not all (k in received_json_data for k in ("service_type","from_date", "to_date", "booking_id")):
            data = {'success': 0, 'message': "Missing Parameter Value Try Again"}
            return JsonResponse(data)

        if received_json_data:
            service_type = received_json_data['service_type']
            from_date = received_json_data['from_date']
            to_date = received_json_data['to_date']
            booking_id = received_json_data['booking_id']

            if not service_type:
                service_type = 0

            if from_date and to_date:
                try:
                    from_date = datetime.strptime(from_date, '%d-%m-%Y')
                    to_date = datetime.strptime(to_date, '%d-%m-%Y')
                except ValueError:
                    data = {'success': 0, 'message': "Incorrect Date/Time format, should be DD-MM-YYYY"}
                    return JsonResponse(data)
            else:
                pass

            user_token = req_token.split()
            if user_token[0] == 'Token':
                user = {}
                try:
                    cursor2 = connection.cursor()
                    cursor2.callproc('getApiCorporateDetailsByAccessToken', [user_token[1]])
                    user = dictfetchall(cursor2)
                    cursor2.close()
                except Exception as e:
                    data = {'success': 0, 'message': "Corporate Information Not Found"}
                    return JsonResponse(data)
                if user:

                    final_data = {}
                    corporate_id = user[0]['corporate_id']
                    cursor2 = connection.cursor()
                    cursor2.callproc('getPublicApiCorporateBookings', [corporate_id,service_type,from_date,to_date,booking_id,1])
                    data = dictfetchall(cursor2)
                    cursor2.close()
                    print(type(data))

                    for i, e in enumerate(data):

                        jsondata = {}
                        rq_details = {}
                        code_details = {}
                        taxi_details = {}
                        driver_details = {}
                        package_details = {}
                        company_details = {}
                        spoc_details = {}
                        invoice_details = {}
                        bill_details = {}
                        try:
                            rq_details['booking_id'] = e['booking_id']
                            rq_details['travel_request_number'] = e['bta_code_travel_req_no']
                            rq_details['from_city'] = e['city_name']
                            rq_details['pickup_location'] = e['pickup_location']
                            rq_details['drop_location'] = e['drop_location']
                            rq_details['pickup_date'] = e['pickup_date']
                            rq_details['pickup_time'] = e['pickup_time']
                            rq_details['booking_date'] = e['booking_date']
                            rq_details['booking_time'] = e['booking_time']
                            rq_details['no_of_seats'] = e['no_of_seats']
                            rq_details['taxi_type'] = e['taxi_type_request']
                            rq_details['cotrav_status'] = e['cotrav_status']
                            rq_details['client_status'] = e['client_status']
                            rq_details['project_city'] = e['assessment_city']
                            jsondata['RequestDetails'] = rq_details

                            code_details['project_code'] = e['assessment_code']
                            code_details['code_description'] = e['code_desc']
                            code_details['valid_from_date'] = e['valid_from_date']
                            code_details['valid_to_date'] = e['valid_to_date']
                            jsondata['ProjectCode'] = code_details

                            driver_details['driver_name'] = e['driver_name']
                            driver_details['driver_contact'] = e['driver_contact']
                            driver_details['licence_no'] = e['licence_no']
                            driver_details['driver_email'] = e['driver_email']
                            jsondata['DriverDetails'] = driver_details

                            taxi_details['brand_name'] = e['brand_name']
                            taxi_details['model_name'] = e['model_name']
                            taxi_details['taxi_reg_no'] = e['taxi_reg_no']
                            taxi_details['taxi_type'] = e['taxi_type_name']
                            jsondata['TaxiDetails'] = taxi_details

                            package_details['package_name'] = e['package_name']
                            package_details['base_rate'] = e['base_rate']
                            package_details['kms_included'] = e['kms']
                            package_details['hours_included'] = e['hours']
                            package_details['extra_km_rate'] = e['km_rate']
                            package_details['extra_hr_rate'] = e['hour_rate']
                            package_details['driver_allowance'] = e['night_rate']
                            jsondata['PackageDetails'] = package_details

                            company_details['company_name'] = e['corporate_name']
                            company_details['contact_person_name'] = e['contact_person_name']
                            company_details['contact_person_no'] = e['contact_person_no']
                            company_details['contact_person_email'] = e['contact_person_email']
                            jsondata['CompanyDetails'] = company_details

                            spoc_details['spoc_name'] = e['spoc_name']
                            spoc_details['spoc_contact'] = e['spoc_contact']
                            spoc_details['spoc_email'] = e['spoc_email']
                            jsondata['SpocDetails'] = spoc_details

                            invoice_details['per_night_cost'] = e['base_price']
                            invoice_details['management_fee'] = e['management_fee']
                            invoice_details['tax_on_management_fee'] = e['tax_on_management_fee']
                            invoice_details['sub_total'] = e['sub_total']
                            invoice_details['company_status'] = e['invoice_status']
                            invoice_details['status_cotrav'] = e['invoice_status_cotrav']
                            jsondata['InvoiceDetails'] = invoice_details

                            bill_details['bill_number'] = e['bill_number']
                            bill_details['bill_created_date'] = e['bill_created_date']
                            bill_details['bill_total_amount'] = e['bill_total_amount']
                            bill_details['tds_deducted_by_client'] = e['tds_deducted_by_client']
                            bill_details['system_calculated_tds'] = e['system_calculated_tds']
                            bill_details['igst'] = e['bill_igst']
                            bill_details['cgst'] = e['bill_cgst']
                            bill_details['sgst'] = e['bill_sgst']
                            bill_details['management_fee'] = e['management_fee']
                            bill_details['outstanding_pending_payment'] = e['outstanding_pending_payment']
                            bill_details['paid_total_amount'] = e['paid_total_amount']
                            bill_details['balance_total_amount'] = e['balance_total_amount']
                            bill_details['advance_payment'] = e['advance_payment']
                            bill_details['taxable_amount'] = e['taxable_amount']
                            bill_details['nontaxable_amount'] = e['nontaxable_amount']
                            jsondata['BillDetails'] = bill_details

                            cursor1 = connection.cursor()
                            booking_id = e['id']
                            cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                            passanger = dictfetchall(cursor1)
                            e['Passengers'] = passanger
                            cursor1.close()
                            jsondata['Passengers'] = passanger

                            final_data[i] = jsondata

                        except Exception as e:
                            data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                            return JsonResponse(data)

                    data = {'success': 1, 'message': "Booking Found", 'Bookings': final_data}
                    return JsonResponse(data)
                else:
                    data = {'success': 0, 'message': "User Information Not Found"}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'message': "Token Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'message': "Please Send Data in JSON Format.."}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)
