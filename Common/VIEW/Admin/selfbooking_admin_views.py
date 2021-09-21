from datetime import date, datetime
from django.conf import settings
from django.shortcuts import render, redirect
from time import sleep
from django_global_request.middleware import get_request
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
import razorpay
from Common.VIEW.Admin.admin_views import getDataFromAPI

razorpay_client = razorpay.Client(auth=("rzp_test_eipQBGxGd1SmmJ", "r82J3rVV4NEAZKMGxIJVPyGY"))


def add_flight_booking_self(request,id):
    if request.method == 'POST':
        if 'admin_login_type' in request.session:
            login_type = request.session['admin_login_type']
            access_token = request.session['admin_access_token']

            user_id = request.POST.get('spoc_id', '')
            corporate_id = request.POST.get('corporate_id', '')
            spoc_id = request.POST.get('spoc_id', '')
            group_id = request.POST.get('group_id', '')
            subgroup_id = request.POST.get('subgroup_id', '')

            trip_type = request.POST.get('trip_type', '')
            return_date = request.POST.get('return_date', '')
            fl_class = request.POST.get('fl_class', '')
            no_of_seats = request.POST.get('no_of_seats', '')
            from_city = request.POST.get('from_city', '')
            to_city = request.POST.get('to_city', '')
            departure_date = request.POST.get('departure_date', '')

            booking_data = {'user_id':user_id,'user_type':login_type,'corporate_id':corporate_id,'spoc_id':spoc_id,'group_id':group_id,
                       'subgroup_id':subgroup_id,'from_city':from_city,'to_city':to_city,
                       'departure_datetime':departure_date,'return_date':return_date,'trip_type':trip_type,'fl_class':fl_class,'no_of_seats':no_of_seats}

            payload = {'auth_token':"",'session_id':access_token,'from_city':from_city,'to_city':to_city,'departure_date':departure_date,
                       'fl_class':fl_class,'return_date':return_date,'trip_type':trip_type,'no_of_seats':no_of_seats,}
            print(payload)
            url_flt = settings.API_BASE_URL + "get_flight_search"
            try:
                flightdata = getDataFromAPI(login_type, access_token, url_flt, payload)
            except Exception as e:
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']
                messages.success(request, 'No Flight Found Please Try Another Flight.!')
                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_self.html',
                              {'booking_datas': booking_data, 'flights': '', 'airports': airports})

            #print(flightdata['Data'])
            if 'FLIGHT' in flightdata['Data'] or 'FLIGHTOW' in flightdata['Data']:
                flight = flightdata['Data']
                #print(flight)
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']
                flight1 = ""
                flight2 = ""
                unique_flights1 = ""
                unique_flights2 = ""
                print("trip type")
                print(trip_type)
                if trip_type == '2':
                    flight1 = flight['FLIGHTOW']
                    flight2 = flight['FLIGHTRT']
                    uniq_flights = ''
                    uniq_fl = []
                    uniq_code = []
                    uniq_img = []
                    uniq_flights2 = ''
                    uniq_fl2 = []
                    uniq_code2 = []
                    uniq_img2 = []
                    for fl_name in flight1:
                        if fl_name['F_NAME'] not in uniq_flights:
                            uniq_fl.append(fl_name['F_NAME'])
                            uniq_code.append(fl_name['F_CODE'])
                            uniq_img.append(fl_name['F_LOGO'])
                    for fl_name2 in flight2:
                        if fl_name2['F_NAME'] not in uniq_flights2:
                            uniq_fl2.append(fl_name2['F_NAME'])
                            uniq_code2.append(fl_name2['F_CODE'])
                            uniq_img2.append(fl_name2['F_LOGO'])

                else:
                    flight1 = flight['FLIGHT']
                    uniq_fl = []
                    uniq_code = []
                    uniq_img = []
                    uniq_flights = ''
                    for fl_name in flight1:
                        if fl_name['F_NAME'] not in uniq_flights:
                            uniq_fl.append(fl_name['F_NAME'])
                            uniq_code.append(fl_name['F_CODE'])
                            uniq_img.append(fl_name['F_LOGO'])

                    uniq_flights = set(zip(uniq_fl,uniq_code,uniq_img))
                    print("in trip 1")

                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_serarch_result.html', {'booking_datas': booking_data,'params':flight['PARAM'], 'flights': flight1, 'flights2': flight2,
                'airports':airports,'no_of_seats':no_of_seats, 'uniq_flights':uniq_flights,'unique_flights2':unique_flights2, 'Deals':flight['Deal']})
            else:
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']

                messages.success(request, 'No Flight Found Please Try Another Flight.!')
                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_self.html',{'booking_datas': booking_data, 'flights': '', 'airports':airports})

        else:
            return HttpResponseRedirect("/login")
    else:
        if 'admin_login_type' in request.session:
            request = get_request()
            login_type = request.session['admin_login_type']
            access_token = request.session['admin_access_token']
            payload = {'corporate_id': id,'Admin_id':request.user.id}

            url_access = settings.API_BASE_URL + "get_airports"
            data = getDataFromAPI(login_type, access_token, url_access, payload)
            airports = data['Airports']

            if id:
                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_self.html', {'airports':airports})
            else:
                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_self.html', {})
        else:
            return HttpResponseRedirect("/login")


