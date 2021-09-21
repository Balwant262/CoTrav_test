import json
import traceback

from django.http import JsonResponse
from django.db import connection
from Common.VIEW.Api.api_views import getUserinfoFromAccessToken, dictfetchall
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime
from django.utils import timezone
import pytz
from Common.email_settings import FCM, AddBooking_Email
from threading import Thread

def create_flight_booking(request):
    if 'AUTHORIZATION' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = '14'
        user_id = '1'
        booking_email = None
        assessment_code =0
        reporting_manager =0
        received_json_data = json.loads(request.body)
        if not all (k in received_json_data for k in ("travel_request_number","usage_type", "trip_type", "seat_type","from_city","to_city",
            "preferred_flight","departure_date","departure_time","return_date","return_time","reason_booking","project_city","ProjectCode","Passengers")):
            data = {'success': 0, 'message': "Missing Parameter Value Try Again"}
            return JsonResponse(data)
        if received_json_data:
            bta_code_travel_req_no = received_json_data['travel_request_number']
            usage_type = received_json_data['usage_type']
            trip_type = received_json_data['trip_type']
            seat_type = received_json_data['seat_type']
            from_city = received_json_data['from_city']
            to_city = received_json_data['to_city']
            preferred_flight = received_json_data['preferred_flight']
            departure_date = received_json_data['departure_date']
            departure_time = received_json_data['departure_time']
            return_date = received_json_data['return_date']
            return_time = received_json_data['return_time']
            reason_booking = received_json_data['reason_booking']
            no_of_seats = 1
            departure_datetime = ''
            return_datetime = ''
            assessment_city_id = received_json_data['project_city']
            employees = list()

            if not ('Passengers' in received_json_data):
                data = {'success': 0, 'message': "Missing Passengers Information"}
                return JsonResponse(data)

            if bta_code_travel_req_no and from_city and to_city and usage_type and trip_type and seat_type and departure_date and departure_time and return_date and return_time:
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
                            if departure_date and departure_time and return_date and return_time:
                                departure_datetime = datetime.strptime(departure_date + " " + departure_time, '%d-%m-%Y %H:%M')
                                return_datetime = datetime.strptime(return_date + " " + return_time, '%d-%m-%Y %H:%M')
                            else:
                                data = {'success': 0, 'message': "Incorrect Date/Time format, should be DD-MM-YYYY/HH:MM"}
                                return JsonResponse(data)
                        except ValueError:
                            data = {'success': 0, 'message': "Incorrect Date/Time format, should be DD-MM-YYYY/HH:MM"}
                            return JsonResponse(data)

                        corporate_id = user[0]['corporate_id']
                        billing_entity_id = user[0]['billing_entity_id']
                        spoc_id = user[0]['spoc_id']
                        group_id = 0
                        subgroup_id = 0
                        timezone.activate(pytz.timezone("Asia/Kolkata"))
                        booking_datetime = timezone.localtime(timezone.now())
                        cursor = connection.cursor()

                        cursor3 = connection.cursor()
                        cursor3.callproc('getAirportsIdByAirportsCodeAndName', [from_city])
                        from_city = dictfetchall(cursor3)
                        if not from_city:
                            data = {'success': 0,
                                    'message': "Your input Airport not added in our database please contact to admin"}
                            return JsonResponse(data)
                        else:
                            from_city = from_city[0]['id']

                        cursor3.close()

                        cursor3 = connection.cursor()
                        cursor3.callproc('getAirportsIdByAirportsCodeAndName', [to_city])
                        from_city1 = dictfetchall(cursor3)
                        if not from_city1:
                            data = {'success': 0,
                                    'message': "Your input Airport not added in our database please contact to admin"}
                            return JsonResponse(data)
                        else:
                            to_city = from_city1[0]['id']

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
                                                     [paar['employee_id'], paar['payroll_employee_id'], paar['title'], paar['employee_name'],
                                                      paar['employee_email'], paar['employee_contact'], paar['age'], paar['gender'],
                                                      paar['id_proof_type'], paar['id_proof_no'], paar['is_cxo'], paar['designation'], paar['home_city_id'], paar['home_address'],
                                                      0, paar['employee_band'], 0, paar['date_of_birth'], make_password("taxi123"), corporate_id, spoc_id, billing_entity_id])
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
                            vendor_booking = ''
                            cursor.callproc('addFlightBooking',
                                            [usage_type, trip_type, seat_type, from_city, to_city,
                                             booking_datetime, departure_datetime,
                                             preferred_flight, assessment_code, no_of_seats, group_id, subgroup_id,
                                             spoc_id, corporate_id, billing_entity_id, reason_booking, user_id,
                                             user_type, employees, booking_email, assessment_city_id,
                                             '@last_booking_id', vendor_booking, '@booking_reference_no',
                                             bta_code_travel_req_no, return_datetime])
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
                                cursor2.callproc('viewFlightBooking', [last_booking_id])
                                emp = dictfetchall(cursor2)
                                cursor2.close()

                                cursor1 = connection.cursor()
                                cursor1.callproc('getAllFlightBookingPassangers', [last_booking_id])
                                passanger = dictfetchall(cursor1)
                                emp[0]['Passangers'] = passanger
                                cursor1.close()

                                cursor3 = connection.cursor()
                                cursor3.callproc('getAllApproverByBookingID', [last_booking_id, 1])
                                approvers = dictfetchall(cursor3)
                                cursor3.close()

                                fcm = FCM()
                                thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Flight"))
                                thread.start()
                                add_booking_email = AddBooking_Email()
                                thread = Thread(target=add_booking_email.send_taxi_email,
                                                args=(emp, approvers, "Flight"))
                                thread.start()
                                thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Flight"))
                                thread.start()

                            data = {'success': 1, 'message': "Flight Booking Added Successfully..! Your Booking ID is : " + str(booking_reference_no), 'booking_id': booking_reference_no}
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