def add_flight_booking_self_conformation(request,id):
    if 'admin_login_type' in request.session:
        login_type = request.session['admin_login_type']
        access_token = request.session['admin_access_token']

        UID = request.POST.get('UID', '')
        ID = request.POST.get('ID', '')
        TID = request.POST.get('TID', '')

        UID2 = request.POST.get('UID2', '')
        ID2 = request.POST.get('ID2', '')
        TID2 = request.POST.get('TID2', '')

        src = request.POST.get('src', '')
        des = request.POST.get('des', '')
        ret_date = request.POST.get('ret_date', '')
        adt = request.POST.get('adt', '')
        chd = request.POST.get('chd', '')
        inf = request.POST.get('inf', '')
        L_OW = request.POST.get('L_OW', '')
        L_RT = request.POST.get('L_RT', '')
        H_OW = request.POST.get('H_OW', '')
        H_RT = request.POST.get('H_RT', '')
        T_TIME = request.POST.get('T_TIME', '')
        dep_date = request.POST.get('dep_date', '')
        trip_string = request.POST.get('trip_string', '')
        booking_datass = request.POST.get('booking_data', '')
        no_of_seats = request.POST.get('no_of_seats', '')
        departure_datetime = request.POST.get('departure_datetime', '')
        return_datetime = request.POST.get('return_datetime', '')
        flight_class_is_international = request.POST.get('flight_class_is_international', '')
        flight1 = ""
        flight2 = ""
        booking_data = {'UID':UID,'ID':ID,'TID':TID,'UID2':UID2,'ID2':ID2,'TID2':TID2,'src':src,'des':des,'dep_date':dep_date,'ret_date':ret_date,
            'adt':adt,'chd':chd,'inf':inf,'L_OW':L_OW,'H_OW':H_OW,'T_TIME':T_TIME,'trip_string':trip_string,'flight_class_is_international':flight_class_is_international,
            'departure_datetime':departure_datetime,'return_datetime':return_datetime}

        url_tokn = settings.API_BASE_URL + "get_flight_fare_search"
        data = getDataFromAPI(login_type, access_token, url_tokn, booking_data)
        print("DATA TYPE")
        print(type(data))
        if data['success'] == 1:
            api_response = data['Data']
            dayHours_onword = data['dayHours_onword']
            dayHours_return = data['dayHours_return']
            print("SEARCH PAI RESPONSE")

            payload = {'corporate_id': request.user.corporate_id, 'spoc_id': request.user.id}
            url_enty = settings.API_BASE_URL + "billing_entities"
            entys = getDataFromAPI(login_type, access_token, url_enty, payload)
            entities = entys['Entitys']

            url_ass_code = settings.API_BASE_URL + "get_assessment_code"
            ass_code = getDataFromAPI(login_type, access_token, url_ass_code, payload)
            ass_code = ass_code['AssCodes']

            url_cities_ass = settings.API_BASE_URL + "get_assessment_city"
            cities_ass = getDataFromAPI(login_type, access_token, url_cities_ass, payload)
            cities = cities_ass['AssCity']

            url_emp = settings.API_BASE_URL + "employees"
            company_emp = getDataFromAPI(login_type, access_token, url_emp, payload)
            employees = company_emp['Employees']

            url_nat = settings.API_BASE_URL + "get_nationality"
            nationality = getDataFromAPI(login_type, access_token, url_nat, payload)
            nationalities = nationality['Nationality']

            return render(request, 'Company/Admin/Self_Booking/add_flight_booking_conformation.html', {'departure_datetime':departure_datetime,
            'return_datetime':return_datetime,'booking_datas': booking_data, 'flights': api_response, 'UID2': UID2, 'employees': employees,
            'cities_ass': cities,'entities': entities, 'assessments': ass_code, 'no_of_seats':no_of_seats,'dayHours_onword':dayHours_onword,
            'flight_class_is_international':flight_class_is_international,'nationalities':nationalities, 'dayHours_return':dayHours_return})
        else:
            return render(request, 'Company/Admin/Self_Booking/add_flight_booking_conformation.html', {'booking_datas': booking_data, 'flights': ''})

    else:
        return HttpResponseRedirect("/login")


def add_flight_booking_self_final(request, id):
    if 'admin_login_type' in request.session:
        login_type = request.session['admin_login_type']
        access_token = request.session['admin_access_token']

        flightdata = request.POST.get('flightdata', '')
        UID2 = request.POST.get('UID2', '')

        user_id = request.POST.get('spoc_id', '')
        corporate_id = request.POST.get('corporate_id', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        usage_type = request.POST.get('usage_type', '')
        trip_type = request.POST.get('trip_type', '')
        seat_type = request.POST.get('seat_type', '')
        from_city = request.POST.get('from_city', '')
        to_city = request.POST.get('to_city', '')
        booking_datetime = request.POST.get('booking_datetime', '')
        departure_date = request.POST.get('departure_date', '')
        departure_date = datetime.strptime(departure_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        preferred_flight = request.POST.get('preferred_flight', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        entity_id = request.POST.get('entity_id', '')
        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')
        no_of_emp = int(no_of_seats) + 1
        employee_name_1 = request.POST.get('employee_name_1', '')
        flight_class_is_international = request.POST.get('flight_class_is_international', '')
        emp_info_international = []
        emp_data = {}
        if flight_class_is_international:
            for i in range(1, no_of_emp):
                emp_data['emp_id'] =  request.POST.get('emp_id_' + str(i), '')
                emp_data['emp_title'] =  request.POST.get('employee_title_' + str(i), '')
                emp_data['emp_fname'] =  request.POST.get('employee_fname_' + str(i), '')
                emp_data['emp_lname'] =  request.POST.get('employee_lname_' + str(i), '')
                emp_data['emp_dob'] =  request.POST.get('employee_dob_' + str(i), '')
                emp_data['emp_passport_no'] =  request.POST.get('employee_passport_' + str(i), '')
                emp_data['emp_passport_exp'] =  request.POST.get('employee_pass_exp_' + str(i), '')
                emp_data['emp_nationality'] =  request.POST.get('employee_nationality_' + str(i), '')
                emp_info_international.append(emp_data)
        else:
            for i in range(1, no_of_emp):
                emp_data['emp_title'] =  request.POST.get('employee_title_' + str(i), '')
                emp_data['emp_fname'] =  request.POST.get('employee_fname_' + str(i), '')
                emp_data['emp_lname'] =  request.POST.get('employee_lname_' + str(i), '')
                emp_data['emp_dob'] =  request.POST.get('employee_edob_' + str(i), '')
                emp_info_international.append(emp_data)

        if entity_id:
            pass
        else:
            entity_id = 0

        employees = []
        employees_name = []

        for i in range(1, no_of_emp):
            employees.append(request.POST.get('employee_id_' + str(i), ''))
            employees_name.append(request.POST.get('employee_name_' + str(i), ''))
            print(employees)

        payload11 = {'flightdata': flightdata, 'employee_name_1': employees_name,'UID2':UID2,'flight_class_is_international':flight_class_is_international,'emp_info_international':str(emp_info_international)}
        print("adsad")
        #print(payload11)
        url_save = settings.API_BASE_URL + "save_flight_booking"
        booking1 = getDataFromAPI(login_type, access_token, url_save, payload11)
        print("API BOOK")
        print(booking1)
        if not 'RESULT' in booking1['Data']:
            messages.error(request, 'Flight Booking Request Failed..!')
            return HttpResponseRedirect("/Corporate/Self_Booking/Admin/flight-bookings/30", {'message': "Operation Successfully"})

        if 'BOOKINGID' in booking1['Data']['RESULT'][0]:
            vendor_booking = booking1['Data']['RESULT'][0]['BOOKINGID']
        else:
            vendor_booking = ""
        payload = {'user_id': user_id, 'user_type': login_type, 'corporate_id': corporate_id, 'spoc_id': spoc_id,
                   'group_id': group_id,
                   'subgroup_id': subgroup_id, 'usage_type': usage_type, 'trip_type': trip_type, 'seat_type': seat_type,
                   'from_city': from_city, 'to_city': to_city,
                   'booking_datetime': booking_datetime, 'departure_datetime': departure_date,
                   'preferred_flight': preferred_flight, 'assessment_code': assessment_code,
                   'reason_booking': reason_booking, 'no_of_seats': no_of_seats, 'employees': employees,
                   'billing_entity_id': entity_id,
                   'is_sms': 1, 'is_email': 1, 'assessment_city_id': assessment_city_id, 'flightdata': flightdata,'UID2':UID2,
                   'employee_name_1': employee_name_1,'vendor_booking':vendor_booking}
        #print(payload)
        if vendor_booking:
            url_taxi_booking = settings.API_BASE_URL + "add_flight_booking"
            booking = getDataFromAPI(login_type, access_token, url_taxi_booking, payload)

            print("MYBOOOK")
            #print(booking)
            if booking['success'] == 1:
                last_booking_id = booking['last_booking_id']
                booking_reference_no = booking['booking_reference_no']

                for i in range(3):
                    url_save = settings.API_BASE_URL + "get_flight_pnr_details"
                    pnr_no = {'pnr': vendor_booking}
                    booking1 = getDataFromAPI(login_type, access_token, url_save, pnr_no)
                    print(booking1)
                    if 'ERROR' in booking1['Data']:
                        sleep(5)
                    else:
                        if UID2:
                            if booking1['Data']['PAXOW'][0]['apnr']:
                                print("GENP PNPRPPRPRPRPPRPRR ......................")
                                print(booking1['Data']['PAXOW'][0]['apnr'])
                                print("GENP PNPRPPRPRPRPPRPRR ......................")
                                pass
                            else:
                                sleep(5)
                        else:
                            print("GENP PNPRPPRPRPRPPRPRR ......................")
                            print(booking1['Data']['PAX'][0]['apnr'])
                            print("GENP PNPRPPRPRPRPPRPRR ......................")
                            if booking1['Data']['PAX'][0]['apnr']:
                                pass
                            else:
                                sleep(5)

                if not 'FLIGHT' in booking1['Data'] or 'FLIGHTOW' in booking1['Data'] :
                    messages.error(request, 'Booking successful, your CoTrav booking id is - ' +str(booking_reference_no)+ ', but pending for PNR status, please check the status under Pending for PNR tab')
                    return HttpResponseRedirect("/Corporate/Admin/Self_Booking/flight-bookings/30", {'message': "Operation Successfully"})
                else:
                    if UID2:
                        if not 'apnr' in booking1['Data']['PAXOW'][0] or len(booking1['Data']['PAXOW'][0]['apnr']) == 0:
                            messages.error(request, 'Booking successful, your CoTrav booking id is - ' + str(booking_reference_no) + ', but pending for PNR status, please check the status under Pending for PNR tab')
                            return HttpResponseRedirect("/Corporate/Admin/Self_Booking/flight-bookings/30",{'message': "Operation Successfully"})
                        else:
                            pass
                    else:
                        if not 'apnr' in booking1['Data']['PAX'][0] or len(booking1['Data']['PAX'][0]['apnr']) == 0:
                            messages.error(request, 'Booking successful, your CoTrav booking id is - ' +str(booking_reference_no)+ ', but pending for PNR status, please check the status under Pending for PNR tab')
                            return HttpResponseRedirect("/Corporate/Admin/Self_Booking/flight-bookings/2",{'message': "Operation Successfully"})
                        else:
                            pass

                    ticket_number =[]
                    pnr_no =[]
                    flight_no =[]
                    flight_name =[]
                    arrival_time =[]
                    departure_time =[]
                    flight_to =[]
                    flight_from =[]
                    is_return_flight =[]

                    if UID2:
                        no_of_stops = booking1['Data']['FLIGHTOW'][0]['STOP']
                        flight_type = seat_type
                        fare_type = booking1['Data']['FLIGHTOW'][0]['FARE_TYPE']
                        meal_is_include = ''
                        no_of_passanger = booking1['Data']['PARAM'][0]['adt']
                        employee_booking_id = employees
                        ticket_price = booking1['Data']['FLIGHTOW'][0]['AMOUNT']

                        if booking1['Data']['CON_FLIGHTOW']:
                            for flightt in booking1['Data']['CON_FLIGHTOW']:
                                ticket_number.append(booking1['Data']['FLIGHTOW'][0]['PCC'])
                                pnr_no.append(booking1['Data']['PAXOW'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME']+":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(flightt['DEP_DATE'] + " " + flightt['DEP_TIME']+":00",  "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('0')
                        else:
                            ticket_number.append(booking1['Data']['FLIGHTOW'][0]['PCC'])
                            pnr_no.append(booking1['Data']['PAXOW'][0]['apnr'])
                            flight_no.append(booking1['Data']['FLIGHTOW'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['Data']['FLIGHTOW'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(booking1['Data']['FLIGHTOW'][0]['ARRV_DATE'] + " " + booking1['Data']['FLIGHTOW'][0]['ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(booking1['Data']['FLIGHTOW'][0]['DEP_DATE'] + " " + booking1['Data']['FLIGHTOW'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['Data']['FLIGHTOW'][0]['DES_NAME'])
                            flight_from.append(booking1['Data']['FLIGHTOW'][0]['ORG_NAME'])
                            is_return_flight.append('0')


                        if booking1['Data']['CON_FLIGHTRT']:
                            for flightt in booking1['Data']['CON_FLIGHTRT']:
                                ticket_number.append(booking1['Data']['FLIGHTRT'][0]['PCC'])
                                pnr_no.append(booking1['Data']['PAXRT'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime( flightt['DEP_DATE'] + " " + flightt['DEP_TIME'] + ":00","%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('1')
                        else:
                            ticket_number.append(booking1['Data']['FLIGHTRT'][0]['PCC'])
                            pnr_no.append(booking1['Data']['PAXRT'][0]['apnr'])
                            flight_no.append(booking1['Data']['FLIGHTRT'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['Data']['FLIGHTRT'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(booking1['Data']['FLIGHTRT'][0]['ARRV_DATE'] + " " + booking1['Data']['FLIGHTRT'][0]['ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(booking1['Data']['FLIGHTRT'][0]['DEP_DATE'] + " " + booking1['Data']['FLIGHTRT'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['Data']['FLIGHTRT'][0]['DES_NAME'])
                            flight_from.append(booking1['Data']['FLIGHTRT'][0]['ORG_NAME'])
                            is_return_flight.append('1')

                            print("INNNNNNNNNNNN ELSEEEEEEEEEEEEEEEE")


                    else:
                        no_of_stops = booking1['Data']['FLIGHT'][0]['STOP']
                        flight_type = seat_type
                        fare_type = booking1['Data']['FLIGHT'][0]['FARE_TYPE']
                        meal_is_include = ''
                        no_of_passanger = booking1['Data']['FLIGHT'][0]['SEAT']
                        employee_booking_id = employees
                        ticket_price = booking1['Data']['FLIGHT'][0]['AMOUNT']

                        if booking1['Data']['CON_FLIGHT']:
                            for flightt in booking1['Data']['CON_FLIGHT']:
                                ticket_number.append(booking1['Data']['FLIGHT'][0]['PCC'])
                                pnr_no.append(booking1['Data']['PAX'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME']+":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(flightt['DEP_DATE'] + " " + flightt['DEP_TIME']+":00",  "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('0')
                            print("INNNNNNNNNNNN IFFFFFFFFFFFFF")
                        else:
                            ticket_number.append(booking1['Data']['FLIGHT'][0]['PCC'])
                            pnr_no.append(booking1['Data']['PAX'][0]['apnr'])
                            flight_no.append(booking1['Data']['FLIGHT'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['Data']['FLIGHT'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(booking1['Data']['FLIGHT'][0]['ARRV_DATE'] + " " + booking1['Data']['FLIGHT'][0]['ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(booking1['Data']['FLIGHT'][0]['DEP_DATE'] + " " + booking1['Data']['FLIGHT'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['Data']['FLIGHT'][0]['DES_NAME'])
                            flight_from.append(booking1['Data']['FLIGHT'][0]['ORG_NAME'])
                            is_return_flight.append('0')
                            print("INNNNNNNNNNNN ELSEEEEEEEEEEEEEEEE")

                    sub_total = 118+int(ticket_price)

                    url_assign = settings.API_BASE_URL + "assign_flight_booking"
                    payload11 = {'ticket_no': ticket_number, 'pnr_no': pnr_no, 'portal_used': "",
                               'booking_id': last_booking_id, 'user_id': user_id, 'user_type': login_type, 'flight_no': flight_no,
                               'flight_name': flight_name, 'arrival_time': arrival_time,
                               'departure_time': departure_time, 'flight_to': flight_to, 'flight_from': flight_from,
                               'no_of_stops': no_of_stops, 'seat_type': seat_type, 'flight_type': flight_type,
                               'trip_type': trip_type, 'fare_type': fare_type, 'meal_is_include': meal_is_include,
                               'no_of_passanger': no_of_passanger, 'employee_booking_id': employee_booking_id,
                               'ticket_price': ticket_price, 'management_fee': '100',
                               'tax_mng_amt': '18', 'tax_on_management_fee': '18',
                               'tax_on_management_fee_percentage': '18',
                               'sub_total': sub_total,
                               'management_fee_igst': 18, 'management_fee_cgst': 0,
                               'management_fee_sgst': 0,
                               'management_fee_igst_rate': int(ticket_price)*0.18,
                               'management_fee_cgst_rate': 0,
                               'management_fee_sgst_rate': 0, 'cgst': 0, 'sgst': 0,
                               'igst': int(sub_total)*0.18,
                               'oper_ticket_price': ticket_price, 'oper_commission': "",
                               'oper_commission_type': "",
                               'oper_cotrav_billing_entity': "1",
                               'cotrav_billing_entity': '1',
                               'oper_cgst': 0, 'oper_sgst': 0, 'oper_igst': 18,
                               'client_ticket_path': '', 'client_ticket': '1',
                               'vender_ticket': '',
                               'vender_ticket_path': '', 'is_client_sms': '1',
                               'is_client_email': '1',
                               'igst_amount': int(ticket_price)*0.18, 'cgst_amount': 0, 'sgst_amount': 0,
                               'operator_id': '1','vendor_booking_id':vendor_booking,'is_return_flight':is_return_flight,
                               }
                    print("payrol  .....")
                    print(payload11)
                    company11 = getDataFromAPI(login_type, access_token, url_assign, payload11)
                    print(company11)
                    messages.success(request, 'Flight Booking Added Successfully..!')
                    return HttpResponseRedirect("/Corporate/Admin/Self_Booking/flight-bookings/2", {'message': "Operation Successfully"})
            else:
                messages.error(request, 'Flight Booking Not Added..!')
                return HttpResponseRedirect("/Corporate/Admin/Self_Booking/flight-bookings/2", {'message': "Operation Successfully"})
        else:
            messages.error(request, 'Flight Booking Not Added..!')
            return HttpResponseRedirect("/Corporate/Admin/Self_Booking/flight-bookings/2", {'message': "Operation Successfully"})


    else:
        return HttpResponseRedirect("/login")


def add_hotel_booking_self(request,id):
    if request.method == 'POST':
        if 'admin_login_type' in request.session:
            login_type = request.session['admin_login_type']
            access_token = request.session['admin_access_token']

            user_id = request.POST.get('spoc_id', '')
            corporate_id = request.POST.get('corporate_id', '')
            spoc_id = request.POST.get('spoc_id', '')
            group_id = request.POST.get('group_id', '')
            subgroup_id = request.POST.get('subgroup_id', '')

            trip_type = request.POST.get('trip_type', '')
            return_date = request.POST.get('return_date', '')
            fl_class = request.POST.get('fl_class', '')
            no_of_seats = request.POST.get('no_of_seats', '')
            from_city = request.POST.get('from_city', '')
            to_city = request.POST.get('to_city', '')
            departure_date = request.POST.get('departure_date', '')

            booking_data = {'user_id':user_id,'user_type':login_type,'corporate_id':corporate_id,'spoc_id':spoc_id,'group_id':group_id,
                       'subgroup_id':subgroup_id,'from_city':from_city,'to_city':to_city,
                       'departure_datetime':departure_date,'return_date':return_date,'trip_type':trip_type,'fl_class':fl_class,'no_of_seats':no_of_seats}

            payload = {'auth_token':"",'session_id':access_token,'from_city':from_city,'to_city':to_city,'departure_date':departure_date,
                       'fl_class':fl_class,'return_date':return_date,'trip_type':trip_type,'no_of_seats':no_of_seats,}
            print(payload)
            url_flt = settings.API_BASE_URL + "get_flight_search"
            try:
                flightdata = getDataFromAPI(login_type, access_token, url_flt, payload)
            except Exception as e:
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']
                messages.success(request, 'No Flight Found Please Try Another Flight.!')
                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_self.html',
                              {'booking_datas': booking_data, 'flights': '', 'airports': airports})

            #print(flightdata['Data'])
            if 'FLIGHT' in flightdata['Data'] or 'FLIGHTOW' in flightdata['Data']:
                flight = flightdata['Data']
                #print(flight)
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']
                flight1 = ""
                flight2 = ""
                unique_flights1 = ""
                unique_flights2 = ""
                print("trip type")
                print(trip_type)
                if trip_type == '2':
                    flight1 = flight['FLIGHTOW']
                    flight2 = flight['FLIGHTRT']
                    uniq_flights = ''
                    uniq_fl = []
                    uniq_code = []
                    uniq_img = []
                    uniq_flights2 = ''
                    uniq_fl2 = []
                    uniq_code2 = []
                    uniq_img2 = []
                    for fl_name in flight1:
                        if fl_name['F_NAME'] not in uniq_flights:
                            uniq_fl.append(fl_name['F_NAME'])
                            uniq_code.append(fl_name['F_CODE'])
                            uniq_img.append(fl_name['F_LOGO'])
                    for fl_name2 in flight2:
                        if fl_name2['F_NAME'] not in uniq_flights2:
                            uniq_fl2.append(fl_name2['F_NAME'])
                            uniq_code2.append(fl_name2['F_CODE'])
                            uniq_img2.append(fl_name2['F_LOGO'])

                else:
                    flight1 = flight['FLIGHT']
                    uniq_fl = []
                    uniq_code = []
                    uniq_img = []
                    uniq_flights = ''
                    for fl_name in flight1:
                        if fl_name['F_NAME'] not in uniq_flights:
                            uniq_fl.append(fl_name['F_NAME'])
                            uniq_code.append(fl_name['F_CODE'])
                            uniq_img.append(fl_name['F_LOGO'])

                    uniq_flights = set(zip(uniq_fl,uniq_code,uniq_img))
                    print("in trip 1")

                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_serarch_result.html', {'booking_datas': booking_data,'params':flight['PARAM'], 'flights': flight1, 'flights2': flight2,
                'airports':airports,'no_of_seats':no_of_seats, 'uniq_flights':uniq_flights,'unique_flights2':unique_flights2, 'Deals':flight['Deal']})
            else:
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']

                messages.success(request, 'No Flight Found Please Try Another Flight.!')
                return render(request, 'Company/Admin/Self_Booking/add_flight_booking_self.html',{'booking_datas': booking_data, 'flights': '', 'airports':airports})

        else:
            return HttpResponseRedirect("/login")
    else:
        if 'admin_login_type' in request.session:
            request = get_request()
            login_type = request.session['admin_login_type']
            access_token = request.session['admin_access_token']
            payload = {'corporate_id': id,'Admin_id':request.user.id}


            if id:
                return render(request, 'Company/Admin/Self_Booking/self_booking_hotel_search.html', {})
            else:
                return render(request, 'Company/Admin/Self_Booking/self_booking_hotel_search.html', {})
        else:
            return HttpResponseRedirect("/login")


def add_bus_booking_self(request,id):
    if request.method == 'POST':
        if 'admin_login_type' in request.session:
            login_type = request.session['admin_login_type']
            access_token = request.session['admin_access_token']

            user_id = request.POST.get('spoc_id', '')
            corporate_id = request.POST.get('corporate_id', '')
            spoc_id = request.POST.get('spoc_id', '')
            group_id = request.POST.get('group_id', '')
            subgroup_id = request.POST.get('subgroup_id', '')

            trip_type = request.POST.get('trip_type', '')
            return_date = request.POST.get('return_date', '')
            fl_class = request.POST.get('fl_class', '')
            no_of_seats = request.POST.get('no_of_seats', '')
            from_city = request.POST.get('from_city', '')
            to_city = request.POST.get('to_city', '')
            departure_date = request.POST.get('departure_date', '')

            booking_data = {'user_id':user_id,'user_type':login_type,'corporate_id':corporate_id,'spoc_id':spoc_id,'group_id':group_id,
                       'subgroup_id':subgroup_id,'from_city':from_city,'to_city':to_city,
                       'departure_datetime':departure_date,'return_date':return_date,'trip_type':trip_type,'fl_class':fl_class,'no_of_seats':no_of_seats}

            payload = {'auth_token':"",'session_id':access_token,'from_city':from_city,'to_city':to_city,'departure_date':departure_date,
                       'fl_class':fl_class,'return_date':return_date,'trip_type':trip_type,'no_of_seats':no_of_seats,}
            print(payload)
            url_flt = settings.API_BASE_URL + "get_flight_search"
            try:
                flightdata = getDataFromAPI(login_type, access_token, url_flt, payload)
            except Exception as e:
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']
                messages.success(request, 'No Flight Found Please Try Another Flight.!')
                return render(request, 'Company/Admin/Self_Booking/add_bus_booking_serarch_result.html', {'booking_datas': booking_data, 'flights': '', 'airports': airports})

            #print(flightdata['Data'])
            if 'FLIGHT' in flightdata['Data'] or 'FLIGHTOW' in flightdata['Data']:
                flight = flightdata['Data']
                #print(flight)
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)

                return render(request, 'Company/Admin/Self_Booking/add_bus_booking_serarch_result.html', {'booking_datas': booking_data})
            else:
                url_access = settings.API_BASE_URL + "get_airports"
                data11 = getDataFromAPI(login_type, access_token, url_access, payload)
                airports = data11['Airports']

                messages.success(request, 'No Flight Found Please Try Another Flight.!')
                return render(request, 'Company/Admin/Self_Booking/add_bus_booking_serarch_result.html',{'booking_datas': booking_data, 'flights': '', 'airports':airports})

        else:
            return HttpResponseRedirect("/login")
    else:
        if 'admin_login_type' in request.session:
            request = get_request()
            login_type = request.session['admin_login_type']
            access_token = request.session['admin_access_token']
            payload = {'corporate_id': id,'Admin_id':request.user.id}

            url_access = settings.API_BASE_URL + "get_airports"
            data11 = getDataFromAPI(login_type, access_token, url_access, payload)
            airports = data11['Airports']

            if id:
                return render(request, 'Company/Admin/Self_Booking/add_bus_booking_self.html', {'airports':airports})
            else:
                return render(request, 'Company/Admin/Self_Booking/add_bus_booking_self.html', {})
        else:
            return HttpResponseRedirect("/login")