def get_flight_booking(request):
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
                    cursor2.callproc('getPublicApiCorporateBookings', [corporate_id,service_type,from_date,to_date,booking_id,5])
                    data = dictfetchall(cursor2)
                    cursor2.close()
                    print(type(data))

                    for i, e in enumerate(data):

                        jsondata = {}
                        f_data = []
                        rq_details = {}
                        assign_details = {}
                        ow_flight_details = {}
                        code_details = {}
                        rt_flight_details = {}
                        company_details = {}
                        spoc_details = {}
                        invoice_details = {}
                        bill_details = {}
                        try:
                            rq_details['booking_id'] = e['booking_id']
                            rq_details['travel_request_number'] = e['travel_request_number']
                            rq_details['usage_type'] = e['usage_type']
                            rq_details['journey_type'] = e['journey_type']
                            rq_details['flight_class'] = e['flight_class']
                            rq_details['from_airport'] = e['from_location']
                            rq_details['to_airport'] = e['to_location']
                            rq_details['departure_date'] = e['departure_datetime']
                            rq_details['return_date'] = e['return_datetime']
                            rq_details['booking_date'] = e['booking_date']
                            rq_details['booking_time'] = e['booking_time']
                            rq_details['preferred_flight'] = e['preferred_flight']
                            rq_details['no_of_seats'] = e['no_of_seats']
                            rq_details['cotrav_status'] = e['cotrav_status']
                            rq_details['client_status'] = e['client_status']
                            rq_details['project_city'] = e['assessment_city']
                            jsondata['RequestDetails'] = rq_details

                            code_details['project_code'] = e['assessment_code']
                            code_details['code_description'] = e['code_desc']
                            code_details['valid_from_date'] = e['valid_from_date']
                            code_details['valid_to_date'] = e['valid_to_date']
                            jsondata['ProjectCode'] = code_details

                            assign_details['usage_type'] = e['flight_type']
                            assign_details['journey_type'] = e['seat_type']
                            assign_details['flight_class'] = e['trip_type']
                            assign_details['fare_type'] = e['fare_type']
                            assign_details['is_meal_include'] = e['meal_is_include']
                            assign_details['no_of_stops'] = e['no_of_stops']
                            assign_details['return_flight_no_of_stops'] = e['return_no_of_stops']
                            assign_details['operator_contact'] = e['operator_name']
                            assign_details['operator_contact'] = e['operator_contact']
                            jsondata['AssignFlightDetails'] = assign_details

                            cursor2 = connection.cursor()
                            booking_id = e['id']
                            cursor2.callproc('getAllFlightBookingFlights', [booking_id])
                            flights = dictfetchall(cursor2)
                            json_text = ''

                            if e['journey_type'] == 'One Way':
                                json_text = 'FlightDetails'
                            else:
                                json_text = 'OnwordsFlightDetails'
                            for i, f in enumerate(flights):

                                if int(f['is_return_flight']) == 1:
                                    rt_flight_details['flight_name'] = f['flight_name']
                                    rt_flight_details['flight_no'] = f['flight_no']
                                    rt_flight_details['pnr_no'] = f['pnr_no']
                                    rt_flight_details['from_city'] = f['from_city']
                                    rt_flight_details['to_city'] = f['to_city']
                                    rt_flight_details['departure_date'] = dateonly(f['departure_datetime'])
                                    rt_flight_details['departure_time'] = timeonly(f['departure_datetime'])
                                    rt_flight_details['arrival_date'] = dateonly(f['arrival_datetime'])
                                    rt_flight_details['arrival_time'] = timeonly(f['arrival_datetime'])
                                    jsondata['ReturnFlightDetails'] = rt_flight_details
                                else:
                                    print(f['from_city'])
                                    ow_flight_details['flight_name'] = f['flight_name']
                                    ow_flight_details['flight_no'] = f['flight_no']
                                    ow_flight_details['pnr_no'] = f['pnr_no']
                                    ow_flight_details['from_city'] = f['from_city']
                                    ow_flight_details['to_city'] = f['to_city']
                                    ow_flight_details['departure_date'] = dateonly(f['departure_datetime'])
                                    ow_flight_details['departure_time'] = timeonly(f['departure_datetime'])
                                    ow_flight_details['arrival_date'] = dateonly(f['arrival_datetime'])
                                    ow_flight_details['arrival_time'] = timeonly(f['arrival_datetime'])
                                    f_data.append(ow_flight_details)
                                    ow_flight_details = {}
                                    print(f_data)
                            cursor2.close()

                            jsondata[json_text] = f_data

                            company_details['company_name'] = e['corporate_name']
                            company_details['contact_person_name'] = e['contact_person_name']
                            company_details['contact_person_no'] = e['contact_person_no']
                            company_details['contact_person_email'] = e['contact_person_email']
                            jsondata['CompanyDetails'] = company_details

                            spoc_details['spoc_name'] = e['spoc_name']
                            spoc_details['spoc_contact'] = e['spoc_contact']
                            spoc_details['spoc_email'] = e['spoc_email']
                            jsondata['SpocDetails'] = spoc_details

                            invoice_details['base_rate'] = e['per_night_cost']
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
                            cursor1.callproc('getAllFlightBookingPassangers', [booking_id])
                            passanger = dictfetchall(cursor1)
                            e['Passengers'] = passanger
                            cursor1.close()
                            jsondata['Passengers'] = passanger

                            final_data[i] = jsondata

                        except Exception as e:
                            print(traceback.print_exc())
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


def dateonly(dt=''):
    try:
        if(dt):
            datetime_str = dt
            datetime_object = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M')
            booking_date = str(datetime_object.day) + "-" + str(datetime_object.month) + "-" + str(datetime_object.year)
            return booking_date
        else:
            return ''
    except ValueError:
        return ''


def timeonly(dt=''):
    try:
        if(dt):
            datetime_str = dt
            datetime_object = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M')
            booking_time = str(datetime_object.hour) + ":" + str(datetime_object.hour)
            return booking_time
        else:
            return ''
    except ValueError :
        return ''