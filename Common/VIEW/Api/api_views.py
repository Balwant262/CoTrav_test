import os
import traceback
from datetime import datetime
import base64
from threading import Thread
from CoTrav import settings
from django.core.files.storage import default_storage
import sys
from django.utils.timesince import timesince
from dateutil.parser import parse
import json
import requests
from django.utils import timezone
import pytz
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.db import connection
from Common.models import Corporate_Login
from Common.models import Corporate_Spoc_Login
from Common.models import Corporate_Employee_Login
from Common.models import Corporate_Approves_1_Login
from Common.models import Corporate_Approves_2_Login
from Common.models import Corporate_Agent
from Common.models import Operator_Login


from Common.models import Corporate_Login_Access_Token
from Common.models import Corporate_Spoc_Login_Access_Token
from Common.models import Corporate_Employee_Login_Access_Token
from Common.models import Corporate_Approves_1_Login_Access_Token
from Common.models import Corporate_Approves_2_Login_Access_Token
from Common.models import Corporate_Agent_Login_Access_Token
from Common.models import Operator_Login_Access_Token
from Common.models import Operator_Driver_Access_Token
from Common.models import Operator_Driver

from django.contrib.auth.hashers import check_password
import string
import random
from Common.email_settings import SignIn_OTP, AddBooking_Email, newUserAdd_Email, Assign_Booking_Email, FCM, SignupEmail
from landing.cotrav_messeging import Flight, TaxCalc
from landing.forms import LeadGenerationModelForm, LeadUpdateForm
from landing.leads_generation import file_upload
from landing.models import Leadgeneration, LeadComments, LeadLog, Document
from Common.email_settings import SignupEmail,Lead_Status_Change_Email, FrroChangeDoucumentRequestLetter_Email,FrroChangeOfficeStatus_Email

COTRAV_EMAILS = "balwant@taxiaxi.in,chauhanbalwant007@gmail.com"
COTRAV_NUMBERS = "9579477262,"


def login(request):
    user_name = request.POST.get('user_name', '')
    user_password = request.POST.get('user_password', '')
    user_type = request.POST.get('user_type', '')

    if user_type == '8':
        user_name = request.POST.get('mobile_no', '')
        user_password = "taxi123"

    is_mobile = request.POST.get('is_mobile', '')
    if is_mobile == '1':
        user_info = request.POST.get('user_info', '')
    else:
        user_info = request.META['HTTP_USER_AGENT']

    if user_name and user_password and user_type:
        cursor = connection.cursor()
        cursor.callproc('getLoginDetails', [user_name,user_type])
        user = dictfetchall(cursor)
        print(user)
        print(user_name)
        print(user_type)

        if user:
            if not user[0]['is_deleted']:
                if user_type == '8':
                    password = "dsdsfdsfsdf"
                else:
                    password = check_password(user_password, user[0]['password'])

                if password:
                    gen_access_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(60))
                    generate_otp = ''.join(random.choice(string.digits) for _ in range(6))
                    resp1 = 1
                    if user_type == '8':
                        opt_message =  "Dear User,\n\n" + generate_otp + " is your verification code to access your profile and bookings on Cotrav app, you need to verify your email first. \n\nRgrds,\nCoTrav."
                        fcm = FCM()
                        thread = Thread(target=fcm.send_message_to_moblies, args=(user_name, opt_message))
                        thread.start()
                        resp1 = 1
                    else:
                        add_otp = SignIn_OTP()
                        email_subject = "Cotrav - Verify Your Email"
                        email_body = "Dear User,<br><br>" + generate_otp + " is your verification code to access your profile and bookings on Cotrav app, you need to verify your email first. <br><br>Rgrds,<br>CoTrav."
                        thread = Thread(target=add_otp.send_email, args=(user_name, email_subject, email_body))
                        thread.start()
                        resp1 = 1

                    if resp1:
                        if user_type == '1':
                            insert_data = Corporate_Login_Access_Token.objects.create(corporate_login_id=user[0]['id'], access_token=gen_access_token,user_agent=user_info)
                        elif user_type == '2':
                            insert_data = Corporate_Approves_1_Login_Access_Token.objects.create(subgroup_authenticater_id=user[0]['id'], access_token=gen_access_token, user_agent=user_info)
                            print(insert_data)
                        elif user_type == '3':
                            insert_data = Corporate_Approves_2_Login_Access_Token.objects.create(group_authenticater_id=user[0]['id'], access_token=gen_access_token,user_agent=user_info)
                        elif user_type == '4':
                            insert_data = Corporate_Spoc_Login_Access_Token.objects.create(spoc_id=user[0]['id'],access_token=gen_access_token,user_agent=user_info)
                        elif user_type == '6':
                            insert_data = Corporate_Employee_Login_Access_Token.objects.create(employee_id=user[0]['id'], access_token=gen_access_token, user_agent=user_info)
                        elif user_type == '8':
                            insert_data = Operator_Driver_Access_Token.objects.create(driver_id=user[0]['id'], access_token=gen_access_token, user_agent=user_info)

                        elif user_type == '10':
                            insert_data = Corporate_Agent_Login_Access_Token.objects.create(agent_id=user[0]['id'], access_token=gen_access_token, user_agent=user_info)

                        data = {'success': 1,'access_token':gen_access_token, 'message': 'Login Successfully', 'User': user,'OTP':generate_otp}
                    else:
                        data = {'success': 0, 'message': 'OTP Not Send To Your Email Id Please Type Anothe Email'}
                else:
                    data = {'success': 0, 'message': 'Invalid User Name Or Password'}
            else:
                data = {'success': 0, 'message': 'Invalid User'}
        else:
            data = {'success': 0, 'message': 'Invalid User Name Or Password'}
    else:
        print("in else")
        data = {'success': 0, 'message': 'Please Enter Valid Inputs...'}
    return JsonResponse(data)


def logout(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    timezone.activate(pytz.timezone("Asia/Kolkata"))
                    user.expiry_date = timezone.localtime(timezone.now())  # change field
                    user.save()  # this will update only
                    data = {'success': 1, 'message': 'User Logout Successfully'}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def service_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllServiceType', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Types': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def railway_stations(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllRailwayStations', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Stations': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def bus_booking_portals(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllBusBookingPortals', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Portals': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def companies(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateDetails', [user.id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Corporates': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_company(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewCorporateDetails', [corporate_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllCorporateDocumnets', [corporate_id])
                    passanger = dictfetchall(cursor1)
                    company[0]['Documents'] = passanger
                    cursor1.close()

                    data = {'success': 1, 'Corporates': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_companies(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_name = request.POST.get('corporate_name', '')
        corporate_code = request.POST.get('corporate_code', '')
        contact_person_name = request.POST.get('contact_person_name', '')
        contact_person_no = request.POST.get('contact_person_no', '')
        contact_person_email = request.POST.get('contact_person_email', '')
        bill_corporate_name = request.POST.get('bill_corporate_name', '')
        address_line_1 = request.POST.get('address_line_1', '')
        address_line_2 = request.POST.get('address_line_2', '')
        address_line_3 = request.POST.get('address_line_3', '')
        billing_city_id = request.POST.get('billing_city_id', '')
        gst_id = request.POST.get('gst_id', '')

        has_billing_spoc_level = request.POST.get('has_billing_spoc_level', '')
        has_billing_admin_level = request.POST.get('has_billing_admin_level', '')
        has_auth_level = request.POST.get('has_auth_level', '')
        no_of_auth_level = request.POST.get('no_of_auth_level', '')
        has_assessment_codes = request.POST.get('has_assessment_codes', '')
        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        has_self_booking_access = request.POST.get('has_self_booking_access', '')
        will_do_realtime_payment = request.POST.get('will_do_realtime_payment', '')
        tds_on_management_fee_only = request.POST.get('tds_on_management_fee_only', '')
        is_spoc = request.POST.get('is_spoc', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')

        cotrav_agent_id = request.POST.get('cotrav_agent_id', '')
        user_type = request.POST.get('user_type', '')
        password = make_password(request.POST.get('password', ''))
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('create_corporate_with_basic_details',[corporate_name, corporate_code,contact_person_name,contact_person_no,contact_person_email,bill_corporate_name,address_line_1,
                      address_line_2,address_line_3,gst_id,has_billing_spoc_level,has_auth_level,no_of_auth_level,has_assessment_codes,is_radio,is_local,is_outstation, is_bus,
                       is_train, is_hotel, is_meal, is_flight,is_water_bottles,  is_reverse_logistics,is_spoc,password,cotrav_agent_id,user_type,
                    billing_city_id,has_self_booking_access,will_do_realtime_payment,has_billing_admin_level,is_send_email,is_send_sms,tds_on_management_fee_only])
                    company = dictfetchall(cursor)
                    print(company)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email, args=(contact_person_name, contact_person_email, "taxi123", "Admin"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(contact_person_name, contact_person_email, "taxi123", "Admin")
                        if is_spoc:
                            thread = Thread(target=add_user.new_user_send_email, args=(contact_person_name, contact_person_email, "taxi123", "Spoc"))
                            thread.start()
                            thread = Thread(target=add_user.new_user_send_email, args=(contact_person_name, contact_person_email, "taxi123", "Employee"))
                            thread.start()
                            #resp1 = add_user.new_user_send_email(contact_person_name, contact_person_email, "taxi123", "Spoc")
                            #resp1 = add_user.new_user_send_email(contact_person_name, contact_person_email, "taxi123", "Employee")

                        data = {'success': 1, 'message': "Corporate Added Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_company(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_name = request.POST.get('corporate_name', '')
        corporate_code = request.POST.get('corporate_code', '')
        contact_person_name = request.POST.get('contact_person_name', '')
        contact_person_no = request.POST.get('contact_person_no', '')
        contact_person_email = request.POST.get('contact_person_email', '')

        has_billing_spoc_level = request.POST.get('has_billing_spoc_level', '')
        has_billing_admin_level = request.POST.get('has_billing_admin_level', '')
        has_auth_level = request.POST.get('has_auth_level', '')
        no_of_auth_level = request.POST.get('no_of_auth_level', '')
        has_assessment_codes = request.POST.get('has_assessment_codes', '')
        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        has_self_booking_access = request.POST.get('has_self_booking_access', '')
        will_do_realtime_payment = request.POST.get('will_do_realtime_payment', '')
        tds_on_management_fee_only = request.POST.get('tds_on_management_fee_only', '')

        user_id = request.POST.get('user_id', '')
        corporate_id = request.POST.get('corporate_id', '')
        user_type = request.POST.get('user_type', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateCorporate',[corporate_name, corporate_code,contact_person_name,contact_person_no,contact_person_email,
                      has_billing_spoc_level,has_auth_level,no_of_auth_level,has_assessment_codes,is_radio,is_local, is_outstation, is_bus,
                       is_train, is_hotel, is_meal, is_flight,is_water_bottles,  is_reverse_logistics,corporate_id,user_id,user_type,
                        has_self_booking_access,will_do_realtime_payment,has_billing_admin_level,is_send_email,is_send_sms,tds_on_management_fee_only])
                    company = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_company(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        corporate_id = request.POST.get('corporate_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteCorporate',[corporate_id,user_id,user_type])
                    company = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_company_document(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        corporate_id = request.POST.get('corporate_id', '')
        user_id = request.POST.get('user_id', '')
        document_name = request.POST.get('document_name', '')
        document_desc = request.POST.get('document_desc', '')
        document = request.POST.get('document', '')
        
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addCorporateDocument',[corporate_id,user_id,user_type, document_name, document_desc, document])
                    company = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Document Added Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_company_document(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        document_id = request.POST.get('document_id', '')
        user_id = request.POST.get('user_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteCorporateDocument',[document_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Document Added Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_company_rates(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        package_name = request.POST.get('package_name', '')
        city_id = request.POST.get('city_id')
        taxi_type = request.POST.get('taxi_type', '')
        tour_type = request.POST.get('tour_type', '')
        kms = request.POST.get('kms', '')
        hours = request.POST.get('hours', '')
        km_rate = request.POST.get('km_rate', '')
        hour_rate = request.POST.get('hour_rate', '')
        base_rate = request.POST.get('base_rate', '')
        night_rate = request.POST.get('night_rate', '')
        night_start = request.POST.get('night_start', '')
        night_end = request.POST.get('night_end', '')

        rate_id = request.POST.get('rate_id')

        if rate_id:
            pass
        else:
            rate_id = 0
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addCorporateRate',[corporate_id,package_name,city_id,taxi_type,tour_type,kms,hours,km_rate,hour_rate,base_rate,
                                                        night_rate,user_id,user_type,rate_id,night_start,night_end])
                    company = dictfetchall(cursor)
                    print(company)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Rate Added Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_company_rates(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        package_name = request.POST.get('package_name', '')
        city_id = request.POST.get('city_id')
        taxi_type = request.POST.get('taxi_type', '')
        tour_type = request.POST.get('tour_type', '')
        kms = request.POST.get('kms', '')
        hours = request.POST.get('hours', '')
        km_rate = request.POST.get('km_rate', '')
        hour_rate = request.POST.get('hour_rate', '')
        base_rate = request.POST.get('base_rate', '')
        night_rate = request.POST.get('night_rate', '')
        night_start = request.POST.get('night_start', '')
        night_end = request.POST.get('night_end', '')

        rate_id = request.POST.get('rate_id')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateCorporateRate',[corporate_id,package_name,city_id,taxi_type,tour_type,kms,hours,km_rate,hour_rate,base_rate,
                                                        night_rate,user_id,user_type,rate_id,night_start,night_end])
                    company = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Rate Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_company_rates(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        rate_id = request.POST.get('rate_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteCorporateRate',[rate_id,user_id,user_type])
                    company = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Rate Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def company_rates(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateRatesDetails', [corporate_id, user.id, user_type])
                    corporate_rates = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Corporate_Retes': corporate_rates}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def billing_entities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateBillingEntitiesDetails', [corporate_id, user.id, user_type])
                    entity = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Entitys': entity}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_billing_entitie(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        entity_id = request.POST.get('entity_id', '')
        if entity_id:
            entity_id = entity_id
        else:
            entity_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewBillingEntitiesDetails', [entity_id])
                    entity = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Entitys': entity}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def corporate_management_fee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateManagementFeesDetails', [])
                    entity = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Fees': entity}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def service_fee_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllServiceFeesTypes', [])
                    entity = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Types': entity}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def admins(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateAdminsDetails', [corporate_id, user.id, user_type])
                    admin = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Admins': admin}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_admin(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        admin_id = request.POST.get('admin_id', '')
        if admin_id:
            admin_id = admin_id
        else:
            admin_id = '0'

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewAdminDetails', [admin_id])
                    admin = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Admins': admin}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def groups(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'
        user = {}

        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateGroupsDetails', [corporate_id, user.id, user_type])
                    group = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Groups': group}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def subgroups(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateSubgroupsDetails', [corporate_id,user.id,user_type])
                    subgroup = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Subgroups': subgroup}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def spocs(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateSpocsDetails', [corporate_id,user.id,user_type])
                    spoc = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Spocs': spoc}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def auth2_spocs(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        group_id = request.POST.get('group_id', '')
        if group_id:
            group_id = group_id
        else:
            group_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateGroupAuthSpocsDetails', [group_id])
                    spoc = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Spocs': spoc}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def auth1_spocs(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        group_id = request.POST.get('subgroup_id', '')
        if group_id:
            group_id = group_id
        else:
            group_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateSubGroupAuthSpocsDetails', [group_id])
                    spoc = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Spocs': spoc}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)

def employee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = 0

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateEmployeesDetails', [corporate_id,user.id,user_type])
                    employee = dictfetchall(cursor)
                    cursor.close()
                    for e in employee:
                        employee_id = e['id']
                        print("Employee ID")
                        print(employee_id)
                        cursor1 = connection.cursor()
                        cursor1.callproc('getEmployeePassportDetails', [employee_id])
                        passport = dictfetchall(cursor1)
                        cursor1.close()
                        e['PassportDetails'] = passport

                    data = {'success': 1, 'Employees': employee}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def spoc_employee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        spoc_id = request.POST.get('spoc_id', '')
        if spoc_id:
            spoc_id = spoc_id
        else:
            spoc_id = 0

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateSpocEmployeesDetails', [spoc_id])
                    employee = dictfetchall(cursor)
                    cursor.close()

                    for e in employee:
                        print(e)
                        employee_id = e['id']

                        print(employee_id)
                        cursor1 = connection.cursor()
                        cursor1.callproc('getEmployeePassportDetails', [employee_id])
                        passport = dictfetchall(cursor1)
                        cursor1.close()
                        e['PassportDetails'] = passport


                    data = {'success': 1, 'Employees': employee}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def corporate_package(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        city_id = request.POST.get('city_id', '')
        taxi_type = request.POST.get('taxi_type', '')
        tour_type = request.POST.get('tour_type', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getCorporatePackage', [corporate_id,city_id,taxi_type,tour_type])
                    employee = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Package': employee}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_assessment_code(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllAssessmentCodes', [corporate_id])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'AssCodes': cities}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_assessment_city(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllAssessmentCity', [corporate_id])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'AssCity': cities}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def city_by_package(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'
            
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getCityByPackageCity', [corporate_id])
                    cities = dictfetchall(cursor)
                    print(cities)
                    cursor.close()
                    data = {'success': 1, 'Cities': cities}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def cities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCity', [])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Cities': cities}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def taxi_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllTaxiTypes', [])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'taxi_types': cities}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def train_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllTrainTypes', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Types': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def bus_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllBusTypes', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Types': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def irctc_accounts(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllIrctcAccounts', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Accounts': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def hotel_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllHotelTypes', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Types': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_airports(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllAirports', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Airports': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)
    

def hotel_booking_portals(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllHotelBookingPortals', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Portals': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_hotel_portal(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        hotel_id = request.POST.get('hotel_id', '')
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewHotelBookingPortals', [hotel_id])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Portals': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_hotel_portal(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        hotel_name = request.POST.get('hotel_name', '')
        hotel_email = request.POST.get('hotel_email', '')
        hotel_contact = request.POST.get('hotel_contact', '')
        website = request.POST.get('website', '')

        print(hotel_email)

        hotel_address = request.POST.get('hotel_address', '')
        contact_name = request.POST.get('contact_name', '')
        contact_email = request.POST.get('contact_email', '')
        contact_no = request.POST.get('contact_no', '')

        beneficiary_name = request.POST.get('beneficiary_name', '')
        beneficiary_account_no = request.POST.get('beneficiary_account_no', '')
        bank_name = request.POST.get('bank_name', '')
        ifsc_code = request.POST.get('ifsc_code', '')

        is_service_tax_applicable = request.POST.get('is_service_tax_applicable', '')
        tds_rate = request.POST.get('tds_rate', '')
        gst_id = request.POST.get('gst_id', '')
        pan_no = request.POST.get('pan_no', '')

        if tds_rate:
            tds_rate = tds_rate
        else:
            tds_rate = 0

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addHotelPortal', [hotel_name,hotel_email,hotel_contact,website,hotel_address,contact_name,contact_email,contact_no,beneficiary_name,beneficiary_account_no,
                                                    ifsc_code,is_service_tax_applicable,tds_rate,gst_id,pan_no,user_id,user_type,bank_name])
                    emp = dictfetchall(cursor)
                    print(emp)
                    data = {'success': 1, 'message': "Hotel Added Successfully", 'id':emp}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_hotel_portal(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        hotel_name = request.POST.get('hotel_name', '')
        hotel_email = request.POST.get('hotel_email', '')
        hotel_contact = request.POST.get('hotel_contact', '')
        website = request.POST.get('website', '')

        is_service_tax_applicable = request.POST.get('is_service_tax_applicable', '')
        tds_rate = request.POST.get('tds_rate', '')
        gst_id = request.POST.get('gst_id', '')
        pan_no = request.POST.get('pan_no', '')
        portal_vendor_id = request.POST.get('portal_vendor_id', '')
        hotel_id = request.POST.get('hotel_id', '')


        if tds_rate:
            tds_rate = tds_rate
        else:
            tds_rate = 0

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateHotelPortal', [hotel_name,hotel_email,hotel_contact,website,is_service_tax_applicable,tds_rate,gst_id,pan_no,user_id,user_type,hotel_id,portal_vendor_id])
                    emp = dictfetchall(cursor)
                    print(emp)
                    data = {'success': 1, 'message': "Hotel Added Successfully", 'id':emp}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def room_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllRoomTypes', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Types': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_corporate_management_fee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        service_fees_type_id = request.POST.get('service_fees_type_id', '')
        service_fees_type_value = request.POST.get('service_fees_type_value', '')
        service_fees_type = request.POST.get('service_fees_type', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addCorporateManagementFees', [corporate_id,service_fees_type_id,service_fees_type_value,service_fees_type,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': 'Management Fee Added Successfully'}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_corporate_management_fee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        service_fees_type_id = request.POST.get('service_fees_type_id', '')
        service_fees_type_value = request.POST.get('service_fees_type_value', '')
        service_fees_type = request.POST.get('service_fees_type', '')
        fees_id = request.POST.get('fees_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateCorporateManagementFees', [corporate_id,service_fees_type_id,service_fees_type_value,service_fees_type,fees_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Management Fee Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_corporate_management_fee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        fees_id = request.POST.get('fees_id', '')
        user_id = request.POST.get('user_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteCorporateManagementFees', [fees_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Management Fee Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_taxi_type(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')
        type_name = request.POST.get('type_name', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addTaxiTypes', [type_name,user_id,user_type])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company,'id':company}
                    else:
                        data = {'success': 1, 'message': "Taxi Type Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_taxi_type(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        type_name = request.POST.get('type_name', '')
        taxitype_id = request.POST.get('taxitype_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateTaxiTypes', [type_name,taxitype_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Taxi Type Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_taxi_type(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        taxitype_id = request.POST.get('taxitype_id', '')
        user_id = request.POST.get('user_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteTaxiTypes', [taxitype_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Taxi Type Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_taxi_model(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        brand_name = request.POST.get('brand_name', '')
        model_name = request.POST.get('model_name', '')
        taxi_type_id = request.POST.get('taxitype_id', '')
        no_of_seats = request.POST.get('no_of_seats', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addTaxiModel', [brand_name,model_name,taxi_type_id,no_of_seats,user_id,user_type])
                    cities = dictfetchall(cursor)
                    print(cities)
                    data = {'success': 1, 'message': "Taxi Model Added Successfully", 'id' : cities}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_taxi_model(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        brand_name = request.POST.get('brand_name', '')
        model_name = request.POST.get('model_name', '')
        taxi_type_id = request.POST.get('taxitype_id', '')
        no_of_seats = request.POST.get('no_of_seats', '')
        model_id = request.POST.get('model_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateTaxiModel', [brand_name,model_name,taxi_type_id,no_of_seats,model_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Taxi Model Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_taxi_model(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        model_id = request.POST.get('model_id', '')
        user_id = request.POST.get('user_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteTaxiModel', [model_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Taxi Model Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def taxis(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllTaxis', [])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Taxis': cities}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_taxi(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        model_id = request.POST.get('model_id', '')
        taxi_reg_no = request.POST.get('taxi_reg_no', '')
        make_year = request.POST.get('make_year', '')
        garage_location = request.POST.get('garage_location', '')
        garage_distance = request.POST.get('garage_distance', '')

        if garage_distance:
            garage_distance = float(garage_distance)
        else:
            garage_distance = 0

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addTaxi', [model_id,taxi_reg_no,make_year,garage_location,garage_distance,user_id,user_type])
                    cities = dictfetchall(cursor)
                    print(cities)
                    data = {'success': 1, 'message': "Taxi Added Successfully",'id':cities}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_taxi(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        model_id = request.POST.get('model_id', '')
        taxi_reg_no = request.POST.get('taxi_reg_no', '')
        make_year = request.POST.get('make_year', '')
        garage_location = request.POST.get('garage_location', '')
        garage_distance = request.POST.get('garage_distance', '')

        if garage_distance:
            garage_distance = float(garage_distance)
        else:
            garage_distance = 0

        taxi_id = request.POST.get('taxi_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateTaxi', [model_id,taxi_reg_no,make_year,garage_location,garage_distance,taxi_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    company = dictfetchall(cursor)
                    cursor.close()
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Taxi Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_taxi(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        taxi_id = request.POST.get('taxi_id', '')
        user_id = request.POST.get('user_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteTaxi', [taxi_id,user_id,user_type])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Taxi Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def taxi_models(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllTaxiModels', [])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Models': cities}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_billing_entity(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')
        entity_name = request.POST.get('entity_name', '')
        billing_city_id = request.POST.get('billing_city_id')
        contact_person_name = request.POST.get('contact_person_name', '')
        contact_person_email = request.POST.get('contact_person_email', '')
        contact_person_no = request.POST.get('contact_person_no', '')
        address_line_1 = request.POST.get('address_line_1', '')
        address_line_2 = request.POST.get('address_line_2', '')
        address_line_3 = request.POST.get('address_line_3', '')
        gst_id = request.POST.get('gst_id', '')
        pan_no = request.POST.get('pan_no', '')

        entity_id = request.POST.get('entity_id')
        is_delete = request.POST.get('is_delete')

        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        if entity_id:
            entity_id = entity_id
        else:
            entity_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCorporateBillingEntity', [user_id,corporate_id,user_type,entity_name,billing_city_id,contact_person_name,
                                                                        contact_person_email,contact_person_no,address_line_1,address_line_2,address_line_3,
                                                                        gst_id,pan_no,entity_id,is_delete])
                    result = dictfetchall(cursor)
                    cursor.close()

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Billing Entity Added Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_billing_entity(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')
        entity_name = request.POST.get('entity_name', '')
        billing_city_id = request.POST.get('billing_city_id')
        contact_person_name = request.POST.get('contact_person_name', '')
        contact_person_email = request.POST.get('contact_person_email', '')
        contact_person_no = request.POST.get('contact_person_no', '')
        address_line_1 = request.POST.get('address_line_1', '')
        address_line_2 = request.POST.get('address_line_2', '')
        address_line_3 = request.POST.get('address_line_3', '')
        gst_id = request.POST.get('gst_id', '')
        pan_no = request.POST.get('pan_no', '')

        entity_id = request.POST.get('entity_id')

        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        if entity_id:
            entity_id = entity_id
        else:
            entity_id = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateCorporateBillingEntity', [user_id,corporate_id,user_type,entity_name,billing_city_id,contact_person_name,
                                                                        contact_person_email,contact_person_no,address_line_1,address_line_2,address_line_3,
                                                                        gst_id,pan_no,entity_id])
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Billing Entity Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_billing_entity(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        entity_id = request.POST.get('entity_id')
        is_delete = request.POST.get('is_delete')

        if entity_id:
            entity_id = entity_id
        else:
            entity_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCorporateBillingEntity',
                                    [user_id, user_type, entity_id])
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Billing Entity Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_cotrav_billing_entity(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        entity_name = request.POST.get('entity_name', '')
        billing_city_id = request.POST.get('billing_city_id')
        contact_person_name = request.POST.get('contact_person_name', '')
        contact_person_email = request.POST.get('contact_person_email', '')
        contact_person_no = request.POST.get('contact_person_no', '')
        address_line_1 = request.POST.get('address_line_1', '')
        address_line_2 = request.POST.get('address_line_2', '')
        address_line_3 = request.POST.get('address_line_3', '')
        gst_id = request.POST.get('gst_id', '')
        pan_no = request.POST.get('pan_no', '')

        entity_id = request.POST.get('entity_id')
        is_delete = request.POST.get('is_delete')

        if entity_id:
            entity_id = entity_id
        else:
            entity_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCotravBillingEntity', [user_id,user_type,entity_name,billing_city_id,contact_person_name,
                                                                        contact_person_email,contact_person_no,address_line_1,address_line_2,address_line_3,
                                                                        gst_id,pan_no,entity_id,is_delete])
                    result = dictfetchall(cursor)
                    print(result)
                    cursor.close()

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Billing Entity Added Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_cotrav_billing_entity(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')
        entity_name = request.POST.get('entity_name', '')
        billing_city_id = request.POST.get('billing_city_id')
        contact_person_name = request.POST.get('contact_person_name', '')
        contact_person_email = request.POST.get('contact_person_email', '')
        contact_person_no = request.POST.get('contact_person_no', '')
        address_line_1 = request.POST.get('address_line_1', '')
        address_line_2 = request.POST.get('address_line_2', '')
        address_line_3 = request.POST.get('address_line_3', '')
        gst_id = request.POST.get('gst_id', '')
        pan_no = request.POST.get('pan_no', '')

        entity_id = request.POST.get('entity_id')

        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        if entity_id:
            entity_id = entity_id
        else:
            entity_id = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateCotravBillingEntity', [user_id,user_type,entity_name,billing_city_id,contact_person_name,
                                                                        contact_person_email,contact_person_no,address_line_1,address_line_2,address_line_3,
                                                                        gst_id,pan_no,entity_id])
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Billing Entity Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_cotrav_billing_entity(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        entity_id = request.POST.get('entity_id')
        is_delete = request.POST.get('is_delete')
        print("enitititi id")
        print(entity_id)
        if entity_id:
            entity_id = entity_id
        else:
            entity_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCotravBillingEntity',[user_id, user_type, entity_id])
                    cursor.close()
                    company = dictfetchall(cursor)
                    print(company)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Billing Entity Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_group(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')
        group_name = request.POST.get('group_name', '')
        zone_name = request.POST.get('zone_name')

        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        cid = request.POST.get('cid', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        is_visa = request.POST.get('is_visa', '')
        is_frro = request.POST.get('is_frro', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        access_token = request.POST.get('access_token_auth', '')
        password = make_password(request.POST.get('password', ''))

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCorporateGroup', [user_id,corporate_id,user_type,group_name,zone_name,name,email,cid,contact_no,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,
                                                             is_water_bottles,is_reverse_logistics,access_token,password,is_send_email,is_send_sms,is_visa,is_frro,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        #resp1 = add_user.new_user_send_email(name, email, "taxi123", "Approver 2")
                        thread = Thread(target=add_user.new_user_send_email, args=(name, email, "taxi123", "Approver 2"))
                        thread.start()
                        data = {'success': 1, 'message': "Company Group Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_group(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        group_id = request.POST.get('group_id', '')

        user_id = request.POST.get('user_id', '')
        group_name = request.POST.get('group_name', '')
        zone_name = request.POST.get('zone_name')

        if group_id:
            group_id = group_id
        else:
            group_id = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateGroupDetails', [group_id,group_name,zone_name,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company Group Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_group(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        group_id = request.POST.get('group_id', '')
        user_id = request.POST.get('user_id', '')

        if group_id:
            group_id = group_id
        else:
            group_id = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteGroupDetails', [group_id,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company Group Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_subgroup(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        print("dsasdasdasd")
        user_id = request.POST.get('user_id', '')
        subgroup_name = request.POST.get('subgroup_name', '')
        group_id = request.POST.get('group_id', '')

        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        cid = request.POST.get('cid', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        is_visa = request.POST.get('is_visa', '')
        is_frro = request.POST.get('is_frro', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        access_token = request.POST.get('access_token_auth', '')
        password = make_password(request.POST.get('password', ''))
        print(password)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCorporateSubGroup', [user_id,corporate_id,user_type,subgroup_name,group_id,name,email,cid,contact_no,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,
                    is_water_bottles,is_reverse_logistics,access_token,password,is_send_email,is_send_sms,is_visa,is_frro,is_guesthouse])
                    print(subgroup_name)
                    company = dictfetchall(cursor)
                    print(company)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email, args=(name, email, "taxi123", "Approver 1"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(name, email, "taxi123", "Approver 1")
                        data = {'success': 1, 'message': "Subgroup Insert Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    print("Exception")
                    data = {'success': 0, 'message': "Error in Data Insert"+e}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_subgroup(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')
        user_id = request.POST.get('user_id', '')
        subgroup_name = request.POST.get('group_name', '')

        if subgroup_id:
            subgroup_id = subgroup_id
        else:
            subgroup_id = '0'

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateSubGroupDetails', [subgroup_id,subgroup_name,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company SubGroup Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_subgroup(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        subgroup_id = request.POST.get('subgroup_id', '')
        user_id = request.POST.get('user_id', '')

        if subgroup_id:
            subgroup_id = subgroup_id
        else:
            subgroup_id = '0'

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteSubGroupDetails', [subgroup_id,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company SubGroup Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_group_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')

        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        cid = request.POST.get('cid', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')

        group_id = request.POST.get('group_id')

        is_delete = request.POST.get('delete_id')
        access_token = request.POST.get('access_token_auth', '')
        password = make_password(request.POST.get('password', ''))
        group_auth_id = request.POST.get('group_auth_id', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        if group_id:
            group_id = group_id
        else:
            group_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCorporateGroupAuthenticator', [user_id,corporate_id,user_type,name,email,cid,contact_no,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,
                    is_water_bottles,is_reverse_logistics,group_id,is_delete,access_token,password,group_auth_id,is_send_email,is_send_sms,is_frro,is_visa,is_guesthouse])

                    company = dictfetchall(cursor)

                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email, args=(name, email, "taxi123", "Approver 2"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(name, email, "taxi123", "Approver 2")
                        data = {'success': 1, 'message': "Company Group Authenticator Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_group_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        user_id = request.POST.get('user_id', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        cid = request.POST.get('cid', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        group_auth_id = request.POST.get('group_auth_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateCorporateGroupAuthenticator', [user_id,corporate_id,user_type,name,email,cid,contact_no,is_radio,is_local,
                        is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,is_water_bottles,is_reverse_logistics,group_auth_id,is_send_email,
                        is_send_sms,is_frro,is_visa,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company Group Authenticator Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_group_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        group_auth_id = request.POST.get('group_auth_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteGroupAuthenticator', [group_auth_id,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company Group Authenticator Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_subgroup_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')

        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        cid = request.POST.get('cid', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')

        subgroup_id = request.POST.get('subgroup_id')

        is_delete = request.POST.get('delete_id')
        access_token = request.POST.get('access_token_auth', '')
        password = make_password(request.POST.get('password', ''))
        subgroup_auth_id = request.POST.get('subgroup_auth_id', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        if subgroup_id:
            subgroup_id = subgroup_id
        else:
            subgroup_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCorporateSubGroupAuthenticator', [user_id,corporate_id,user_type,name,email,cid,contact_no,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,
                    is_water_bottles,is_reverse_logistics,subgroup_id,is_delete,access_token,password,subgroup_auth_id,is_send_email,is_send_sms,is_frro,is_visa,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email, args=(name, email, "taxi123", "Approver 1"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(name, email, "taxi123", "Approver 1")
                        data = {'success': 1, 'message': "Company SubGroup Authenticator Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_subgroup_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        user_id = request.POST.get('user_id', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        cid = request.POST.get('cid', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        subgroup_auth_id = request.POST.get('subgroup_auth_id', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateCorporateSubGroupAuthenticator', [user_id,corporate_id,user_type,name,email,cid,contact_no,is_radio,is_local,
                        is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,is_water_bottles,is_reverse_logistics,subgroup_auth_id,is_send_email,
                                                                             is_send_sms,is_frro,is_visa,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company SubGroup Authenticator Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_subgroup_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        subgroup_auth_id = request.POST.get('subgroup_auth_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteSubGroupAuthenticator', [subgroup_auth_id,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Company SubGroup Authenticator Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_admin(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')

        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')

        is_delete = request.POST.get('delete_id')
        access_token = request.POST.get('access_token_auth', '')
        password = make_password(request.POST.get('password', ''))
        admin_id = request.POST.get('admin_id', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        has_billing_access = request.POST.get('has_billing_access', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '0'

        if admin_id:
            admin_id = admin_id
        else:
            admin_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCorporateAdmin', [user_id,corporate_id,user_type,name,email,contact_no,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,
                    is_water_bottles,is_reverse_logistics,is_delete,access_token,password,admin_id,is_send_email,is_send_sms,has_billing_access,is_frro,is_visa,is_guesthouse])
                    company = dictfetchall(cursor)
                    
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email(name, email, "taxi123", "Admin"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(name, email, "taxi123", "Admin")

                        data = {'success': 1, 'message': "Corporate Admin Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_admin(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        user_id = request.POST.get('user_id', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        contact_no = request.POST.get('contact_no', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')

        admin_id = request.POST.get('admin_id', '')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        has_billing_access = request.POST.get('has_billing_access', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateCorporateAdmin', [user_id,corporate_id,user_type,name,email,contact_no,is_radio,is_local,
                        is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,is_water_bottles,is_reverse_logistics,admin_id,is_send_email,
                        is_send_sms,has_billing_access,is_frro,is_visa,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Admin Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_admin(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        admin_id = request.POST.get('admin_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCorporateAdmin', [admin_id,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Admin Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_spoc(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')

        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')
        user_cid = request.POST.get('user_cid', '')

        user_name = request.POST.get('user_name', '')
        user_contact = request.POST.get('user_contact', '')
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')
        budget = request.POST.get('budget')
        expense = request.POST.get('expense')

        is_radio = request.POST.get('is_radio')
        is_local = request.POST.get('is_local')
        is_outstation = request.POST.get('is_outstation')
        is_bus = request.POST.get('is_bus')
        is_train = request.POST.get('is_train')
        is_hotel = request.POST.get('is_hotel')
        is_meal = request.POST.get('is_meal')
        is_flight = request.POST.get('is_flight')
        is_water_bottles = request.POST.get('is_water_bottles')
        is_reverse_logistics = request.POST.get('is_reverse_logistics')

        is_delete = request.POST.get('delete_id')
        access_token = request.POST.get('access_token_auth', '')
        password = make_password(request.POST.get('password', ''))
        spoc_id = request.POST.get('spoc_id')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = 0

        if budget:
            budget = budget
        else:
            budget = 0

        if expense:
            expense = expense
        else:
            expense = 0

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = 0
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('addNewCorporateSpoc', [user_id,corporate_id,user_type,group_id,subgroup_id,user_cid,user_name,user_contact,email,username,
                     budget,expense,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,
                     is_water_bottles,is_reverse_logistics,is_delete,access_token,password,spoc_id,is_send_email,is_send_sms,is_frro,is_visa,is_guesthouse])
                    company = dictfetchall(cursor)
                    print(company)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email, args=(user_name, email, "taxi123", "Spoc"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(user_name, email, "taxi123", "Spoc")
                        data = {'success': 1, 'message': "Corporate Spoc Added Successfully"}
                    cursor.close()

                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_spoc(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        user_id = request.POST.get('user_id', '')

        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')
        user_cid = request.POST.get('user_cid', '')

        user_name = request.POST.get('user_name', '')
        user_contact = request.POST.get('user_contact', '')
        email = request.POST.get('email', '')
        username = request.POST.get('username', '')
        budget = request.POST.get('budget', '')
        expense = request.POST.get('expense', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')

        is_delete = request.POST.get('delete_id')
        access_token = request.POST.get('access_token_auth', '')
        spoc_id = request.POST.get('spoc_id')
        is_send_email = request.POST.get('is_send_email', '')
        is_send_sms = request.POST.get('is_send_sms', '')
        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateCorporateSpoc', [user_id,corporate_id,user_type,group_id,subgroup_id,user_cid,user_name,user_contact,email,username,
                       budget,expense,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,is_meal,is_flight,
                       is_water_bottles,is_reverse_logistics,is_delete,spoc_id,is_send_email,is_send_sms,is_frro,is_visa,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Spoc Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_spoc(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        spoc_id = request.POST.get('spoc_id', '')
        delete_id = request.POST.get('delete_id', '')
        print(spoc_id)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCorporateSpoc', [spoc_id,user_id,user_type,delete_id])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Spoc Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def active_spoc(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        spoc_id = request.POST.get('spoc_id', '')
        print("spoc id")
        print(spoc_id)
        print(user_id)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('activeCorporateSpoc', [spoc_id,user_id,user_type])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Spoc Active Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_employee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        user_id = request.POST.get('user_id', '')

        spoc_id = request.POST.get('spoc_id')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        core_employee_id = request.POST.get('core_employee_id', '')
        employee_cid = request.POST.get('employee_cid', '')

        employee_name = request.POST.get('employee_name', '')
        employee_email = request.POST.get('employee_email', '')
        employee_contact = request.POST.get('employee_contact', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender')
        id_proof_type = request.POST.get('id_proof_type')

        id_proof_no = request.POST.get('id_proof_no', '')
        is_active = request.POST.get('is_active', '')
        has_dummy_email = 0
        fcm_regid = request.POST.get('fcm_regid', '')
        is_cxo = request.POST.get('is_cxo', '')
        designation = request.POST.get('designation', '')
        home_city = request.POST.get('home_city', '')
        home_address = request.POST.get('home_address', '')
        reporting_manager = request.POST.get('reporting_manager', '')
        employee_band = request.POST.get('employee_band', '')

        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        passport_issue_date = request.POST.get('passport_issue_date', '')
        passport_no = request.POST.get('passport_no', '')
        passport_expiry_date = request.POST.get('passport_expiry_date', '')
        visa_number = request.POST.get('visa_number', '')
        visa_expiry_date = request.POST.get('visa_expiry_date', '')
        current_location = request.POST.get('current_location', '')
        current_stay_address = request.POST.get('current_stay_address', '')
        company_contract_expiry_date = request.POST.get('company_contract_expiry_date', '')
        lease_status = request.POST.get('lease_status', '')
        
        assistant_id = request.POST.get('assistant_id', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, '%d-%m-%Y')
        else:
            date_of_birth = None

        if passport_issue_date and passport_issue_date != 'None':
            passport_issue_date = datetime.strptime(passport_issue_date, '%d-%m-%Y')
        else:
            passport_issue_date = None

        if passport_expiry_date and passport_expiry_date != 'None':
            passport_expiry_date = datetime.strptime(passport_expiry_date, '%d-%m-%Y')
        else:
            passport_expiry_date = None

        if visa_expiry_date and visa_expiry_date != 'None':
            visa_expiry_date = datetime.strptime(visa_expiry_date, '%d-%m-%Y')
        else:
            visa_expiry_date = None

        if company_contract_expiry_date and company_contract_expiry_date != 'None':
            company_contract_expiry_date = datetime.strptime(company_contract_expiry_date, '%d-%m-%Y')
        else:
            company_contract_expiry_date = None

        is_delete = request.POST.get('delete_id')
        password = make_password(request.POST.get('password', ''))
        employee_id = request.POST.get('employee_id')
        username = request.POST.get('username')

        if employee_id:
            employee_id = employee_id
        else:
            employee_id = '0'

        if is_delete:
            is_delete = is_delete
        else:
            is_delete = '0'

        if assistant_id:
            assistant_id = assistant_id
        else:
            assistant_id = 0
        
        if reporting_manager:
            reporting_manager = reporting_manager
        else:
            reporting_manager = 0

        if age:
            pass
        else:
            age = 0
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    result = cursor.callproc('addNewCorporateEmployee', [user_id,user_type,spoc_id, core_employee_id, employee_cid,
                    employee_name, employee_email, employee_contact, age, gender, id_proof_type, id_proof_no, is_active, has_dummy_email,
                    fcm_regid, is_cxo, designation, home_city, home_address, assistant_id, date_of_birth,is_delete,employee_id,
                    billing_entity_id,corporate_id,password,username,reporting_manager,employee_band,is_frro,is_visa,passport_issue_date,passport_no,
                    passport_expiry_date,visa_number,visa_expiry_date,current_location, current_stay_address,company_contract_expiry_date,lease_status])

                    company = dictfetchall(cursor)
                    print(company)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email, args=(employee_name, employee_email, "taxi123", "Employee"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(employee_name, employee_email, "taxi123", "Employee")
                        data = {'success': 1, 'message': "Corporate Employee Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_employee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        user_id = request.POST.get('user_id', '')

        spoc_id = request.POST.get('spoc_id')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        core_employee_id = request.POST.get('core_employee_id', '')
        employee_cid = request.POST.get('employee_cid', '')

        employee_name = request.POST.get('employee_name', '')
        employee_email = request.POST.get('employee_email', '')
        employee_contact = request.POST.get('employee_contact', '')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        id_proof_type = request.POST.get('id_proof_type')

        id_proof_no = request.POST.get('id_proof_no', '')
        is_active = request.POST.get('is_active')
        has_dummy_email = 0
        fcm_regid = request.POST.get('fcm_regid')
        is_cxo = request.POST.get('is_cxo')
        designation = request.POST.get('designation', '')
        home_city = request.POST.get('home_city', '')
        home_address = request.POST.get('home_address', '')
        assistant_id = request.POST.get('assistant_id', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        reporting_manager = request.POST.get('reporting_manager', '')
        employee_band = request.POST.get('employee_band', '')

        is_frro = request.POST.get('is_frro', '')
        is_visa = request.POST.get('is_visa', '')
        passport_issue_date = request.POST.get('passport_issue_date', '')
        passport_no = request.POST.get('passport_no', '')
        passport_expiry_date = request.POST.get('passport_expiry_date', '')
        visa_number = request.POST.get('visa_number', '')
        visa_expiry_date = request.POST.get('visa_expiry_date', '')
        current_location = request.POST.get('current_location', '')
        current_stay_address = request.POST.get('current_stay_address', '')
        company_contract_expiry_date = request.POST.get('company_contract_expiry_date', '')
        lease_status = request.POST.get('lease_status', '')

        if date_of_birth and date_of_birth != 'None':
            date_of_birth = datetime.strptime(date_of_birth, '%d-%m-%Y')
        else:
            date_of_birth = None
            
        if passport_issue_date and passport_issue_date != 'None':
            passport_issue_date = datetime.strptime(passport_issue_date, '%d-%m-%Y')
        else:
            passport_issue_date = None

        if passport_expiry_date and passport_expiry_date != 'None':
            passport_expiry_date = datetime.strptime(passport_expiry_date, '%d-%m-%Y')
        else:
            passport_expiry_date = None
            
        if visa_expiry_date and visa_expiry_date != 'None':
            visa_expiry_date = datetime.strptime(visa_expiry_date, '%d-%m-%Y')
        else:
            visa_expiry_date = None
            
        if company_contract_expiry_date and company_contract_expiry_date != 'None':
            company_contract_expiry_date = datetime.strptime(company_contract_expiry_date, '%d-%m-%Y')
        else:
            company_contract_expiry_date = None

        if is_cxo == '0':
            assistant_id = 0

        employee_id = request.POST.get('employee_id')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    result = cursor.callproc('updateEmployeeDetails', [user_id,user_type,spoc_id, core_employee_id, employee_cid,
                    employee_name, employee_email, employee_contact, age, gender, id_proof_type, id_proof_no, is_active, has_dummy_email,
                    fcm_regid, is_cxo, designation, home_city, home_address, assistant_id, date_of_birth,employee_id,billing_entity_id,reporting_manager,
                    employee_band,is_frro,is_visa,passport_issue_date,passport_no,
                    passport_expiry_date,visa_number,visa_expiry_date,current_location, current_stay_address,company_contract_expiry_date,lease_status])
                    print(result)
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Employee Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_employee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        employee_id = request.POST.get('employee_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCorporateEmployee', [employee_id,user_id,user_type])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Employee Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_agent(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        emp_id = request.POST.get('emp_id', '')
        username = request.POST.get('username', '')
        contact_no = request.POST.get('contact_no', '')
        email = request.POST.get('email', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        is_visa = request.POST.get('is_visa', '')
        is_frro = request.POST.get('is_frro', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        has_billing_access = request.POST.get('has_billing_access', '')
        has_voucher_payment_access = request.POST.get('has_voucher_payment_access', '')
        has_voucher_approval_access = request.POST.get('has_voucher_approval_access', '')
        is_super_admin = request.POST.get('is_super_admin', '')
        is_relationship_manager = request.POST.get('is_relationship_manager', '')
        is_operation_manager = request.POST.get('is_operation_manager', '')

        password = make_password(request.POST.get('password', ''))
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    result = cursor.callproc('addAgent', [emp_id, username, contact_no,email,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,
                    is_meal,is_flight,is_water_bottles,is_reverse_logistics,has_billing_access,has_voucher_payment_access,has_voucher_approval_access,
                    is_super_admin,password,user_id,user_type,is_relationship_manager,is_operation_manager,is_visa,is_frro,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        add_user = newUserAdd_Email()
                        thread = Thread(target=add_user.new_user_send_email, args=(username, email, "taxi123", "Agent"))
                        thread.start()
                        #resp1 = add_user.new_user_send_email(username, email, "taxi123", "Agent")
                        data = {'success': 1, 'message': "Agent Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_agent(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        emp_id = request.POST.get('emp_id', '')
        username = request.POST.get('username', '')
        contact_no = request.POST.get('contact_no', '')
        email = request.POST.get('email', '')

        is_radio = request.POST.get('is_radio', '')
        is_local = request.POST.get('is_local', '')
        is_outstation = request.POST.get('is_outstation', '')
        is_bus = request.POST.get('is_bus', '')
        is_train = request.POST.get('is_train', '')
        is_hotel = request.POST.get('is_hotel', '')
        is_meal = request.POST.get('is_meal', '')
        is_flight = request.POST.get('is_flight', '')
        is_water_bottles = request.POST.get('is_water_bottles', '')
        is_reverse_logistics = request.POST.get('is_reverse_logistics', '')
        is_visa = request.POST.get('is_visa', '')
        is_frro = request.POST.get('is_frro', '')
        is_guesthouse = request.POST.get('is_guesthouse', '')

        has_billing_access = request.POST.get('has_billing_access', '')
        has_voucher_payment_access = request.POST.get('has_voucher_payment_access', '')
        has_voucher_approval_access = request.POST.get('has_voucher_approval_access', '')
        is_super_admin = request.POST.get('is_super_admin', '')
        is_relationship_manager = request.POST.get('is_relationship_manager', '')
        is_operation_manager = request.POST.get('is_operation_manager', '')

        agent_id = request.POST.get('agent_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    result = cursor.callproc('updateAgent', [emp_id, username, contact_no,email,is_radio,is_local,is_outstation,is_bus,is_train,is_hotel,
                                                          is_meal,is_flight,is_water_bottles,is_reverse_logistics,has_billing_access,
                                                          has_voucher_payment_access,has_voucher_approval_access,is_super_admin,user_id,
                                                          user_type,agent_id,is_relationship_manager,is_operation_manager,is_visa,is_frro,is_guesthouse])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Agent Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_agent(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        agent_id = request.POST.get('agent_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteAgent', [user_id,user_type,agent_id])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Agent Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def activate_agent(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        agent_id = request.POST.get('agent_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('activateAgent', [user_id,user_type,agent_id])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Agent Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)

def view_group(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        group_id = request.POST.get('group_id', '')

        if group_id:
            group_id = group_id
        else:
            group_id = '0'
        user = {}

        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewGroupDetails', [group_id])
                    group = dictfetchall(cursor)
                    data = {'success': 1, 'Groups': group}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_group_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        group_id = request.POST.get('group_id', '')

        if group_id:
            group_id = group_id
        else:
            group_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateGroupsAuthenticator', [group_id])
                    group = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Groups': group}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_subgroup(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        subgroup_id = request.POST.get('subgroup_id', '')

        if subgroup_id:
            subgroup_id = subgroup_id
        else:
            subgroup_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewSubGroupDetails', [subgroup_id])
                    group = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'SubGroups': group}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_subgroup_auth(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        subgroup_id = request.POST.get('subgroup_id', '')

        if subgroup_id:
            subgroup_id = subgroup_id
        else:
            subgroup_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateSubGroupsAuthenticator', [subgroup_id])
                    group = dictfetchall(cursor)
                    data = {'success': 1, 'SubGroups': group}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_auth_1(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        auth_id = request.POST.get('auth_id', '')

        if auth_id:
            auth_id = auth_id
        else:
            auth_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewSubGroupsAuthenticator', [auth_id])
                    group = dictfetchall(cursor)
                    data = {'success': 1, 'Authenticator': group}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_auth_2(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        auth_id = request.POST.get('auth_id', '')

        if auth_id:
            auth_id = auth_id
        else:
            auth_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewGroupsAuthenticator', [auth_id])
                    group = dictfetchall(cursor)
                    data = {'success': 1, 'Authenticator': group}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)
    

def view_spoc(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        spoc_id = request.POST.get('spoc_id', '')

        if spoc_id:
            spoc_id = spoc_id
        else:
            spoc_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewSpocDetails', [spoc_id])
                    spoc = dictfetchall(cursor)
                    data = {'success': 1, 'Spoc': spoc}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_employee(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        employee_id = request.POST.get('employee_id', '')

        if employee_id:
            employee_id = employee_id
        else:
            employee_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewEmployeeDetails', [employee_id])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    
                    for e in emp:
                        employee_id = e['id']
                        cursor1 = connection.cursor()
                        cursor1.callproc('getEmployeePassportDetails', [employee_id])
                        passport = dictfetchall(cursor1)
                        cursor1.close()
                        e['PassportDetails'] = passport
                    

                    data = {'success': 1, 'Employee': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_employee_documents(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        employee_id = request.POST.get('employee_id', '')

        if employee_id:
            employee_id = employee_id
        else:
            employee_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllEmployeeDocumentDetails', [employee_id])
                    emp = dictfetchall(cursor)
                    cursor.close()
                  
                    data = {'success': 1, 'Employee': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)

def view_agent(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        agent_id = request.POST.get('agent_id', '')

        if agent_id:
            agent_id = agent_id
        else:
            agent_id = '0'
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewAgentDetails', [agent_id])
                    agent = dictfetchall(cursor)
                    data = {'success': 1, 'Agent': agent}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def assessment_codes(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id;
        else:
            corporate_id = 0;

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateAssessmentCodes', [corporate_id, user.id, user_type])
                    agent = dictfetchall(cursor)
                    print("dsafsafasfasf COCOCC")
                    print(agent)
                    data = {'success': 1, 'Codes': agent}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_assessment_codes(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        assessment_code = request.POST.get('assessment_code', '')
        code_desc = request.POST.get('code_desc', '')
        from_date = request.POST.get('from_date', '')
        from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('to_date', '')
        to_date = datetime.strptime(to_date, '%d-%m-%Y')
        service_from = request.POST.get('service_from', '')
        service_from = datetime.strptime(service_from, '%d-%m-%Y')
        service_to = request.POST.get('service_to', '')
        service_to = datetime.strptime(service_to, '%d-%m-%Y')

        print(from_date)
        print(to_date)
        print(service_from)
        print(service_to)

        if from_date:
            pass
        else:
            from_date = None

        if to_date:
            pass
        else:
            to_date = None

        if service_from:
            pass
        else:
            service_from = None

        if service_to:
            pass
        else:
            service_to = None

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addCorporateAssessmentCodes', [corporate_id,assessment_code,code_desc,from_date,to_date,user_id,user_type,service_from,service_to])
                    agent = dictfetchall(cursor)
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Assessment Code Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_assessment_codes(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        assessment_code = request.POST.get('assessment_code', '')
        code_desc = request.POST.get('code_desc', '')
        from_date = request.POST.get('from_date', '')
        from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('to_date', '')
        to_date = datetime.strptime(to_date, '%d-%m-%Y')
        code_id = request.POST.get('code_id', '')
        service_from = request.POST.get('service_from', '')
        service_from = datetime.strptime(service_from, '%d-%m-%Y')
        service_to = request.POST.get('service_to', '')
        service_to = datetime.strptime(service_to, '%d-%m-%Y')

        print(from_date)
        print(to_date)
        print(service_from)
        print(service_to)

        if from_date:
            pass
        else:
            from_date = None

        if to_date:
            pass
        else:
            to_date = None

        if service_from:
            pass
        else:
            service_from = None

        if service_to:
            pass
        else:
            service_to = None
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateCorporateAssessmentCodes', [corporate_id,assessment_code,code_desc,from_date,to_date,code_id,user_id,user_type,service_from,service_to])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Assessment Code Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_assessment_codes(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        code_id = request.POST.get('code_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteCorporateAssessmentCodes', [code_id,user_id,user_type])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Assessment Code Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def assessment_cities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id;
        else:
            corporate_id = 0;
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateAssessmentCities', [corporate_id, user.id, user_type])
                    agent = dictfetchall(cursor)
                    data = {'success': 1, 'Cities': agent}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_assessment_cities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        city_name = request.POST.get('city_name', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addCorporateAssessmentCity', [corporate_id,city_name,user_id,user_type])
                    company = dictfetchall(cursor)
                    print(company)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Assessment City Added Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error11': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_assessment_cities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        corporate_id = request.POST.get('corporate_id', '')
        city_name = request.POST.get('city_name', '')
        city_id = request.POST.get('city_id')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateCorporateAssessmentCity', [corporate_id,city_name,city_id,user_id,user_type])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Assessment City Updated Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_assessment_cities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        city_id = request.POST.get('city_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deleteCorporateAssessmentCity', [city_id,user_id,user_type])

                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Assessment City Deleted Successfully"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_agents(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllAgentsDetails', [])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'Agents': emp}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_agents(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        agent_id = request.POST.get('agent_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewAgentsDetails', [agent_id])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'Agents': emp}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)
################################## Taxi Booking  ###############################

def view_taxi_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewTaxiBooking', [booking_id])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    cursor1 = connection.cursor()
                    booking_id = emp[0]['id']
                    corporate_id = emp[0]['corporate_id']
                    print(booking_id)
                    cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    cursor1.close()

                    cursor4 = connection.cursor()
                    cursor4.callproc('getAllCorporateBillingEntitiesDetails', [corporate_id, user.id, user_type])
                    actions1 = dictfetchall(cursor4)
                    emp[0]['ClientEntity'] = actions1
                    cursor4.close()

                    cursor5 = connection.cursor()
                    cursor5.callproc('getAllCotravBillingEntities', [])
                    actions2 = dictfetchall(cursor5)
                    emp[0]['CotravEntity'] = actions2
                    cursor5.close()

                    cursor6 = connection.cursor()
                    cursor6.callproc('getAllCorporateRatesDetails', [corporate_id, user.id, user_type])
                    actions3 = dictfetchall(cursor6)
                    emp[0]['Packages'] = actions3
                    cursor6.close()

                    cursor7 = connection.cursor()
                    cursor7.callproc('getAllCorporateEmployeesDetails', [corporate_id, user.id, user_type])
                    actions6 = dictfetchall(cursor7)
                    emp[0]['Employees'] = actions6
                    cursor7.close()

                    cursor8 = connection.cursor()
                    cursor8.callproc('getAllCorporateSpocsDetails', [corporate_id, user.id, user_type])
                    actions63 = dictfetchall(cursor8)
                    emp[0]['Spocs'] = actions63
                    cursor8.close()

                    cursor9 = connection.cursor()
                    cursor9.callproc('getAllCorporateAssessmentCities', [corporate_id, user.id, user_type])
                    actions62 = dictfetchall(cursor9)
                    emp[0]['AssCities'] = actions62
                    cursor9.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCorporateAssessmentCodes', [corporate_id, user.id, user_type])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['AssCodes'] = actions61
                    cursor81.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllTaxiBookingsActionLogs', [booking_id])
                    actions = dictfetchall(cursor3)
                    cursor3.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllTrackingStatusByBookingID', [1, booking_id])
                    flights = dictfetchall(cursor2)
                    emp[0]['TrackingStatus'] = flights
                    cursor2.close()

                    cursor21 = connection.cursor()
                    cursor21.callproc('getAllBookingFeedbackByBookingID', [1, booking_id])
                    flights1 = dictfetchall(cursor21)
                    emp[0]['BookingFeedbacks'] = flights1
                    cursor21.close()


                    if emp[0]['is_invoice']:
                        cursor2 = connection.cursor()
                        invoice_id = emp[0]['invoice_id']
                        print(invoice_id)
                        print("iiiiiiinnnnnvvvvvoooo")
                        cursor2.callproc('getallTaxiInvoiceActionLog', [invoice_id])
                        invoicess = dictfetchall(cursor2)
                        emp[0]['InvoiceActionLog'] = invoicess
                        cursor2.close()

                    emp[0]['Passangers'] = passanger
                    emp[0]['ActionLogs'] = actions
                    data = {'success': 1, 'Bookings': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_bus_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewBusBooking', [booking_id])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    cursor1 = connection.cursor()
                    booking_id = emp[0]['id']
                    corporate_id = emp[0]['corporate_id']
                    print(booking_id)
                    cursor1.callproc('getAllBusBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    cursor1.close()

                    cursor4 = connection.cursor()
                    cursor4.callproc('getAllCorporateBillingEntitiesDetails', [corporate_id, user.id, user_type])
                    actions1 = dictfetchall(cursor4)
                    emp[0]['ClientEntity'] = actions1
                    cursor4.close()

                    cursor5 = connection.cursor()
                    cursor5.callproc('getAllCotravBillingEntities', [])
                    actions2 = dictfetchall(cursor5)
                    emp[0]['CotravEntity'] = actions2
                    cursor5.close()

                    cursor7 = connection.cursor()
                    cursor7.callproc('getAllCorporateEmployeesDetails', [corporate_id, user.id, user_type])
                    actions6 = dictfetchall(cursor7)
                    emp[0]['Employees'] = actions6
                    cursor7.close()

                    cursor8 = connection.cursor()
                    cursor8.callproc('getAllCorporateSpocsDetails', [corporate_id, user.id, user_type])
                    actions63 = dictfetchall(cursor8)
                    emp[0]['Spocs'] = actions63
                    cursor8.close()

                    cursor9 = connection.cursor()
                    cursor9.callproc('getAllCorporateAssessmentCities', [corporate_id, user.id, user_type])
                    actions62 = dictfetchall(cursor9)
                    emp[0]['AssCities'] = actions62
                    cursor9.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCorporateAssessmentCodes', [corporate_id, user.id, user_type])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['AssCodes'] = actions61
                    cursor81.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllBusBookingsActionLogs', [booking_id])
                    actions = dictfetchall(cursor3)
                    cursor3.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllTrackingStatusByBookingID', [2, booking_id])
                    flights = dictfetchall(cursor2)
                    emp[0]['TrackingStatus'] = flights
                    cursor2.close()

                    cursor21 = connection.cursor()
                    cursor21.callproc('getAllBookingFeedbackByBookingID', [2, booking_id])
                    flights1 = dictfetchall(cursor21)
                    emp[0]['BookingFeedbacks'] = flights1
                    cursor21.close()

                    if emp[0]['is_invoice']:
                        cursor2 = connection.cursor()
                        invoice_id = emp[0]['invoice_id']
                        print(invoice_id)
                        print("iiiiiiinnnnnvvvvvoooo")
                        cursor2.callproc('getallTaxiInvoiceActionLog', [invoice_id])
                        invoicess = dictfetchall(cursor2)
                        emp[0]['InvoiceActionLog'] = invoicess
                        cursor2.close()

                    emp[0]['Passangers'] = passanger
                    emp[0]['ActionLogs'] = actions
                    data = {'success': 1, 'Bookings': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_train_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewTrainBooking', [booking_id])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    cursor1 = connection.cursor()
                    booking_id = emp[0]['id']
                    corporate_id = emp[0]['corporate_id']

                    cursor1.callproc('getAllTrainBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    cursor1.close()

                    cursor4 = connection.cursor()
                    cursor4.callproc('getAllCorporateBillingEntitiesDetails', [corporate_id, user.id, user_type])
                    actions1 = dictfetchall(cursor4)
                    emp[0]['ClientEntity'] = actions1
                    cursor4.close()

                    cursor5 = connection.cursor()
                    cursor5.callproc('getAllCotravBillingEntities', [])
                    actions2 = dictfetchall(cursor5)
                    emp[0]['CotravEntity'] = actions2
                    cursor5.close()

                    cursor7 = connection.cursor()
                    cursor7.callproc('getAllCorporateEmployeesDetails', [corporate_id, user.id, user_type])
                    actions6 = dictfetchall(cursor7)
                    emp[0]['Employees'] = actions6
                    cursor7.close()

                    cursor8 = connection.cursor()
                    cursor8.callproc('getAllCorporateSpocsDetails', [corporate_id, user.id, user_type])
                    actions63 = dictfetchall(cursor8)
                    emp[0]['Spocs'] = actions63
                    cursor8.close()

                    cursor9 = connection.cursor()
                    cursor9.callproc('getAllCorporateAssessmentCities', [corporate_id, user.id, user_type])
                    actions62 = dictfetchall(cursor9)
                    emp[0]['AssCities'] = actions62
                    cursor9.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCorporateAssessmentCodes', [corporate_id, user.id, user_type])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['AssCodes'] = actions61
                    cursor81.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllTrainTypes', [])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['TrainTypes'] = actions61
                    cursor81.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllRailwayStations', [])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['Stations'] = actions61
                    cursor81.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllTrainBookingsActionLogs', [booking_id])
                    actions = dictfetchall(cursor3)
                    cursor3.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllTrackingStatusByBookingID', [3, booking_id])
                    flights = dictfetchall(cursor2)
                    emp[0]['TrackingStatus'] = flights
                    cursor2.close()

                    cursor21 = connection.cursor()
                    cursor21.callproc('getAllBookingFeedbackByBookingID', [3, booking_id])
                    flights1 = dictfetchall(cursor21)
                    emp[0]['BookingFeedbacks'] = flights1
                    cursor21.close()


                    if emp[0]['is_invoice']:
                        cursor2 = connection.cursor()
                        invoice_id = emp[0]['invoice_id']
                        print(invoice_id)
                        print("iiiiiiinnnnnvvvvvoooo")
                        cursor2.callproc('getallTaxiInvoiceActionLog', [invoice_id])
                        invoicess = dictfetchall(cursor2)
                        emp[0]['InvoiceActionLog'] = invoicess
                        cursor2.close()

                    emp[0]['Passangers'] = passanger
                    emp[0]['ActionLogs'] = actions

                    data = {'success': 1, 'Bookings': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_hotel_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:

                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewHotelBooking', [booking_id])
                    emp = dictfetchall(cursor)
                    print(emp)
                    cursor.close()
                    cursor1 = connection.cursor()
                    booking_id = emp[0]['id']
                    corporate_id = emp[0]['corporate_id']
                    print(booking_id)

                    cursor1.callproc('getAllHotelBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    cursor1.close()

                    cursor4 = connection.cursor()
                    cursor4.callproc('getAllCorporateBillingEntitiesDetails', [corporate_id, user.id, user_type])
                    actions1 = dictfetchall(cursor4)
                    emp[0]['ClientEntity'] = actions1
                    cursor4.close()

                    cursor5 = connection.cursor()
                    cursor5.callproc('getAllCotravBillingEntities', [])
                    actions2 = dictfetchall(cursor5)
                    emp[0]['CotravEntity'] = actions2
                    cursor5.close()

                    cursor7 = connection.cursor()
                    cursor7.callproc('getAllCorporateEmployeesDetails', [corporate_id, user.id, user_type])
                    actions6 = dictfetchall(cursor7)
                    emp[0]['Employees'] = actions6
                    cursor7.close()

                    cursor8 = connection.cursor()
                    cursor8.callproc('getAllCorporateSpocsDetails', [corporate_id, user.id, user_type])
                    actions63 = dictfetchall(cursor8)
                    emp[0]['Spocs'] = actions63
                    cursor8.close()

                    cursor9 = connection.cursor()
                    cursor9.callproc('getAllCorporateAssessmentCities', [corporate_id, user.id, user_type])
                    actions62 = dictfetchall(cursor9)
                    emp[0]['AssCities'] = actions62
                    cursor9.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCorporateAssessmentCodes', [corporate_id, user.id, user_type])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['AssCodes'] = actions61
                    cursor81.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCity', [])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['cities'] = actions61
                    cursor81.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllRoomTypes', [])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['RoomTypes'] = actions61
                    cursor81.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllRoomTypes', [])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['Buckets'] = actions61
                    cursor81.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllHotelTypes', [])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['RoomTypes'] = actions61
                    cursor81.close()


                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllTrackingStatusByBookingID', [4, booking_id])
                    flights = dictfetchall(cursor2)
                    emp[0]['TrackingStatus'] = flights
                    cursor2.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllHotelBookingsActionLogs', [booking_id])
                    actions = dictfetchall(cursor3)
                    cursor3.close()

                    cursor21 = connection.cursor()
                    cursor21.callproc('getAllBookingFeedbackByBookingID', [4, booking_id])
                    flights1 = dictfetchall(cursor21)
                    emp[0]['BookingFeedbacks'] = flights1
                    cursor21.close()

                    if emp[0]['is_invoice']:
                        cursor2 = connection.cursor()
                        invoice_id = emp[0]['invoice_id']
                        print(invoice_id)
                        print("iiiiiiinnnnnvvvvvoooo")
                        cursor2.callproc('getallTaxiInvoiceActionLog', [invoice_id])
                        invoicess = dictfetchall(cursor2)
                        emp[0]['InvoiceActionLog'] = invoicess
                        cursor2.close()

                    emp[0]['Passangers'] = passanger
                    emp[0]['ActionLogs'] = actions

                    data = {'success': 1, 'Bookings': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_flight_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewFlightBooking', [booking_id])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    cursor1 = connection.cursor()
                    booking_id = emp[0]['id']
                    corporate_id = emp[0]['corporate_id']


                    cursor1.callproc('getAllFlightBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    cursor1.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllFlightBookingFlights', [booking_id])
                    flights = dictfetchall(cursor2)
                    cursor2.close()

                    cursor4 = connection.cursor()
                    cursor4.callproc('getAllCorporateBillingEntitiesDetails', [corporate_id, user.id, user_type])
                    actions1 = dictfetchall(cursor4)
                    emp[0]['ClientEntity'] = actions1
                    cursor4.close()

                    cursor5 = connection.cursor()
                    cursor5.callproc('getAllCotravBillingEntities', [])
                    actions2 = dictfetchall(cursor5)
                    emp[0]['CotravEntity'] = actions2
                    cursor5.close()

                    cursor7 = connection.cursor()
                    cursor7.callproc('getAllCorporateEmployeesDetails', [corporate_id, user.id, user_type])
                    actions6 = dictfetchall(cursor7)
                    emp[0]['Employees'] = actions6
                    cursor7.close()

                    cursor8 = connection.cursor()
                    cursor8.callproc('getAllCorporateSpocsDetails', [corporate_id, user.id, user_type])
                    actions63 = dictfetchall(cursor8)
                    emp[0]['Spocs'] = actions63
                    cursor8.close()

                    cursor9 = connection.cursor()
                    cursor9.callproc('getAllCorporateAssessmentCities', [corporate_id, user.id, user_type])
                    actions62 = dictfetchall(cursor9)
                    emp[0]['AssCities'] = actions62
                    cursor9.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCorporateAssessmentCodes', [corporate_id, user.id, user_type])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['AssCodes'] = actions61
                    cursor81.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllFlightBookingsActionLogs', [booking_id])
                    actions = dictfetchall(cursor3)
                    cursor3.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllTrackingStatusByBookingID', [5, booking_id])
                    flights22 = dictfetchall(cursor2)
                    emp[0]['TrackingStatus'] = flights22
                    cursor2.close()

                    cursor21 = connection.cursor()
                    cursor21.callproc('getAllBookingFeedbackByBookingID', [5, booking_id])
                    flights1 = dictfetchall(cursor21)
                    emp[0]['BookingFeedbacks'] = flights1
                    cursor21.close()

                    if emp[0]['is_invoice']:
                        cursor2 = connection.cursor()
                        invoice_id = emp[0]['invoice_id']
                        cursor2.callproc('getallTaxiInvoiceActionLog', [invoice_id])
                        invoicess = dictfetchall(cursor2)
                        emp[0]['InvoiceActionLog'] = invoicess
                        cursor2.close()

                    emp[0]['Passangers'] = passanger
                    emp[0]['Flights'] = flights
                    emp[0]['ActionLogs'] = actions
                    data = {'success': 1, 'message': 'Feedback Added Successfully..!', 'Bookings': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': 'Feedback Failed to Add..!', 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_city_name(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        city_name = request.POST.get('city_name', '')
        state_id = request.POST.get('state_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:

                    cursor.callproc('addCities', [city_name,state_id])
                    result = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Data Insert Successfully",'id':result}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_state_name(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        city_state = request.POST.get('city_state', '')
        country_id = request.POST.get('country_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:

                    cursor.callproc('addState', [city_state,country_id])
                    result = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Data Insert Successfully",'id':result}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_country_name(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        city_country = request.POST.get('city_country', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:

                    cursor.callproc('addCountry', [city_country])
                    result = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Data Insert Successfully",'id':result}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_taxi_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        corporate_id = request.POST.get('corporate_id', '')
        booking_email = request.POST.get('booking_email', '')
        entity_id = request.POST.get('entity_id', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')
        print("i m in api")
        tour_type = request.POST.get('tour_type', '')
        pickup_city = request.POST.get('pickup_city', '')
        pickup_location = request.POST.get('pickup_location', '')
        drop_location = request.POST.get('drop_location', '')
        pickup_datetime = request.POST.get('pickup_datetime', '')
        booking_datetime = request.POST.get('booking_datetime', '')
        if booking_datetime:
            booking_datetime = datetime.strptime(booking_datetime, '%d-%m-%Y %H:%M:%S')
        else:
            timezone.activate(pytz.timezone("Asia/Kolkata"))
            booking_datetime = timezone.localtime(timezone.now())
            print(booking_datetime)
        pickup_datetime = datetime.strptime(pickup_datetime, '%d-%m-%Y %H:%M:%S')
        taxi_type = request.POST.get('taxi_type')
        package_id = request.POST.get('package_id')
        no_of_days = request.POST.get('no_of_days', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        is_sms = request.POST.get('is_sms', '')
        is_email = request.POST.get('is_email', '')

        if booking_email:
            pass
        else:
            booking_email=''

        if taxi_type:
            taxi_type = taxi_type
        else:
            taxi_type = 0

        if package_id:
            package_id = package_id
        else:
            package_id = 0

        if no_of_days:
            no_of_days = no_of_days
        else:
            no_of_days = 0

        if assessment_code:
            pass
        else:
            assessment_code =0

        if assessment_city_id:
            pass
        else:
            assessment_city_id =0

        if booking_datetime:
            pass
        else:
            timezone.activate(pytz.timezone("Asia/Kolkata"))
            booking_datetime = timezone.localtime(timezone.now())  # change field

        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    booking_reference_no = ''
                    cursor.callproc('addTaxiBooking', [user_type,user_id,entity_id,corporate_id,spoc_id,group_id,subgroup_id,tour_type,pickup_city,pickup_location,drop_location,pickup_datetime,
                    taxi_type,package_id,no_of_days,reason_booking,no_of_seats,assessment_code,assessment_city_id,employees,booking_datetime,
                    booking_email,'@last_booking_id','@booking_reference_no',bta_code_travel_req_no])
                    booking_id = dictfetchall(cursor)
                    print(booking_id)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        cursor.execute("SELECT @last_booking_id")
                        last_booking_id = cursor.fetchone()[0]
                        print(last_booking_id)
                        cursor.close()

                        cursor12 = connection.cursor()
                        cursor12.execute("SELECT @booking_reference_no")
                        booking_reference_no = cursor12.fetchone()[0]
                        print("Booking Refrence no")
                        print(booking_reference_no)
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
                        cursor3.callproc('getAllApproverByBookingID', [last_booking_id,1])
                        approvers = dictfetchall(cursor3)
                        cursor3.close()

                        fcm = FCM()
                        thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Taxi"))
                        thread.start()

                        add_booking_email = AddBooking_Email()
                        if is_email == '1':
                            thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Taxi"))
                            thread.start()
                            #resp6 = add_booking_email.send_taxi_email(emp, approvers, "Taxi")
                        if is_sms == '1':
                            thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Taxi"))
                            thread.start()
                            #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Taxi")

                        data = {'success': 1, 'message': "Taxi Booking Added Successfully..! Your Booking ID is : "+str(booking_reference_no),'booking_reference_no':booking_reference_no}
                        return JsonResponse(data)
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': e}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def edit_taxi_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        booking_email = request.POST.get('booking_email', '')
        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        booking_id = request.POST.get('booking_id', '')
        tour_type = request.POST.get('tour_type', '')
        current_city_id = request.POST.get('current_city_id', '')
        taxi_type = request.POST.get('taxi_type', '')
        no_of_days = request.POST.get('no_of_days', '')
        pickup_location = request.POST.get('pickup_location', '')
        drop_location = request.POST.get('drop_location', '')
        pickup_datetime = request.POST.get('pickup_datetime', '')
        pickup_datetime = datetime.strptime(pickup_datetime, '%d-%m-%Y %H:%M:%S')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        cotrav_billing_entity = request.POST.get('cotrav_billing_entity', '')
        rate_id = request.POST.get('rate_id', '')
        reason_booking = request.POST.get('reason_booking', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        if booking_email:
            pass
        else:
            booking_email=''

        if taxi_type:
            taxi_type = taxi_type
        else:
            taxi_type = 0

        if rate_id:
            rate_id = rate_id
        else:
            rate_id = 0

        if no_of_days:
            no_of_days = no_of_days
        else:
            no_of_days = 0

        no_of_seats = request.POST.get('no_of_seats', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateTaxiBooking', [booking_id,booking_email,tour_type,current_city_id,taxi_type,no_of_days,pickup_location,drop_location,
                    pickup_datetime,billing_entity_id,cotrav_billing_entity,rate_id,no_of_seats,reason_booking,assessment_code,assessment_city_id,spoc_id,
                    group_id,subgroup_id,employees,user_id,user_type])
                    booking_id = dictfetchall(cursor)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        data = {'success': 1, 'message': "Taxi Booking Updated Successfully..! "}
                        return JsonResponse(data)
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': e}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_bus_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')

        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        corporate_id = request.POST.get('corporate_id', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        from_location = request.POST.get('from', '')
        to_location = request.POST.get('to', '')
        bus_type = request.POST.get('bus_type', '')
        bus_type2 = request.POST.get('bus_type2', '')
        bus_type3 = request.POST.get('bus_type3', '')
        booking_datetime = request.POST.get('booking_datetime', '')
        if booking_datetime:
            booking_datetime = datetime.strptime(booking_datetime, '%d-%m-%Y %H:%M:%S')
        else:
            timezone.activate(pytz.timezone("Asia/Kolkata"))
            booking_datetime = timezone.localtime(timezone.now())
            print(booking_datetime)

        journey_datetime = request.POST.get('journey_datetime', '')
        journey_datetime = datetime.strptime(journey_datetime, '%d-%m-%Y %H:%M:%S')
        journey_datetime_to = request.POST.get('journey_datetime_to', '')
        journey_datetime_to = datetime.strptime(journey_datetime_to, '%d-%m-%Y %H:%M:%S')
        entity_id = request.POST.get('entity_id', '')
        preferred_bus = request.POST.get('preferred_bus', '')
        preferred_board_point = request.POST.get('preferred_board_point', '')
        preferred_drop_point = request.POST.get('preferred_drop_point', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        is_email = request.POST.get('is_email', '')
        is_sms = request.POST.get('is_sms', '')

        if booking_email:
            pass
        else:
            booking_email=''

        if assessment_code:
            pass
        else:
            assessment_code=0

        if assessment_city_id:
            pass
        else:
            assessment_city_id=0

        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    booking_reference_no = ''
                    cursor.callproc('addBusBooking', [user_type,user_id,corporate_id,spoc_id,group_id,subgroup_id,from_location,
                    to_location,bus_type,bus_type2,bus_type3,booking_datetime,journey_datetime,entity_id,preferred_bus,reason_booking,no_of_seats,
                    assessment_code,assessment_city_id,employees,booking_email,journey_datetime_to,'@last_booking_id','@booking_reference_no',
                    bta_code_travel_req_no,preferred_board_point,preferred_drop_point])
                    booking_id = dictfetchall(cursor)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        cursor.execute("SELECT @last_booking_id")
                        last_booking_id = cursor.fetchone()[0]
                        print(last_booking_id)
                        cursor.close()

                        cursor12 = connection.cursor()
                        cursor12.execute("SELECT @booking_reference_no")
                        booking_reference_no = cursor12.fetchone()[0]
                        print("Booking Refrence no")
                        print(booking_reference_no)
                        cursor12.close()

                        cursor2 = connection.cursor()
                        cursor2.callproc('viewBusBooking', [last_booking_id])
                        emp = dictfetchall(cursor2)
                        cursor2.close()

                        cursor1 = connection.cursor()
                        cursor1.callproc('getAllBusBookingPassangers', [last_booking_id])
                        passanger = dictfetchall(cursor1)
                        emp[0]['Passangers'] = passanger
                        cursor1.close()

                        cursor3 = connection.cursor()
                        cursor3.callproc('getAllApproverByBookingID', [last_booking_id,2])
                        approvers = dictfetchall(cursor3)
                        cursor3.close()

                        fcm = FCM()
                        thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Bus"))
                        thread.start()

                        add_booking_email = AddBooking_Email()
                        if is_email  == '1':
                            thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Bus"))
                            thread.start()
                            #resp6 = add_booking_email.send_taxi_email(emp, approvers, "Bus")
                        if is_sms == '1':
                            thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Bus"))
                            thread.start()
                            #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Bus")

                    cursor.close()
                    data = {'success': 1, 'message': "Bus Booking Added Successfully..! Your Booking ID is : "+str(booking_reference_no),'booking_reference_no':booking_reference_no}
                    return JsonResponse(data)

                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def edit_bus_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        booking_id = request.POST.get('booking_id', '')
        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        from_location = request.POST.get('from', '')
        to_location = request.POST.get('to', '')
        bus_type = request.POST.get('bus_type', '')
        bus_type2 = request.POST.get('bus_type2', '')
        journey_datetime = request.POST.get('journey_datetime', '')
        journey_datetime = datetime.strptime(journey_datetime, '%d-%m-%Y %H:%M:%S')
        journey_datetime_to = request.POST.get('journey_datetime_to', '')
        journey_datetime_to = datetime.strptime(journey_datetime_to, '%d-%m-%Y %H:%M:%S')

        preferred_bus = request.POST.get('preferred_bus', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        cotrav_billing_entity = request.POST.get('cotrav_billing_entity', '')
        billing_entity_id = request.POST.get('billing_entity_id', '')

        if booking_email:
            pass
        else:
            booking_email=''

        no_of_seats = request.POST.get('no_of_seats', '')
        reason_booking = request.POST.get('reason_booking', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateBusBooking', [booking_id,bta_code_travel_req_no,booking_email,from_location,to_location,bus_type,
                    journey_datetime,journey_datetime_to,preferred_bus,billing_entity_id,cotrav_billing_entity,no_of_seats,reason_booking,assessment_code,assessment_city_id,spoc_id,
                    group_id,subgroup_id,employees,user_id,user_type,bus_type2])
                    booking_id = dictfetchall(cursor)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        data = {'success': 1, 'message': "Bus Booking Updated Successfully..! "}
                        return JsonResponse(data)
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': e}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_train_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')

        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        corporate_id = request.POST.get('corporate_id', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        from_location = request.POST.get('from', '')
        to_location = request.POST.get('to', '')
        train_type = request.POST.get('train_type', '')
        booking_datetime = request.POST.get('booking_datetime', '')
        if booking_datetime:
            booking_datetime = datetime.strptime(booking_datetime, '%d-%m-%Y %H:%M:%S')
        else:
            timezone.activate(pytz.timezone("Asia/Kolkata"))
            booking_datetime = timezone.localtime(timezone.now())
            print(booking_datetime)

        journey_datetime = request.POST.get('journey_datetime', '')
        journey_datetime = datetime.strptime(journey_datetime, '%d-%m-%Y %H:%M:%S')
        journey_datetime_to = request.POST.get('journey_datetime_to', '')
        journey_datetime_to = datetime.strptime(journey_datetime_to, '%d-%m-%Y %H:%M:%S')
        entity_id = request.POST.get('entity_id', '')
        preferred_train = request.POST.get('preferred_train', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        is_email = request.POST.get('is_email', '')
        is_sms = request.POST.get('is_sms', '')

        if booking_email:
            pass
        else:
            booking_email=''

        if assessment_code:
            pass
        else:
            assessment_code=0

        if assessment_city_id:
            pass
        else:
            assessment_city_id=0

        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    booking_reference_no = ''
                    cursor.callproc('addTrainBooking', [user_type,user_id,corporate_id,spoc_id,group_id,subgroup_id,from_location,
                    to_location,train_type,train_type,train_type,booking_datetime,journey_datetime,entity_id,preferred_train,reason_booking,
                    no_of_seats,assessment_code,assessment_city_id,employees,booking_email,journey_datetime_to,'@last_booking_id','@booking_reference_no',bta_code_travel_req_no])
                    booking_id = dictfetchall(cursor)
                    print(booking_id)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        cursor.execute("SELECT @last_booking_id")
                        last_booking_id = cursor.fetchone()[0]
                        print(last_booking_id)
                        cursor.close()

                        cursor12 = connection.cursor()
                        cursor12.execute("SELECT @booking_reference_no")
                        booking_reference_no = cursor12.fetchone()[0]
                        print("Booking Refrence no")
                        print(booking_reference_no)
                        cursor12.close()

                        cursor2 = connection.cursor()
                        cursor2.callproc('viewTrainBooking', [last_booking_id])
                        emp = dictfetchall(cursor2)
                        cursor2.close()

                        cursor1 = connection.cursor()
                        cursor1.callproc('getAllTrainBookingPassangers', [last_booking_id])
                        passanger = dictfetchall(cursor1)
                        emp[0]['Passangers'] = passanger
                        cursor1.close()

                        cursor3 = connection.cursor()
                        cursor3.callproc('getAllApproverByBookingID', [last_booking_id,3])
                        approvers = dictfetchall(cursor3)
                        cursor3.close()

                        fcm = FCM()
                        thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Train"))
                        thread.start()

                        add_booking_email = AddBooking_Email()
                        if is_email == '1':
                            thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Train"))
                            thread.start()
                            #resp6 = add_booking_email.send_taxi_email(emp, approvers, "Train")
                        if is_sms == '1':
                            thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Train"))
                            thread.start()
                            #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Train")

                        cursor.close()

                        data = {'success': 1, 'message': "Train Booking Added Successfully..! Your Booking ID is : " + str(booking_reference_no), 'booking_reference_no': booking_reference_no}
                        return JsonResponse(data)

                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def edit_train_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        booking_id = request.POST.get('booking_id', '')
        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        from_location = request.POST.get('from', '')
        to_location = request.POST.get('to', '')
        bus_type = request.POST.get('train_type_priority_1', '')
        bus_type2 = request.POST.get('train_type_priority_2', '')
        journey_datetime = request.POST.get('journey_datetime', '')
        journey_datetime = datetime.strptime(journey_datetime, '%d-%m-%Y %H:%M:%S')
        journey_datetime_to = request.POST.get('journey_datetime_to', '')
        journey_datetime_to = datetime.strptime(journey_datetime_to, '%d-%m-%Y %H:%M:%S')

        preferred_bus = request.POST.get('preferred_bus', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        cotrav_billing_entity = request.POST.get('cotrav_billing_entity', '')
        billing_entity_id = request.POST.get('billing_entity_id', '')

        if booking_email:
            pass
        else:
            booking_email=''

        no_of_seats = request.POST.get('no_of_seats', '')
        reason_booking = request.POST.get('reason_booking', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('updateTrainBooking', [booking_id,bta_code_travel_req_no,booking_email,from_location,to_location,bus_type,
                    journey_datetime,journey_datetime_to,preferred_bus,billing_entity_id,cotrav_billing_entity,no_of_seats,reason_booking,assessment_code,assessment_city_id,spoc_id,
                    group_id,subgroup_id,employees,user_id,user_type,bus_type2])
                    booking_id = dictfetchall(cursor)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        data = {'success': 1, 'message': "Train Booking Updated Successfully..! "}
                        return JsonResponse(data)
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': e}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_hotel_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')

        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        corporate_id = request.POST.get('corporate_id', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        from_city_id = request.POST.get('from_city_id', '')
        from_area_id = request.POST.get('from_area_id', '')
        preferred_area = request.POST.get('preferred_area', '')
        bucket_priority_1 = request.POST.get('bucket_priority_1', '')
        bucket_priority_2 = request.POST.get('bucket_priority_2', '')
        room_type_id = request.POST.get('room_type_id', '')

        booking_datetime = request.POST.get('booking_datetime', '')
        if booking_datetime:
            booking_datetime = datetime.strptime(booking_datetime, '%d-%m-%Y %H:%M:%S')
        else:
            timezone.activate(pytz.timezone("Asia/Kolkata"))
            booking_datetime = timezone.localtime(timezone.now())
            print(booking_datetime)
        
        checkin_datetime = request.POST.get('checkin_datetime', '')
        checkin_datetime = datetime.strptime(checkin_datetime, '%d-%m-%Y %H:%M:%S')
        checkout_datetime = request.POST.get('checkout_datetime', '')
        checkout_datetime = datetime.strptime(checkout_datetime, '%d-%m-%Y %H:%M:%S')
        no_of_nights = request.POST.get('no_of_nights', '')

        preferred_hotel= request.POST.get('preferred_hotel','')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        is_email = request.POST.get('is_email', '')
        is_sms = request.POST.get('is_sms', '')

        if booking_email:
            pass
        else:
            booking_email=''

        if assessment_code:
            pass
        else:
            assessment_code=0

        if assessment_city_id:
            pass
        else:
            assessment_city_id=0

        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    booking_reference_no = ''
                    cursor.callproc('addHotelBooking', [from_city_id,from_area_id,preferred_area,checkin_datetime,checkout_datetime,bucket_priority_1,bucket_priority_2,
                    room_type_id,preferred_hotel,booking_datetime,assessment_code,assessment_city_id,no_of_seats,group_id,subgroup_id,spoc_id,
                    corporate_id,billing_entity_id,reason_booking,user_id,user_type,employees,booking_email,'@last_booking_id',no_of_nights,'@booking_reference_no',bta_code_travel_req_no])
                    booking_id = dictfetchall(cursor)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        cursor.execute("SELECT @last_booking_id")
                        last_booking_id = cursor.fetchone()[0]
                        print(last_booking_id)
                        cursor.close()

                        cursor12 = connection.cursor()
                        cursor12.execute("SELECT @booking_reference_no")
                        booking_reference_no = cursor12.fetchone()[0]
                        print("Booking Refrence no")
                        print(booking_reference_no)
                        cursor12.close()

                        cursor2 = connection.cursor()
                        cursor2.callproc('viewHotelBooking', [last_booking_id])
                        emp = dictfetchall(cursor2)
                        cursor2.close()

                        cursor1 = connection.cursor()
                        cursor1.callproc('getAllHotelBookingPassangers', [last_booking_id])
                        passanger = dictfetchall(cursor1)
                        emp[0]['Passangers'] = passanger
                        cursor1.close()

                        cursor3 = connection.cursor()
                        cursor3.callproc('getAllApproverByBookingID', [last_booking_id,4])
                        approvers = dictfetchall(cursor3)
                        cursor3.close()

                        fcm = FCM()
                        thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Hotel"))
                        thread.start()

                        add_booking_email = AddBooking_Email()
                        if is_email == '1':
                            thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Hotel"))
                            thread.start()
                            #resp6 = add_booking_email.send_taxi_email(emp, approvers, "Hotel")
                        if is_sms == '1':
                            thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Hotel"))
                            thread.start()
                            #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Hotel")

                    data = {'success': 1, 'message': "Hotel Booking Added Successfully..! Your Booking ID is : "+str(booking_reference_no),'booking_reference_no':booking_reference_no}
                    return JsonResponse(data)

                except Exception as e:
                    print("EXCEPTION")
                    print(e)
                    data = {'success': 0, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def edit_hotel_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        booking_id = request.POST.get('booking_id', '')
        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        bucket_priority_1 = request.POST.get('bucket_priority_1', '')
        bucket_priority_2 = request.POST.get('bucket_priority_2', '')
        hotel_type = request.POST.get('hotel_type', '')
        from_city_id = request.POST.get('from_city_id', '')
        from_area_id = request.POST.get('from_area_id', '')
        preferred_area_name = request.POST.get('preferred_area_name', '')


        checkin_datetime = request.POST.get('checkin_datetime', '')
        checkin_datetime = datetime.strptime(checkin_datetime, '%d-%m-%Y %H:%M:%S')
        checkout_datetime = request.POST.get('checkout_datetime', '')
        checkout_datetime = datetime.strptime(checkout_datetime, '%d-%m-%Y %H:%M:%S')
        no_of_nights = 1

        preferred_hotel = request.POST.get('preferred_hotel', '')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        cotrav_billing_entity = request.POST.get('cotrav_billing_entity', '')


        if booking_email:
            pass
        else:
            booking_email = ''

        if assessment_code:
            pass
        else:
            assessment_code = 0

        if assessment_city_id:
            pass
        else:
            assessment_city_id = 0

        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    booking_reference_no = ''
                    cursor.callproc('updateHotelBooking',[booking_id,bta_code_travel_req_no,booking_email,from_city_id,from_area_id,preferred_area_name,
                    checkin_datetime,checkout_datetime,preferred_hotel,billing_entity_id,cotrav_billing_entity,no_of_seats,reason_booking,assessment_code,assessment_city_id,spoc_id,
                    group_id,subgroup_id,employees,user_id,user_type,bucket_priority_1,bucket_priority_2,hotel_type])
                    booking_id = dictfetchall(cursor)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        pass
                    data = {'success': 1, 'message': "Hotel Booking Updated Successfully..!"}
                    return JsonResponse(data)

                except Exception as e:
                    print("EXCEPTION")
                    print(e)
                    data = {'success': 0, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_flight_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        vendor_booking = request.POST.get('vendor_booking', '')
        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')

        corporate_id = request.POST.get('corporate_id', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        usage_type = request.POST.get('usage_type', '')
        journey_type = request.POST.get('trip_type', '')
        flight_class = request.POST.get('seat_type', '')
        from_location = request.POST.get('from_city', '')
        to_location = request.POST.get('to_city', '')

        booking_datetime = request.POST.get('booking_datetime', '')
        if booking_datetime:
            booking_datetime = datetime.strptime(booking_datetime, '%d-%m-%Y %H:%M:%S')
        else:
            timezone.activate(pytz.timezone("Asia/Kolkata"))
            booking_datetime = timezone.localtime(timezone.now())
            print(booking_datetime)

        departure_datetime = request.POST.get('departure_datetime', '')
        departure_datetime = datetime.strptime(departure_datetime, '%d-%m-%Y')

        return_datetime = request.POST.get('return_datetime', '')
        if return_datetime:
            return_datetime = datetime.strptime(return_datetime, '%d-%m-%Y')

        preferred_flight= request.POST.get('preferred_flight','')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        is_sms = request.POST.get('is_sms', '')
        is_email = request.POST.get('is_email', '')

        if booking_email:
            pass
        else:
            booking_email=''

        if assessment_code:
            pass
        else:
            assessment_code=0

        if assessment_city_id:
            pass
        else:
            assessment_city_id=0

        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')
        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        print(employees)

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    last_booking_id = ''
                    cursor.callproc('addFlightBooking', [usage_type,journey_type,flight_class,from_location,to_location,booking_datetime,departure_datetime,
                    preferred_flight,assessment_code,no_of_seats,group_id,subgroup_id,spoc_id,corporate_id,billing_entity_id,reason_booking,user_id,
                    user_type,employees,booking_email,assessment_city_id,'@last_booking_id',vendor_booking,'@booking_reference_no',bta_code_travel_req_no,return_datetime])
                    booking_id = dictfetchall(cursor)
                    print(booking_id)
                    booking_reference_no = ''
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        cursor.execute("SELECT @last_booking_id")
                        last_booking_id = cursor.fetchone()[0]
                        print(last_booking_id)
                        cursor.close()

                        cursor12 = connection.cursor()
                        cursor12.execute("SELECT @booking_reference_no")
                        booking_reference_no = cursor12.fetchone()[0]
                        print("Booking Refrence no")
                        print(booking_reference_no)
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
                        cursor3.callproc('getAllApproverByBookingID', [last_booking_id,5])
                        approvers = dictfetchall(cursor3)
                        cursor3.close()

                        fcm = FCM()
                        thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Flight"))
                        thread.start()

                        add_booking_email = AddBooking_Email()
                        if is_email == '1':
                            thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Flight"))
                            thread.start()
                            #resp6 = add_booking_email.send_taxi_email(emp, approvers, "Flight")
                        if is_sms == '1':
                            thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Flight"))
                            thread.start()
                            #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Flight")

                    cursor.close()
                    data = {'success': 1, 'message': "Flight Booking Added Success",'last_booking_id':last_booking_id,'booking_reference_no':booking_reference_no}
                    return JsonResponse(data)

                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def edit_flight_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        booking_id = request.POST.get('booking_id', '')
        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        booking_email = request.POST.get('booking_email', '')
        usage_type = request.POST.get('usage_type', '')
        journey_type = request.POST.get('trip_type', '')
        flight_class = request.POST.get('seat_type', '')
        from_location = request.POST.get('from_city', '')
        to_location = request.POST.get('to_city', '')
        preferred_flight = request.POST.get('preferred_flight', '')
        assessment_code = request.POST.get('assessment_code', '')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        cotrav_billing_entity = request.POST.get('cotrav_billing_entity', '')

        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        departure_datetime = request.POST.get('departure_datetime', '')
        return_datetime = request.POST.get('return_datetime', '')
        departure_datetime = datetime.strptime(departure_datetime, '%d-%m-%Y')
        if return_datetime:
            return_datetime = datetime.strptime(return_datetime, '%d-%m-%Y')


        if booking_email:
            pass
        else:
            booking_email=''

        if assessment_code:
            pass
        else:
            assessment_code=0

        if assessment_city_id:
            pass
        else:
            assessment_city_id=0

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        print(employees)

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    last_booking_id = ''
                    cursor.callproc('updateFlightBooking', [booking_id,bta_code_travel_req_no,booking_email,usage_type,journey_type,flight_class,from_location,to_location,departure_datetime,
                    preferred_flight,assessment_code,no_of_seats,reason_booking,assessment_city_id,spoc_id,group_id,subgroup_id,employees,user_id, user_type,billing_entity_id,return_datetime])
                    booking_id = dictfetchall(cursor)
                    print(booking_id)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        pass
                    cursor.close()
                    data = {'success': 1, 'message': "Flight Booking Updated Successfully..!"}
                    return JsonResponse(data)

                except Exception as e:
                    print(e)
                    data = {'success': 0, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)
########## sanket added this #########


def taxi_packages(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateTaxiPackages', [])
                    packages = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'packages': packages}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def employee_dashboard(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        employee_id = request.POST.get('employee_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('employeeHomePage', [employee_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def approver_2_dashboard(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        approver_2 = request.POST.get('approver_2_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('Approver_2HomePage', [approver_2])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def approver_1_dashboard(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        approver_1 = request.POST.get('approver_1_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('Approver_1HomePage', [approver_1])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def spoc_dashboard(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        spoc_id = request.POST.get('spoc_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('spocHomePage', [spoc_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def admin_dashboard(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        admin_id = request.POST.get('corporate_id', '')
        print("Corporate id")
        print(admin_id)
        print("Corporate id")
        user_token = req_token.split()
        print("aaaaacccccc")
        print(user_token)
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('adminHomePage', [admin_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def agent_dashboard(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('agentsHomePage', [user.id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def agent_dashboard_om(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('agentsHomePageOperationManager', [user.id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def agent_dashboard_rm(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('agentsHomePageRelationshipManager', [user.id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)

def operator_dashboard(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        operator_id = request.POST.get('operator_id', '')
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('OperatorHomePage', [operator_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Dashboard': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_cotrav_billing_entities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCotravBillingEntities', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Enitity': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def corporate_management_fees(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
        if corporate_id:
            corporate_id = corporate_id
        else:
            corporate_id = '2'
        service_type = 1
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCorporateManagementFees', [corporate_id, service_type])
                    entity = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Fees': entity}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_emp_passport_details(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        employee_id = request.POST.get('employee_id', '')
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getEmployeePassportDetails', [employee_id])
                    entity = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Passport': entity}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)

#################################### FOR MIS ################################


def report_taxi_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        filter_by = request.POST.get('filter_by', '')
        from_date = request.POST.get('booking_from_datetime', '')
        if from_date:
            from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('booking_to_datetime', '')
        if to_date:
            to_date = datetime.strptime(to_date, '%d-%m-%Y')
        booking_status = request.POST.get('booking_status', '')
        company_name = request.POST.get('company_name', '')
        print(filter_by)
        print(from_date)
        print(to_date)
        print(booking_status)
        print(company_name)
        print(user_id)
        print(user_type)
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('reportTaxiBookings', [filter_by,from_date,to_date,booking_status,company_name,user_id,user_type])
                emp = dictfetchall(cursor)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        #print(booking_id)
                        cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()
                        cursor2 = connection.cursor()
                        booking_id = e['id']
                        #print(booking_id)
                        cursor2.callproc('getAllTaxiBookingsActionLogs', [booking_id])
                        action = dictfetchall(cursor2)
                        e['Actions'] = action
                        cursor2.close()
                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                print(emp)
                data = {'success': 1, 'Bookings': emp}
                return JsonResponse(data)

                #data = {'success': 1, 'Bookings': emp}
                #return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def report_bus_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        filter_by = request.POST.get('filter_by', '')
        from_date = request.POST.get('booking_from_datetime', '')
        if from_date:
            from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('booking_to_datetime', '')
        if to_date:
            to_date = datetime.strptime(to_date, '%d-%m-%Y')
        booking_status = request.POST.get('booking_status', '')
        company_name = request.POST.get('company_name', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('reportBusBookings', [filter_by,from_date,to_date,booking_status,company_name,user_id,user_type ])
                emp = dictfetchall(cursor)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        #print(booking_id)
                        cursor1.callproc('getAllBusBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()
                        cursor2 = connection.cursor()
                        booking_id = e['id']
                        #print(booking_id)
                        cursor2.callproc('getAllBusBookingsActionLogs', [booking_id])
                        action = dictfetchall(cursor2)
                        e['Actions'] = action
                        cursor2.close()
                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp}
                return JsonResponse(data)

                #data = {'success': 1, 'Bookings': emp}
                #return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def report_train_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        filter_by = request.POST.get('filter_by', '')
        from_date = request.POST.get('booking_from_datetime', '')
        if from_date:
            from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('booking_to_datetime', '')
        if to_date:
            to_date = datetime.strptime(to_date, '%d-%m-%Y')
        booking_status = request.POST.get('booking_status', '')
        company_name = request.POST.get('company_name', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('reportTrainBookings', [filter_by,from_date,to_date,booking_status,company_name,user_id,user_type ])
                emp = dictfetchall(cursor)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        #print(booking_id)
                        cursor1.callproc('getAllTrainBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()
                        cursor2 = connection.cursor()
                        booking_id = e['id']
                        #print(booking_id)
                        cursor2.callproc('getAllTrainBookingsActionLogs', [booking_id])
                        action = dictfetchall(cursor2)
                        e['Actions'] = action
                        cursor2.close()
                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp}
                return JsonResponse(data)

                #data = {'success': 1, 'Bookings': emp}
                #return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def report_flight_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        filter_by = request.POST.get('filter_by', '')
        from_date = request.POST.get('booking_from_datetime', '')
        if from_date:
            from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('booking_to_datetime', '')
        if to_date:
            to_date = datetime.strptime(to_date, '%d-%m-%Y')
        booking_status = request.POST.get('booking_status', '')
        company_name = request.POST.get('company_name', '')


        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('reportFlightBookings', [filter_by, from_date, to_date, booking_status, company_name,user_id,user_type])
                emp = dictfetchall(cursor)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        # print(booking_id)
                        cursor1.callproc('getAllFlightBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()
                        cursor2 = connection.cursor()
                        booking_id = e['id']
                        # print(booking_id)
                        cursor2.callproc('getAllFlightBookingsActionLogs', [booking_id])
                        action = dictfetchall(cursor2)
                        e['Actions'] = action
                        cursor2.close()

                        cursor3 = connection.cursor()
                        cursor3.callproc('getAllFlightBookingFlights', [booking_id])
                        flights = dictfetchall(cursor3)
                        e['Flights'] = flights
                        cursor3.close()

                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp}
                return JsonResponse(data)

                # data = {'success': 1, 'Bookings': emp}
                # return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def report_hotel_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        filter_by = request.POST.get('filter_by', '')
        from_date = request.POST.get('booking_from_datetime', '')
        if from_date:
            from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('booking_to_datetime', '')
        if to_date:
            to_date = datetime.strptime(to_date, '%d-%m-%Y')
        booking_status = request.POST.get('booking_status', '')
        company_name = request.POST.get('company_name', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('reportHotelBookings', [filter_by, from_date, to_date, booking_status, company_name ,user_id,user_type])
                emp = dictfetchall(cursor)
                print(emp)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        # print(booking_id)
                        cursor1.callproc('getAllHotelBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()
                        cursor2 = connection.cursor()
                        booking_id = e['id']
                        # print(booking_id)
                        cursor2.callproc('getAllHotelBookingsActionLogs', [booking_id])
                        action = dictfetchall(cursor2)
                        e['Actions'] = action
                        cursor2.close()
                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp}
                return JsonResponse(data)

                # data = {'success': 1, 'Bookings': emp}
                # return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_flight_access_token(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getFlightAccessToken', [])
                    train = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Token': train}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def generate_auth_token(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    url = "http://auth.ksofttechnology.com/API/AUTH"
                    payload = {
                        "TYPE": "AUTH",
                        "NAME": "GET_AUTH_TOKEN",
                        "STR": [
                            {
                                "A_ID": "27286260",
                                "U_ID": "test",
                                "PWD": "test",
                                "MODULE": "B2B",
                                "HS": "D"
                            }
                        ]
                    }

                    headers = {}
                    r = requests.post(url, json=payload)
                    api_response = r.json()
                    data = {'success': 1, 'Data': api_response}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'Data': ''}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_flight_search(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        try:
            trip_type = request.POST.get('trip_type', '')
            return_date = request.POST.get('return_date', '')
            fl_class = request.POST.get('fl_class', '')
            no_of_seats = request.POST.get('no_of_seats', '')
            from_city = request.POST.get('from_city', '')
            to_city = request.POST.get('to_city', '')
            departure_date = request.POST.get('departure_date', '')
            d_date = parse(departure_date).strftime("%Y-%m-%d")
            print(d_date)
            if return_date:
                return_date = parse(return_date).strftime("%Y-%m-%d")
            else:
                return_date = ""

            user = {}
            user_token = req_token.split()
            if user_token[0] == 'Token':
                try:
                    user = getUserinfoFromAccessToken(user_token[1], user_type)
                except Exception as e:
                    data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                    return JsonResponse(data)
                if user:
                    try:

                        cursor = connection.cursor()
                        cursor.callproc('getFlightAccessToken', [])
                        token = dictfetchall(cursor)
                        cursor.close()
                        AUTH_TOKEN = token[0]['access_token']
                        url = "http://auth.ksofttechnology.com/API/AUTH"
                        payload = {
                            "TYPE": "AUTH",
                            "NAME": "VERIFY_AUTH_TOKEN",
                            "STR": [
                                {"TOKEN": AUTH_TOKEN, "MODULE": "B2B", "HS": "D"}
                            ]
                        }
                        print(payload)
                        r = requests.post(url, json=payload)
                        print(r)
                        db_token = r.json()
                        print(db_token)
                        print("old DADADA")

                        if db_token['STATUS'] == "FAILED":
                            url = "http://auth.ksofttechnology.com/API/AUTH"
                            payload = {
                                "TYPE": "AUTH",
                                "NAME": "GET_AUTH_TOKEN",
                                "STR": [
                                    {
                                        "A_ID": "79394396",
                                        "U_ID": "Taxivaxi",
                                        "PWD": "Taxi$Vaxi1234",
                                        "MODULE": "B2B",
                                        "HS": "D"
                                    }
                                ]
                            }

                            headers = {}
                            r = requests.post(url, json=payload)
                            new_token = r.json()
                            print(new_token)
                            NEW_AUTH_TOKEN = new_token['RESULT']

                            #old_token = db_token['RESULT']
                            cursor = connection.cursor()
                            cursor.callproc('addFlightAccessToken', [AUTH_TOKEN,NEW_AUTH_TOKEN])
                            token = dictfetchall(cursor)
                            cursor.close()

                        else:
                            AUTH_TOKEN = db_token['RESULT']

                        url = "http://mdt.ksofttechnology.com/API/FLIGHT"
                        payload = {
                                "TYPE": "AIR",
                                "NAME": "GET_FLIGHT",
                                "STR": [
                                    {
                                        "AUTH_TOKEN": ""+AUTH_TOKEN,
                                        "SESSION_ID": "XKWP9TWKSDJ4PAKXKUHE1WM72GTBPO13FTUGF454CIGLQYM6F9",
                                        "TRIP": ""+trip_type,
                                        "SECTOR": "",
                                        "SRC": ""+from_city,
                                        "DES": ""+to_city,
                                        "DEP_DATE": ""+d_date,
                                        "RET_DATE": ""+return_date,
                                        "ADT": ""+no_of_seats,
                                        "CHD": "0",
                                        "INF": "0",
                                        "PC": ""+fl_class,
                                        "PF": "",
                                        "HS": "D"
                                    }
                                ]
                            }

                        headers = {}
                        print(payload)
                        r = requests.post(url, json=payload)
                        api_response = r.json()
                        print(trip_type)
                        print("trip type")
                        if trip_type == '1':
                            print(trip_type)
                            print("trip type")
                            sorted_obj = dict(api_response)
                            sorted_obj['FLIGHT'] = sorted(sorted_obj['FLIGHT'], key=lambda x: int(x['AMT']), reverse=False)
                            for dura in sorted_obj['FLIGHT']:
                                data1 = dura['DUR'].split(':')
                                if data1[0] == '0d':
                                    data1[0] = ''
                                data = data1[0]+' '+data1[1]+' '+data1[2]
                                dura['DUR'] = data
                                if dura['CON_DETAILS']:
                                    for dura1 in dura['CON_DETAILS']:
                                        data2 = dura1['DURATION'].split(':')
                                        if data2[0] == '0d':
                                            data2[0] = ''
                                        data = data2[0] + ' ' + data2[1] + ' ' + data2[2]
                                        dura1['DURATION'] = data
                                        #print("in conn flight")
                        else:
                            print(trip_type)
                            sorted_obj = dict(api_response)
                            print(sorted_obj)
                            sorted_obj['FLIGHTOW'] = sorted(sorted_obj['FLIGHTOW'], key=lambda x: int(x['AMT']), reverse=False)
                            sorted_obj['FLIGHTRT'] = sorted(sorted_obj['FLIGHTRT'], key=lambda x: int(x['AMT']), reverse=False)

                            for dura in sorted_obj['FLIGHTOW']:
                                data1 = dura['DUR'].split(':')
                                if data1[0] == '0d':
                                    data1[0] = ''
                                data = data1[0]+' '+data1[1]+' '+data1[2]
                                dura['DUR'] = data
                                if dura['CON_DETAILS']:
                                    for dura1 in dura['CON_DETAILS']:
                                        data2 = dura1['DURATION'].split(':')
                                        if data2[0] == '0d':
                                            data2[0] = ''
                                        data = data2[0] + ' ' + data2[1] + ' ' + data2[2]
                                        dura1['DURATION'] = data

                            for dura in sorted_obj['FLIGHTRT']:
                                data1 = dura['DUR'].split(':')
                                if data1[0] == '0d':
                                    data1[0] = ''
                                data = data1[0]+' '+data1[1]+' '+data1[2]
                                dura['DUR'] = data
                                if dura['CON_DETAILS']:
                                    for dura1 in dura['CON_DETAILS']:
                                        data2 = dura1['DURATION'].split(':')
                                        if data2[0] == '0d':
                                            data2[0] = ''
                                        data = data2[0] + ' ' + data2[1] + ' ' + data2[2]
                                        dura1['DURATION'] = data

                        data = {'success': 1, 'Data': sorted_obj}
                        return JsonResponse(data)
                    except Exception as e:
                        print(e)
                        data = {'success': 0, 'Data': e}
                        return JsonResponse(data)
                else:
                    data = {'success': 0, 'error': "User Information Not Found"}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'Corporates': "Token Not Found"}
                return JsonResponse(data)
        except Exception as e:
            print("EXCEPTION API")
            data = {'success': 0, 'Data': e}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_flight_fare_search(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        flight_1 = ""
        flight_2 = ""
        trip_string = request.POST.get('trip_string', '')
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
        H_OW = request.POST.get('H_OW', '')
        T_TIME = request.POST.get('T_TIME', '')
        L_RT = request.POST.get('L_RT', '')
        H_RT = request.POST.get('H_RT', '')

        dep_date = request.POST.get('dep_date', '')
        d_date = parse(dep_date).strftime("%Y-%m-%d")

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    url = "http://mdt.ksofttechnology.com/API/AVLT"
                    payload = {
                        "NAME": "FARE_CHECK",
                        "TYPE": "AIR",
                        "STR": [
                            {
                                "FLIGHT" : {
                                    "UID": str(UID),
                                    "ID": str(ID),
                                    "TID": str(TID)
                                },
                                "PARAM": {
                                    "src": str(src),
                                    "des": str(des),
                                    "dep_date": str(d_date),
                                    "ret_date": ""+ret_date,
                                    "adt": ""+adt,
                                    "chd": ""+chd,
                                    "inf": ""+inf,
                                    "L_OW": ""+L_OW,
                                    "H_OW": ""+H_OW,
                                    "T_TIME": ""+T_TIME,
                                    "Trip_String": ""+trip_string
                                },
                                "GSTINFO": {
                                    "Address": "1/1075/1/2 GF 4, Mehrauli, New Delhi 110030",
                                    "Company": "BAI INFOSOLUTIONS PRIVATE LIMITED",
                                    "Email": "vinod@taxivaxi.com",
                                    "Mobile": "11321654654",
                                    "Number": "07AAGCB3556P1Z7",
                                    "Pin": "110030",
                                    "State": "New Delhi",
                                    "Type": "GST Type",
                                    "hasGST": 'true'
                                  }
                            }
                        ],

                    }

                    payload2 = {
                        "NAME": "FARE_CHECK",
                        "TYPE": "AIR",
                        "STR": [
                            {

                                "FLIGHTOW" : {
                                    "UID": str(UID),
                                    "ID": str(ID),
                                    "TID": str(TID)
                                },
                                "FLIGHTRT": {
                                    "UID": str(UID2),
                                    "ID": str(ID2),
                                    "TID": str(TID2)
                                },
                                "PARAM": {
                                    "src": str(src),
                                    "des": str(des),
                                    "dep_date": str(d_date),
                                    "ret_date": ""+ret_date,
                                    "adt": ""+adt,
                                    "chd": ""+chd,
                                    "inf": ""+inf,
                                    "L_OW": ""+L_OW,
                                    "H_OW": ""+H_OW,
                                    "L_RT": ""+L_RT,
                                    "H_RT": ""+H_RT,
                                    "T_TIME": ""+T_TIME,
                                    "Trip_String": ""+trip_string
                                },
                                "GSTINFO": {
                                    "Address": "1/1075/1/2 GF 4, Mehrauli, New Delhi 110030",
                                    "Company": "BAI INFOSOLUTIONS PRIVATE LIMITED",
                                    "Email": "vinod@taxivaxi.com",
                                    "Mobile": "11321654654",
                                    "Number": "07AAGCB3556P1Z7",
                                    "Pin": "110030",
                                    "State": "New Delhi",
                                    "Type": "GST Type",
                                    "hasGST": 'true'
                                  }
                            }
                        ],

                    }
                    #print(payload)
                    #print(payload2)
                    headers = {}
                    r = {}
                    api_response = ''
                    dayHours = ''
                    dayHours_onword = ''
                    dayHours_return = ''
                    DEP_TIME1 = []
                    DEP_DATE1 = []
                    ARRV_TIME1 = []
                    ARRV_DATE1 = []
                    DEP_TIME = []
                    DEP_DATE = []
                    ARRV_TIME = []
                    ARRV_DATE = []
                    if UID2:
                        r = requests.post(url, json=payload2)
                        api_response = r.json()
                        for dura in api_response['FLIGHTRT']:
                            data1 = dura['DURATION'].split(':')
                            if data1[0] == '0d':
                                data1[0] = ''
                            data = data1[0] + ' ' + data1[1] + ' ' + data1[2]
                            dura['DURATION'] = data
                            print(dura)
                            dura['DEP_DATE'] = datetime.strptime(str(dura['DEP_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                            dura['ARRV_DATE'] = datetime.strptime(str(dura['ARRV_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")

                        if api_response['CON_FLIGHTRT']:
                            for dura1 in api_response['CON_FLIGHTRT']:
                                data2 = dura1['DURATION'].split(':')
                                if data2[0] == '0d':
                                    data2[0] = ''
                                data = data2[0] + ' ' + data2[1] + ' ' + data2[2]
                                dura1['DURATION'] = data
                                dura1['DEP_DATE'] = datetime.strptime(str(dura1['DEP_DATE']), "%Y-%m-%d").strftime( "%d-%m-%Y")
                                dura1['ARRV_DATE'] = datetime.strptime(str(dura1['ARRV_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                                DEP_TIME.append(dura1['DEP_TIME'])
                                DEP_DATE.append(dura1['DEP_DATE'])
                                ARRV_TIME.append(dura1['ARRV_TIME'])
                                ARRV_DATE.append(dura1['ARRV_DATE'])

                        for dura in api_response['FLIGHTOW']:
                            data1 = dura['DURATION'].split(':')
                            if data1[0] == '0d':
                                data1[0] = ''
                            data = data1[0] + ' ' + data1[1] + ' ' + data1[2]
                            dura['DURATION'] = data
                            dura['DEP_DATE'] = datetime.strptime(str(dura['DEP_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                            dura['ARRV_DATE'] = datetime.strptime(str(dura['ARRV_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")

                        if api_response['CON_FLIGHTOW']:
                            for dura1 in api_response['CON_FLIGHTOW']:
                                data2 = dura1['DURATION'].split(':')
                                if data2[0] == '0d':
                                    data2[0] = ''
                                data = data2[0] + ' ' + data2[1] + ' ' + data2[2]
                                dura1['DURATION'] = data
                                dura1['DEP_DATE'] = datetime.strptime(str(dura1['DEP_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                                dura1['ARRV_DATE'] = datetime.strptime(str(dura1['ARRV_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                                DEP_TIME1.append(dura1['DEP_TIME'])
                                DEP_DATE1.append(dura1['DEP_DATE'])
                                ARRV_TIME1.append(dura1['ARRV_TIME'])
                                ARRV_DATE1.append(dura1['ARRV_DATE'])
                        print(DEP_DATE)
                        print(DEP_DATE1)
                        if DEP_DATE1:
                            adDate = datetime.strptime(str(DEP_DATE1[-1] + ' ' + DEP_TIME1[-1]), "%d-%m-%Y %H:%M")
                            ddDate = datetime.strptime(str(ARRV_DATE1[0] + ' ' + ARRV_TIME1[0]), "%d-%m-%Y %H:%M")
                            diff = ddDate - adDate
                            print(diff)
                            dayHours_onword = timesince(ddDate, adDate)
                        if DEP_DATE:
                            adDate = datetime.strptime(str(DEP_DATE[-1] + ' ' + DEP_TIME[-1]), "%d-%m-%Y %H:%M")
                            ddDate = datetime.strptime(str(ARRV_DATE[0] + ' ' + ARRV_TIME[0]), "%d-%m-%Y %H:%M")
                            diff = ddDate - adDate
                            print(diff)
                            dayHours_return = timesince(ddDate, adDate)
                            print("DAY DILLGLDLGDGDGDLG")
                            print(dayHours_return)

                    else:
                        r = requests.post(url, json=payload)
                        print(r)
                        api_response = r.json()
                        #print(api_response)
                        try:
                            for dura in api_response['FLIGHT']:
                                data1 = dura['DURATION'].split(':')
                                if data1[0] == '0d':
                                    data1[0] = ''
                                data = data1[0] + ' ' + data1[1] + ' ' + data1[2]
                                dura['DURATION'] = data
                                dura['DEP_DATE'] = datetime.strptime(str(dura['DEP_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                                dura['ARRV_DATE'] = datetime.strptime(str(dura['ARRV_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                            if api_response['CON_FLIGHT']:
                                DEP_TIME = []
                                DEP_DATE = []
                                ARRV_TIME = []
                                ARRV_DATE = []
                                for dura1 in api_response['CON_FLIGHT']:
                                    data2 = dura1['DURATION'].split(':')
                                    if data2[0] == '0d':
                                        data2[0] = ''
                                    data = data2[0] + ' ' + data2[1] + ' ' + data2[2]
                                    dura1['DURATION'] = data
                                    dura1['DEP_DATE'] = datetime.strptime(str(dura1['DEP_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                                    dura1['ARRV_DATE'] = datetime.strptime(str(dura1['ARRV_DATE']), "%Y-%m-%d").strftime("%d-%m-%Y")
                                    DEP_TIME.append(dura1['DEP_TIME'])
                                    DEP_DATE.append(dura1['DEP_DATE'])
                                    ARRV_TIME.append(dura1['ARRV_TIME'])
                                    ARRV_DATE.append(dura1['ARRV_DATE'])

                            adDate = datetime.strptime(str(DEP_DATE[-1]+' '+DEP_TIME[-1]), "%d-%m-%Y %H:%M")
                            ddDate = datetime.strptime(str(ARRV_DATE[0]+' '+ARRV_TIME[0]), "%d-%m-%Y %H:%M")
                            diff = ddDate - adDate
                            print(diff)
                            dayHours_onword = timesince(ddDate, adDate)
                            print("DAY DILLGLDLGDGDGDLG")
                            print(dayHours_onword)

                        except Exception as e:
                            print("exception")
                            print(e)

                    print("API TYPE")
                    #print(type(api_response))
                    data = {'success': 1, 'Data': api_response, 'dayHours_onword':str(dayHours_onword), 'dayHours_return':str(dayHours_return)}
                    #print(data)
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'Data': ''}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def save_flight_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        flightdata = request.POST.get('flightdata', '')
        print("SAVER DATAF TYpe")
        print(type(flightdata))
        UID2 = request.POST.get('UID2', '')
        is_mobile = request.POST.get('is_mobile', '')

        employees_name = request.POST.getlist('employee_name_1', '')
        flight_class_is_international = request.POST.get('flight_class_is_international', '')
        emp_info_international = request.POST.get('emp_info_international', '')
        print("SAVER DATAF TYpe")
        print(type(emp_info_international))
        print(emp_info_international)
        if is_mobile:
            print("type of ini_object", type(emp_info_international))
            emp_info_international = json.loads(emp_info_international, strict=False)
            if flight_class_is_international == 'I':
                p_date = ''
                d_date = ''
                for emp_data in emp_info_international:
                    if emp_data['emp_dob']:
                        d_date = parse(emp_data['emp_dob']).strftime("%d-%m-%Y")
                    else:
                        d_date = ''
                    if emp_data['emp_passport_exp']:
                        p_date = parse(emp_data['emp_passport_exp']).strftime("%d-%m-%Y")
                    else:
                        p_date = ''
                    cursor = connection.cursor()
                    d_date = parse(emp_data['emp_dob']).strftime("%d-%m-%Y")
                    cursor.callproc('updateAddEmployeePassportDetails', [emp_data['emp_id'], emp_data['emp_title'], emp_data['emp_fname'], emp_data['emp_lname'],
                        d_date, emp_data['emp_passport_no'], emp_data['emp_passport_exp'], emp_data['emp_nationality']])
                    emp = dictfetchall(cursor)
                    print(emp)
                    cursor.close()

        else:
            emp_info_international = eval(emp_info_international)
            if flight_class_is_international == 'I':
                p_date= ''
                d_date= ''
                for emp_data in emp_info_international:
                    cursor = connection.cursor()
                    if emp_data['emp_dob']:
                        d_date = parse(emp_data['emp_dob']).strftime("%d-%m-%Y")
                    else:
                        d_date = ''
                    if emp_data['emp_passport_exp']:
                        p_date = parse(emp_data['emp_passport_exp']).strftime("%d-%m-%Y")
                    else:
                        p_date = ''
                    cursor.callproc('updateAddEmployeePassportDetails', [emp_data['emp_id'], emp_data['emp_title'], emp_data['emp_fname'], emp_data['emp_lname'],
                        d_date, emp_data['emp_passport_no'], p_date, emp_data['emp_nationality']])
                    emp = dictfetchall(cursor)
                    print(emp)
                    cursor.close()
        print("SAVER DATAF TYpe")
        print(type(emp_info_international))
        dict = []  # create an empty array
        if flight_class_is_international == 'I':
            for emp_data in emp_info_international:
                dict.append({
                    "apnr": "",
                    "baggage": "",
                    "dob": emp_data['emp_dob'],
                    "fare": "",
                    "ffn": "",
                    "fn": emp_data['emp_fname'],
                    "gpnr": "",
                    "ln": emp_data['emp_lname'],
                    "meal": "",
                    "mn": "",
                    "other_info": "",
                    "pi": "",
                    "refundable": "",
                    "status": "",
                    "tc": "",
                    "tktno": "",
                    "ttl": emp_data['emp_title'],
                    "type": "adult",
                    "year": "",
                    "nat": emp_data['emp_nationality'],
                    "pn": emp_data['emp_passport_no'],
                    "ed": emp_data['emp_passport_exp'],
                })
        else:
            for emp_data in emp_info_international:
                dict.append({
                    "apnr": "",
                    "baggage": "",
                    "dob": emp_data['emp_dob'],
                    "fare": "",
                    "ffn": "",
                    "fn": emp_data['emp_fname'],
                    "gpnr": "",
                    "ln": emp_data['emp_lname'],
                    "meal": "",
                    "mn": "",
                    "nat": "",
                    "other_info": "",
                    "pi": "",
                    "refundable": "",
                    "status": "",
                    "tc": "",
                    "tktno": "",
                    "ttl": emp_data['emp_title'],
                    "type": "adult",
                    "year": ""
                })

        user = {}
        payload = {}
        payload2 = {}

        r = ""
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    if is_mobile:
                        print("type of ini_object", type(flightdata))
                        flightdata = json.loads(flightdata, strict=False) 
                    else:
                        flightdata = eval(flightdata)

                    va = flightdata
                    url = "http://mdt.ksofttechnology.com/API/flight"

                    if UID2:
                        for dura in va['FLIGHTRT']:
                            data1 = dura['DURATION'].split(' ')
                            data = ''
                            find_len = len(data1)
                            if find_len == '3':
                                data = data1[0] + ':' + data1[1] + ':' + data1[2]
                            else:
                                data = '0d:' + data1[1] + ':' + data1[2]
                            dura['DURATION'] = data
                            dura['DEP_DATE'] = datetime.strptime(str(dura['DEP_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                            dura['ARRV_DATE'] = datetime.strptime(str(dura['ARRV_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")

                        if va['CON_FLIGHTRT']:
                            for dura1 in va['CON_FLIGHTRT']:
                                data2 = dura1['DURATION'].split(' ')
                                data = ''
                                find_len = len(data2)
                                if find_len == '3':
                                    data = data2[0] + ':' + data2[1] + ':' + data2[2]
                                else:
                                    data = '0d:' + data1[1] + ':' + data1[2]
                                dura1['DURATION'] = data
                                dura1['DEP_DATE'] = datetime.strptime(str(dura1['DEP_DATE']), "%d-%m-%Y").strftime( "%Y-%m-%d")
                                dura1['ARRV_DATE'] = datetime.strptime(str(dura1['ARRV_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")

                        for dura in va['FLIGHTOW']:
                            data1 = dura['DURATION'].split(' ')
                            data = ''
                            find_len = len(data1)
                            if find_len == '3':
                                data = data1[0] + ':' + data1[1] + ':' + data1[2]
                            else:
                                data = '0d:' + data1[1] + ':' + data1[2]
                            dura['DURATION'] = data
                            dura['DEP_DATE'] = datetime.strptime(str(dura['DEP_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                            dura['ARRV_DATE'] = datetime.strptime(str(dura['ARRV_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")

                        if va['CON_FLIGHTOW']:
                            for dura1 in va['CON_FLIGHTOW']:
                                data2 = dura1['DURATION'].split(' ')
                                find_len = len(data2)
                                if find_len == '3':
                                    data = data2[0] + ':' + data2[1] + ':' + data2[2]
                                else:
                                    data = '0d:' + data1[1] + ':' + data1[2]
                                dura1['DURATION'] = data
                                dura1['DEP_DATE'] = datetime.strptime(str(dura1['DEP_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                                dura1['ARRV_DATE'] = datetime.strptime(str(dura1['ARRV_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                                
                        if flight_class_is_international == 'I':
                            payload2 = {
                                "PARAM": va['PARAM'],
                                "STATUS": va['STATUS'],
                                "FLIGHTOW": va['FLIGHTOW'],
                                "CON_FLIGHTOW": va['CON_FLIGHTOW'],
                                "FARE": va['FARE'],
                                "FLIGHTRT": va['FLIGHTRT'],
                                "CON_FLIGHTRT": va['CON_FLIGHTRT'],
                                "Deal": va['Deal'],
                                "FARE_RULE": va['FARE_RULE'],
                                "PAX": dict,
                                "TYPE": "DC",
                                "NAME": "PNR_CREATION",
                                "Others": [
                                    {
                                        "REMARK": "79394396",
                                        "CUSTOMER_EMAIL": "balwant@taxivaxi.in",
                                        "CUSTOMER_MOBILE": "8669152900"
                                    }
                                ]
                            }
                        else:
                            payload2 = {
                                "PARAM": va['PARAM'],
                                "STATUSOW": va['STATUSOW'],
                                "FLIGHTOW": va['FLIGHTOW'],
                                "CON_FLIGHTOW": va['CON_FLIGHTOW'],
                                "FAREOW": va['FAREOW'],
                                "PARAMOW": va['PARAMOW'],
                                "STATUSRT": va['STATUSRT'],
                                "FLIGHTRT": va['FLIGHTRT'],
                                "CON_FLIGHTRT": va['CON_FLIGHTRT'],
                                "FARERT": va['FARERT'],
                                "PARAMRT": va['PARAMRT'],
                                "Deal": va['Deal'],
                                "FARE_RULE": va['FARE_RULE'],
                                "PAX": dict,
                                "TYPE": "DC",
                                "NAME": "PNR_CREATION",
                                "Others": [
                                    {
                                        "REMARK": "79394396",
                                        "CUSTOMER_EMAIL": "balwant@taxivaxi.in",
                                        "CUSTOMER_MOBILE": "8669152900"
                                    }
                                ]
                            }
                    else:
                        print("i m herer first")
                        print(type(va))
                        for dura in va['FLIGHT']:
                            print(dura['DURATION'])
                            data1 = dura['DURATION'].split(' ')
                            data = ''
                            print(len(data1))
                            print(data1)
                            find_len = len(data1)
                            if find_len == '3':
                                data = data1[0]+':' + data1[1] + ':' + data1[2]
                            else:
                                data = '0d:' + data1[1] + ':' + data1[1]
                            print("FLIGHT DURATION")
                            print(data)
                            dura['DURATION'] = data
                            dura['DEP_DATE'] = datetime.strptime(str(dura['DEP_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                            dura['ARRV_DATE'] = datetime.strptime(str(dura['ARRV_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                            print("i m herer")
                        if va['CON_FLIGHT']:
                            for dura1 in va['CON_FLIGHT']:
                                data1 = dura1['DURATION'].split(' ')
                                data = ''
                                print(len(data1))
                                print(data1)
                                find_len = len(data1)
                                if find_len == '3':
                                    data = data1[0] + ':' + data1[1] + ':' + data1[2]
                                else:
                                    data = '0d:' + data1[1] + ':' + data1[2]
                                print("FLIGHT DURATION CON")
                                print(data)
                                dura1['DURATION'] = data
                                dura1['DEP_DATE'] = datetime.strptime(str(dura1['DEP_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                                dura1['ARRV_DATE'] = datetime.strptime(str(dura1['ARRV_DATE']), "%d-%m-%Y").strftime("%Y-%m-%d")
                                print("i m herer11")
                        payload = {
                            "STATUS": va['STATUS'],
                            "FLIGHT": va['FLIGHT'],
                            "CON_FLIGHT": va['CON_FLIGHT'],
                            "FARE": va['FARE'],
                            "PARAM": va['PARAM'],
                            "GSTINFO": va['GSTINFO'],
                            "Deal": va['Deal'],
                            "FARE_RULE": va['FARE_RULE'],
                            "PAX": dict,
                            "TYPE": "DC",
                            "NAME": "PNR_CREATION",
                            "Others": [
                                {
                                    "REMARK": "79394396",
                                    "CUSTOMER_EMAIL": "balwant@taxivaxi.in",
                                    "CUSTOMER_MOBILE": "8669152900"
                                }
                            ]
                        }
                    headers = {}
                    if UID2:
                        print(payload)
                        r = requests.post(url, json=payload2)
                    else:
                        print(payload)
                        r = requests.post(url, json=payload)
                    api_response = r.json()
                    data = {'success': 1, 'Data':api_response}
                    return JsonResponse(data)
                except Exception as e:
                    print("in EXCEPTION sss")
                    print(e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    data = {'success': 0, 'Data': ""}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_flight_pnr_details(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        pnr = request.POST.get('pnr', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    client_session = user_token[1]
                    CLIENT_SESSIONID =  client_session[0:40]
                    url = "http://mdt.ksofttechnology.com/API/flight"
                    payload = {
                            "NAME": "PNR_RETRIVE",
                            "TYPE": "DC",
                            "STR": [
                                {
                                    "BOOKINGID": ""+pnr,
                                    "CLIENT_SESSIONID": "XKWP9TWKSDJ4PAKXKUHE1WM72GTBPO13FTUGF454CIGLQYM6F9",
                                    "HS": "D",
                                    "MODULE": "B2B",
                                }
                            ],
                    }

                    headers = {}
                    #print(payload)
                    r = requests.post(url, json=payload)
                    api_response = r.json()
                    #print(api_response)
                    data = {'success': 1, 'Data': api_response}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'Data': ""}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_flight_booking_with_invoice(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        flightdata = request.POST.get('flightdata', '')
        UID2 = request.POST.get('UID2', '')

        user_id = request.POST.get('spoc_id', '')
        corporate_id = request.POST.get('corporate_id', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        billing_entity_id = request.POST.get('entity_id', '')
        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')
        flight_type = request.POST.get('flight_class', '')

        kafila_booking_id = request.POST.get('kafila_booking_id', '')
        timezone.activate(pytz.timezone("Asia/Kolkata"))
        booking_datetime = timezone.localtime(timezone.now())

        is_email = 1
        is_sms = 1
        client_ticket =""

        if billing_entity_id:
            pass
        else:
            billing_entity_id = 0

        employees = []
        employees_name = []
        no_of_emp = int(no_of_seats) + 1
        for i in range(1, no_of_emp):
            employees.append(request.POST.get('employee_id_' + str(i), ''))
            employees_name.append(request.POST.get('employee_name_' + str(i), ''))
            print(employees)
        print("employee ...")
        print(employees)
        print(employees_name)

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    client_session = user_token[1]
                    CLIENT_SESSIONID =  client_session[0:40]
                    url = "http://mdt.ksofttechnology.com/API/flight"
                    payload = {
                            "NAME": "PNR_RETRIVE",
                            "TYPE": "DC",
                            "STR": [
                                {
                                    "BOOKINGID": ""+kafila_booking_id,
                                    "CLIENT_SESSIONID": "XKWP9TWKSDJ4PAKXKUHE1WM72GTBPO13FTUGF454CIGLQYM6F9",
                                    "HS": "D",
                                    "MODULE": "B2B",
                                }
                            ],
                    }

                    headers = {}
                    #print(payload)
                    r = requests.post(url, json=payload)
                    booking1 = r.json()

                    print(booking1)
                    if UID2:
                        if not ('FLIGHTOW' in booking1):
                            data = {'success': 0, 'error': "Pnr Not Generated"}
                            return JsonResponse(data)
                    else:
                        if not ('FLIGHT' in booking1 or 'FLIGHTOW' in booking1):
                            data = {'success': 0, 'error': "Pnr Not Generated"}
                            return JsonResponse(data)

                    ticket_number = []
                    pnr_no = []
                    flight_no = []
                    flight_name = []
                    arrival_time = []
                    departure_time = []
                    flight_to = []
                    flight_from = []
                    is_return_flight = []
                    flight_type = flight_type
                    journey_type = ""
                    from_location =""
                    to_location = ""

                    departure_datetime =""
                    preferred_flight =""
                    booking_email = ""
                    meal_is_include = ''
                    last_booking_id = 0

                    if UID2:
                        print("in trip two")
                        print(UID2)
                        no_of_stops = booking1['FLIGHTOW'][0]['STOP']
                        flight_type = flight_type
                        fare_type = booking1['FLIGHTOW'][0]['FARE_TYPE']
                        meal_is_include = ''
                        no_of_passanger = booking1['PARAM'][0]['adt']
                        employee_booking_id = employees
                        ticket_price = booking1['FLIGHTOW'][0]['AMOUNT']
                        journey_type = "Round Trip"
                        from_location = booking1['FLIGHTOW'][0]['DES_NAME']
                        to_location = booking1['FLIGHTOW'][0]['ORG_NAME']
                        departure_datetime = datetime.strptime(booking1['FLIGHTOW'][0]['DEP_DATE'] + " " + booking1['FLIGHTOW'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")

                        if booking1['CON_FLIGHTOW']:
                            for flightt in booking1['CON_FLIGHTOW']:
                                ticket_number.append(booking1['FLIGHTOW'][0]['PCC'])
                                pnr_no.append(booking1['PAXOW'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(
                                    flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(
                                    flightt['DEP_DATE'] + " " + flightt['DEP_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('0')
                        else:
                            ticket_number.append(booking1['FLIGHTOW'][0]['PCC'])
                            pnr_no.append(booking1['PAXOW'][0]['apnr'])
                            flight_no.append(booking1['FLIGHTOW'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['FLIGHTOW'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(
                                booking1['FLIGHTOW'][0]['ARRV_DATE'] + " " +
                                booking1['FLIGHTOW'][0][
                                    'ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(
                                booking1['FLIGHTOW'][0]['DEP_DATE'] + " " + booking1['FLIGHTOW'][0][
                                    'DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['FLIGHTOW'][0]['DES_NAME'])
                            flight_from.append(booking1['FLIGHTOW'][0]['ORG_NAME'])
                            is_return_flight.append('0')

                        if booking1['CON_FLIGHTRT']:
                            for flightt in booking1['CON_FLIGHTRT']:
                                ticket_number.append(booking1['FLIGHTRT'][0]['PCC'])
                                pnr_no.append(booking1['PAXRT'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(
                                    flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(
                                    flightt['DEP_DATE'] + " " + flightt['DEP_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('1')
                        else:
                            ticket_number.append(booking1['FLIGHTRT'][0]['PCC'])
                            pnr_no.append(booking1['PAXRT'][0]['apnr'])
                            flight_no.append(booking1['FLIGHTRT'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['FLIGHTRT'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(
                                booking1['FLIGHTRT'][0]['ARRV_DATE'] + " " +
                                booking1['FLIGHTRT'][0][
                                    'ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(
                                booking1['FLIGHTRT'][0]['DEP_DATE'] + " " + booking1['FLIGHTRT'][0][
                                    'DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['FLIGHTRT'][0]['DES_NAME'])
                            flight_from.append(booking1['FLIGHTRT'][0]['ORG_NAME'])
                            is_return_flight.append('1')

                            print("INNNNNNNNNNNN ELSEEEEEEEEEEEEEEEE")


                    else:
                        print("in trip one")
                        print(UID2)
                        no_of_stops = booking1['FLIGHT'][0]['STOP']
                        flight_type = flight_type
                        fare_type = booking1['FLIGHT'][0]['FARE_TYPE']
                        meal_is_include = ''
                        no_of_passanger = booking1['FLIGHT'][0]['SEAT']
                        employee_booking_id = employees
                        ticket_price = booking1['FLIGHT'][0]['AMOUNT']
                        journey_type = "One Way"
                        from_location = booking1['FLIGHT'][0]['DES_NAME']
                        to_location = booking1['FLIGHT'][0]['ORG_NAME']
                        departure_datetime = datetime.strptime(booking1['FLIGHT'][0]['DEP_DATE'] + " " + booking1['FLIGHT'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")

                        if booking1['CON_FLIGHT']:
                            for flightt in booking1['CON_FLIGHT']:
                                ticket_number.append(booking1['FLIGHT'][0]['PCC'])
                                pnr_no.append(booking1['PAX'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(
                                    flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(
                                    flightt['DEP_DATE'] + " " + flightt['DEP_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('0')
                            print("INNNNNNNNNNNN IFFFFFFFFFFFFF")
                        else:
                            ticket_number.append(booking1['FLIGHT'][0]['PCC'])
                            pnr_no.append(booking1['PAX'][0]['apnr'])
                            flight_no.append(booking1['FLIGHT'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['FLIGHT'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(booking1['FLIGHT'][0]['ARRV_DATE'] + " " + booking1['FLIGHT'][0]['ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(booking1['FLIGHT'][0]['DEP_DATE'] + " " + booking1['FLIGHT'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['FLIGHT'][0]['DES_NAME'])
                            flight_from.append(booking1['FLIGHT'][0]['ORG_NAME'])
                            is_return_flight.append('0')
                            print("INNNNNNNNNNNN ELSEEEEEEEEEEEEEEEE")

                    cursor = connection.cursor()
                    print(employees)
                    try:
                        employees = ",".join(employees)
                        cursor.callproc('addFlightBooking',
                                        ["Flight", journey_type, flight_type, from_location, to_location,
                                         booking_datetime, departure_datetime,
                                         preferred_flight, assessment_code, no_of_seats,
                                         group_id, subgroup_id, spoc_id, corporate_id, billing_entity_id,
                                         reason_booking, user_id, user_type, employees, booking_email,
                                         assessment_city_id, '@last_booking_id',kafila_booking_id])
                        booking_id = dictfetchall(cursor)

                        if booking_id:
                            data = {'success': 0, 'message': booking_id}
                        else:
                            cursor.execute("SELECT @last_booking_id")
                            last_booking_id = cursor.fetchone()[0]
                            print("booking id")
                            print(last_booking_id)
                            cursor.close()
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
                            cursor3.callproc('getAllApproverByBookingID', [last_booking_id, 5])
                            approvers = dictfetchall(cursor3)
                            cursor3.close()

                            cursor4 = connection.cursor()
                            cursor4.callproc('assignFlightBooking',
                                            [flight_type, flight_type, journey_type, no_of_stops, last_booking_id,
                                             meal_is_include, fare_type, user_id, user_type, ticket_price,100, 18,
                                             18, 118, 1,18, 0, 0, 18, 0,0, 18,0, 0, 0,ticket_price, 0, 1,1, 18, 9, 9,"", "", 0, 0,0, 1, 1])
                            result = dictfetchall(cursor4)

                            cursor4.close()
                            no_of_stops = int(no_of_stops)
                            print("no of stops")
                            print(no_of_stops)
                            if UID2:
                                final_stop = no_of_stops + 2
                            else:
                                final_stop = no_of_stops+1
                            for x in range(final_stop):
                                cursor5 = connection.cursor()
                                cursor5.callproc('addFlightBookingFlights',
                                                 [flight_name[x], flight_no[x], pnr_no[x], flight_from[x],
                                                  flight_to[x], departure_time[x], arrival_time[x], last_booking_id,
                                                  user_id, user_type, is_return_flight[x]])
                                result = dictfetchall(cursor5)
                                print("addFlightBookingFloght")
                                print(result)
                                cursor5.close()

                            # for xx in range(int(no_of_seats)):
                            #     cursor26 = connection.cursor()
                            #     cursor26.callproc('updateFlightPassangerTickectNo',
                            #                      [ticket_number[xx], employee_booking_id[xx], last_booking_id])
                            #     result = dictfetchall(cursor26)
                            #     print("addFlightBookingticket")
                            #     print(result)
                            #     cursor26.close()

                            company = dictfetchall(cursor)
                            print(company)
                            if company:
                                data = {'success': 0, 'message': company}
                            else:
                                print("Last Booking ID")
                                cursor27 = connection.cursor()
                                cursor27.callproc('viewFlightBooking', [last_booking_id])
                                emp = dictfetchall(cursor27)
                                cursor27.close()

                                cursor11 = connection.cursor()
                                cursor11.callproc('getAllFlightBookingPassangers', [last_booking_id])
                                passanger = dictfetchall(cursor11)
                                emp[0]['Passangers'] = passanger
                                cursor11.close()

                                cursor22 = connection.cursor()
                                cursor22.callproc('getAllFlightBookingFlights', [last_booking_id])
                                flights = dictfetchall(cursor22)
                                cursor22.close()

                                emp[0]['Flights'] = flights

                                get_voucher_path = ''
                                if client_ticket:
                                    voucher = emp[0]
                                    bus_pdf = Flight(voucher)
                                    get_vou = bus_pdf.get(request)
                                    get_voucher_path = get_vou[1]
                                else:
                                    get_voucher_path = ""

                                add_booking_email = AddBooking_Email()
                                if is_email == '1':
                                    thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Flight"))
                                    thread.start()
                                    #resp6 = add_booking_email.send_taxi_email(emp, approvers, "Flight")
                                if is_sms == '1':
                                    thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Flight"))
                                    thread.start()
                                    #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Flight")

                                add_booking_email = Assign_Booking_Email()
                                if is_sms:
                                    thread = Thread(target=add_booking_email.send_client_sms, args=(emp, "Flight"))
                                    thread.start()
                                    #resp1 = add_booking_email.send_client_sms(emp, "Flight")
                                if is_email:
                                    thread = Thread(target=add_booking_email.is_client_email, args=(emp, "Flight", get_voucher_path))
                                    thread.start()
                                    #resp1 = add_booking_email.is_client_email(emp, "Flight", get_voucher_path)

                        cursor.close()
                        data = {'success': 1, 'message': "Insert Success", 'last_booking_id': last_booking_id}
                        return JsonResponse(data)

                    except Exception as e:
                        print(e)
                        data = {'success': 0, 'message': "Error in Data Insert"}
                        return JsonResponse(data)

                except Exception as e:
                    print("EXCEPTIONSNSNSNSN")
                    print(e)
                    data = {'success': 0, 'Data': "Exception"}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_phr_detail_assign_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        booking_id_from_post = request.POST.get('booking_id', '')
        kafila_booking_id = request.POST.get('api_bookigid', '')
        journey_type = request.POST.get('journey_type', '')
        user_id = request.POST.get('user_id', '')


        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    client_session = user_token[1]
                    CLIENT_SESSIONID =  client_session[0:40]
                    url = "http://mdt.ksofttechnology.com/API/flight"
                    payload = {
                            "NAME": "PNR_RETRIVE",
                            "TYPE": "DC",
                            "STR": [
                                {
                                    "BOOKINGID": ""+kafila_booking_id,
                                    "CLIENT_SESSIONID": "XKWP9TWKSDJ4PAKXKUHE1WM72GTBPO13FTUGF454CIGLQYM6F9",
                                    "HS": "D",
                                    "MODULE": "B2B",
                                }
                            ],
                    }

                    headers = {}
                    #print(payload)
                    r = requests.post(url, json=payload)
                    booking1 = r.json()
                    print("BOOKING DETAILS")
                    print(booking1)
                    if not ('FLIGHT' in booking1 or 'FLIGHTOW' in booking1):
                            data = {'success': 0, 'message': "Pnr Not Generated"}
                            return JsonResponse(data)

                    ticket_number = []
                    pnr_no = []
                    flight_no = []
                    flight_name = []
                    arrival_time = []
                    departure_time = []
                    flight_to = []
                    flight_from = []
                    is_return_flight = []
                    flight_type = ""
                    from_location =""
                    to_location = ""

                    departure_datetime =""
                    preferred_flight =""
                    booking_email = ""
                    meal_is_include = ''
                    last_booking_id = 0

                    print("PNEEEEEEEEEEEEEEEEEEEEEEETRRRRRRRRRRRRRRRRRRRRRRRRRR")

                    if journey_type == 'Round Trip':
                        print("in trip two")
                        print(journey_type)
                        no_of_stops = booking1['FLIGHTOW'][0]['STOP']
                        flight_type = flight_type
                        fare_type = booking1['FLIGHTOW'][0]['FARE_TYPE']
                        meal_is_include = ''
                        no_of_passanger = booking1['PARAM'][0]['adt']
                        ticket_price = booking1['FLIGHTOW'][0]['AMOUNT']
                        journey_type = "Round Trip"
                        from_location = booking1['FLIGHTOW'][0]['DES_NAME']
                        to_location = booking1['FLIGHTOW'][0]['ORG_NAME']
                        departure_datetime = datetime.strptime(booking1['FLIGHTOW'][0]['DEP_DATE'] + " " + booking1['FLIGHTOW'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                        if not booking1['PAXOW'][0]['apnr']:
                            data = {'success': 0, 'message': "Pnr Not Generated"}
                            return JsonResponse(data)
                        if booking1['CON_FLIGHTOW']:
                            for flightt in booking1['CON_FLIGHTOW']:
                                ticket_number.append(booking1['FLIGHTOW'][0]['PCC'])
                                pnr_no.append(booking1['PAXOW'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(
                                    flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(
                                    flightt['DEP_DATE'] + " " + flightt['DEP_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('0')
                        else:
                            ticket_number.append(booking1['FLIGHTOW'][0]['PCC'])
                            pnr_no.append(booking1['PAXOW'][0]['apnr'])
                            flight_no.append(booking1['FLIGHTOW'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['FLIGHTOW'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(
                                booking1['FLIGHTOW'][0]['ARRV_DATE'] + " " +
                                booking1['FLIGHTOW'][0][
                                    'ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(
                                booking1['FLIGHTOW'][0]['DEP_DATE'] + " " + booking1['FLIGHTOW'][0][
                                    'DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['FLIGHTOW'][0]['DES_NAME'])
                            flight_from.append(booking1['FLIGHTOW'][0]['ORG_NAME'])
                            is_return_flight.append('0')

                        if booking1['CON_FLIGHTRT']:
                            for flightt in booking1['CON_FLIGHTRT']:
                                ticket_number.append(booking1['FLIGHTRT'][0]['PCC'])
                                pnr_no.append(booking1['PAXRT'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(
                                    flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(
                                    flightt['DEP_DATE'] + " " + flightt['DEP_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('1')
                        else:
                            ticket_number.append(booking1['FLIGHTRT'][0]['PCC'])
                            pnr_no.append(booking1['PAXRT'][0]['apnr'])
                            flight_no.append(booking1['FLIGHTRT'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['FLIGHTRT'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(
                                booking1['FLIGHTRT'][0]['ARRV_DATE'] + " " +
                                booking1['FLIGHTRT'][0][
                                    'ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(
                                booking1['FLIGHTRT'][0]['DEP_DATE'] + " " + booking1['FLIGHTRT'][0][
                                    'DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['FLIGHTRT'][0]['DES_NAME'])
                            flight_from.append(booking1['FLIGHTRT'][0]['ORG_NAME'])
                            is_return_flight.append('1')

                            print("INNNNNNNNNNNN ELSEEEEEEEEEEEEEEEE")
                    else:
                        print("in trip one")
                        no_of_stops = booking1['FLIGHT'][0]['STOP']
                        flight_type = flight_type
                        fare_type = booking1['FLIGHT'][0]['FARE_TYPE']
                        meal_is_include = ''
                        no_of_passanger = booking1['PARAM'][0]['adt']
                        ticket_price = booking1['FLIGHT'][0]['AMOUNT']
                        journey_type = "One Way"
                        from_location = booking1['FLIGHT'][0]['DES_NAME']
                        to_location = booking1['FLIGHT'][0]['ORG_NAME']
                        departure_datetime = datetime.strptime(booking1['FLIGHT'][0]['DEP_DATE'] + " " + booking1['FLIGHT'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")

                        if not booking1['PAX'][0]['apnr']:
                            data = {'success': 0, 'message': "Pnr Not Generated"}
                            return JsonResponse(data)
                        
                        if booking1['CON_FLIGHT']:
                            for flightt in booking1['CON_FLIGHT']:
                                ticket_number.append(booking1['FLIGHT'][0]['PCC'])
                                pnr_no.append(booking1['PAX'][0]['apnr'])
                                flight_no.append(flightt['FLIGHT_NO'])
                                flight_name.append(flightt['FLIGHT_NAME'])
                                arrival_time1 = datetime.strptime(
                                    flightt['ARRV_DATE'] + " " + flightt['ARRV_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                arrival_time.append(arrival_time1)
                                arrival_time2 = datetime.strptime(
                                    flightt['DEP_DATE'] + " " + flightt['DEP_TIME'] + ":00",
                                    "%Y-%m-%d %H:%M:%S")
                                departure_time.append(arrival_time2)
                                flight_to.append(flightt['DES_NAME'])
                                flight_from.append(flightt['ORG_NAME'])
                                is_return_flight.append('0')
                            print("INNNNNNNNNNNN IFFFFFFFFFFFFF")
                        else:
                            ticket_number.append(booking1['FLIGHT'][0]['PCC'])
                            pnr_no.append(booking1['PAX'][0]['apnr'])
                            flight_no.append(booking1['FLIGHT'][0]['FLIGHT_NO'])
                            flight_name.append(booking1['FLIGHT'][0]['FLIGHT_NAME'])
                            arrival_time1 = datetime.strptime(booking1['FLIGHT'][0]['ARRV_DATE'] + " " + booking1['FLIGHT'][0]['ARRV_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            arrival_time.append(arrival_time1)
                            arrival_time2 = datetime.strptime(booking1['FLIGHT'][0]['DEP_DATE'] + " " + booking1['FLIGHT'][0]['DEP_TIME'] + ":00", "%Y-%m-%d %H:%M:%S")
                            departure_time.append(arrival_time2)
                            flight_to.append(booking1['FLIGHT'][0]['DES_NAME'])
                            flight_from.append(booking1['FLIGHT'][0]['ORG_NAME'])
                            is_return_flight.append('0')
                            print("INNNNNNNNNNNN ELSEEEEEEEEEEEEEEEE")

                    try:
                        booking_id = ""

                        if booking_id:
                            data = {'success': 0, 'message': booking_id}
                        else:
                            print(booking_id_from_post)
                            last_booking_id = booking_id_from_post

                            cursor2 = connection.cursor()
                            cursor2.callproc('viewFlightBooking', [last_booking_id])
                            emp = dictfetchall(cursor2)
                            cursor2.close()

                            cursor1 = connection.cursor()
                            cursor1.callproc('getAllFlightBookingPassangers', [last_booking_id])
                            passanger = dictfetchall(cursor1)
                            emp[0]['Passangers'] = passanger
                            cursor1.close()
                            print(emp)
                            cursor3 = connection.cursor()
                            cursor3.callproc('getAllApproverByBookingID', [last_booking_id,5])
                            approvers = dictfetchall(cursor3)
                            cursor3.close()

                            cursor4 = connection.cursor()
                            cursor4.callproc('assignFlightBooking',
                                            [flight_type, flight_type, journey_type, no_of_stops, last_booking_id,
                                             meal_is_include, fare_type, user_id, user_type, ticket_price,100, 18,
                                             18, 118, 1,18, 0, 0, 18, 0,0, 18,0, 0, 0,ticket_price, 0, 1,1, 18, 9, 9,"", "", 0, 0,0, 1, 1])
                            result = dictfetchall(cursor4)

                            cursor4.close()
                            no_of_stops = int(no_of_stops)
                            print("no of stops")
                            print(no_of_stops)
                            if journey_type == 'Round Trip':
                                final_stop = no_of_stops + 2
                            else:
                                final_stop = no_of_stops+1
                            for x in range(final_stop):
                                cursor5 = connection.cursor()
                                cursor5.callproc('addFlightBookingFlights',
                                                 [flight_name[x], flight_no[x], pnr_no[x], flight_from[x],
                                                  flight_to[x], departure_time[x], arrival_time[x], last_booking_id,
                                                  user_id, user_type, is_return_flight[x]])
                                result = dictfetchall(cursor5)
                                print("addFlightBookingFloght")
                                print(result)
                                cursor5.close()

                            employee_booking_id = []
                            employee_booking_id.append("1")
                            employee_booking_id.append("2")

                            print("no of pass")
                            print(no_of_passanger)
                            for xx in range(int(no_of_passanger)):
                                cursor26 = connection.cursor()
                                cursor26.callproc('updateFlightPassangerTickectNo',
                                                 [ticket_number[xx], employee_booking_id[xx], last_booking_id])
                                result = dictfetchall(cursor26)
                                print("addFlightBookingticket")
                                print(result)
                                cursor26.close()

                            print("Last Booking ID")
                            cursor27 = connection.cursor()
                            cursor27.callproc('viewFlightBooking', [last_booking_id])
                            emp = dictfetchall(cursor27)
                            cursor27.close()

                            cursor11 = connection.cursor()
                            cursor11.callproc('getAllFlightBookingPassangers', [last_booking_id])
                            passanger = dictfetchall(cursor11)
                            emp[0]['Passangers'] = passanger
                            cursor11.close()

                            cursor22 = connection.cursor()
                            cursor22.callproc('getAllFlightBookingFlights', [last_booking_id])
                            flights = dictfetchall(cursor22)
                            cursor22.close()

                            emp[0]['Flights'] = flights
                            client_ticket = "GEN PDF"
                            is_email = "1"
                            is_sms = "1"
                            get_voucher_path = ''
                            if client_ticket:
                                voucher = emp[0]
                                bus_pdf = Flight(voucher)
                                get_vou = bus_pdf.get(request)
                                get_voucher_path = get_vou[1]
                            else:
                                get_voucher_path = ""

                            add_booking_email = AddBooking_Email()
                            if is_email == '1':
                                thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Flight"))
                                thread.start()
                                #resp6 = add_booking_email.send_taxi_email(emp, approvers, "Flight")
                            if is_sms == '1':
                                thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Flight"))
                                thread.start()
                                #resp1 = add_booking_email.send_taxi_msg(emp, approvers, "Flight")

                            add_booking_email = Assign_Booking_Email()
                            if is_sms:
                                thread = Thread(target=add_booking_email.send_client_sms, args=(emp, "Flight"))
                                thread.start()
                                #resp1 = add_booking_email.send_client_sms(emp, "Flight")
                            if is_email:
                                thread = Thread(target=add_booking_email.is_client_email, args=(emp, "Flight", get_voucher_path))
                                thread.start()
                                #resp1 = add_booking_email.is_client_email(emp, "Flight", get_voucher_path)

                        data = {'success': 1, 'message': "PNR Generated Success, PNR Details Send to your Email", 'last_booking_id': last_booking_id}
                        return JsonResponse(data)

                    except Exception as e:
                        print(e)
                        data = {'success': 0, 'message': "Error in Data Insert"}
                        return JsonResponse(data)

                except Exception as e:
                    print("EXCEPTIONSNSNSNSN")
                    print(e)
                    data = {'success': 0, 'Data': "Exception"}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_nationality(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllNationality', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Nationality': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def visa_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllVisaType', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Visa': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def visa_service_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllVisaServiceType', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Visa': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def consulate_office(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllVisaConsulateOffice', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Visa': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)



def get_countries(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCountry', [])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Country': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_states(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        country_id = request.POST.get('country_id', '')
        if not country_id:
            country_id =0
        
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllState', [country_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'State': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_cities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        state_id = request.POST.get('state_id', '')
        if not state_id:
            state_id =0

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllCities', [state_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'City': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_operator_package(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        operator_id = request.POST.get('operator_id', '')

        if not operator_id:
            operator_id = 0

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllOperatorRatesDetails', [operator_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Rate': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_fcm_regid(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        fcm_regid = request.POST.get('fcm_regid', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updateFcmRegID', [user_id,user_type,fcm_regid])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'message': "FCM Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_notice(request):
    FCM1 = FCM()
    test = FCM1.send_custome_msg_notification('test')
    data = {'success': 1, 'message': "Notice Send Successfully..!"}
    return JsonResponse(data)


def send_broadcast_notification(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        msg_head = request.POST.get('msg_head', '')
        msg_title = request.POST.get('msg_title', '')
        msg_text = request.POST.get('msg_text', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    print("i m hererererer")
                    FCM1 = FCM()
                    thread = Thread(target=FCM1.send_broadcast_notification, args=(msg_head, msg_title, msg_text))
                    thread.start()
                    #test = FCM1.send_broadcast_notification(msg_head, msg_title, msg_text)
                    data = {'success': 1, 'message': "Notice Send Successfully..!"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def send_message_to_moblies(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        mobile_nos = request.POST.get('mobile_nos', '')
        msg_text = request.POST.get('msg_text', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    print("i m hererererer")
                    FCM1 = FCM()
                    thread = Thread(target=FCM1.send_message_to_moblies, args=(mobile_nos, msg_text))
                    thread.start()
                    #test = FCM1.send_broadcast_notification(msg_head, msg_title, msg_text)
                    data = {'success': 1, 'message': "Message Send Successfully..!"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)

    
def send_mail_to_user(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        email_subject = request.POST.get('email_subject', '')
        email_body = request.POST.get('email_body', '')
        email_to = request.POST.get('email_to', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    print("i m hererererer")
                    FCM1 = FCM()
                    thread = Thread(target=FCM1.send_mail_to_user, args=(email_subject, email_body, email_to))
                    thread.start()
                    #test = FCM1.send_broadcast_notification(msg_head, msg_title, msg_text)
                    data = {'success': 1, 'message': "Mail Send Successfully..!"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_all_leads(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllLeadDetails', [user_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    for comp in company:
                        lead_id = comp['id']
                        cursor11 = connection.cursor()
                        cursor11.callproc('getAllLeadComments', [lead_id])
                        passanger = dictfetchall(cursor11)
                        comp['LeadComments'] = passanger
                        cursor11.close()

                        cursor12 = connection.cursor()
                        cursor12.callproc('getAllLeadDocument', [lead_id])
                        passanger1 = dictfetchall(cursor12)
                        comp['LeadDocument'] = passanger1
                        cursor12.close()

                        cursor22 = connection.cursor()
                        cursor22.callproc('getAllLeadActionLogs', [lead_id])
                        flights = dictfetchall(cursor22)
                        comp['ActionLogs'] = flights
                        cursor22.close()


                    data = {'success': 1, 'Lead': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_lead(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')
        lead_id = request.POST.get('lead_id', '')
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewLeadDetails', [lead_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    for comp in company:
                        cursor11 = connection.cursor()
                        cursor11.callproc('getAllLeadComments', [lead_id])
                        passanger = dictfetchall(cursor11)
                        comp['LeadComments'] = passanger
                        cursor11.close()

                        cursor12 = connection.cursor()
                        cursor12.callproc('getAllLeadDocument', [lead_id])
                        passanger1 = dictfetchall(cursor12)
                        comp['LeadDocument'] = passanger1
                        cursor12.close()

                        cursor22 = connection.cursor()
                        cursor22.callproc('getAllLeadActionLogs', [lead_id])
                        flights = dictfetchall(cursor22)
                        comp['ActionLogs'] = flights
                        cursor22.close()

                    data = {'success': 1, 'Lead': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_lead(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    # cursor = connection.cursor()
                    # cursor.callproc('addNewLeadDetails', [contact_name,company_name,contact_number,contact_email,company_location,contact_address,company_website,
                    # message,hear_about_us,assigned_sales_person,status,lead_source,lead_communication,attachments,comments,user_id])
                    # company = dictfetchall(cursor)
                    # cursor.close()

                    form = LeadGenerationModelForm(request.POST or None, request.FILES)
                    if form.is_valid():

                        new_lead = form.save()
                        if request.FILES:
                            resp = file_upload(request, new_lead.pk)

                        new_comment = form.cleaned_data['Comments']
                        status_action = form.cleaned_data['Status']
                        # print(new_lead.pk)
                        # print(form.cleaned_data['Comments'])
                        cmt = LeadComments()
                        cmt.lead_id = new_lead.pk
                        cmt.comment = new_comment
                        cmt.created_by = Corporate_Agent.objects.get(pk=user_id)
                        cmt.created_at = timezone.now()
                        cmt.save()
                        log = LeadLog()
                        log.lead_id = new_lead.pk
                        log.comment = new_comment
                        log.status_action = status_action
                        log.action_initiated_by = user_id
                        log.save()
                        is_email = request.POST.get('is_email')
                        is_sms = request.POST.get('is_sms')

                        if is_email:
                            print("in email")
                            Contact_Name = request.POST.get('Contact_Name', '')
                            Company_Name = request.POST.get('Company_Name', '')
                            Contact_Number = request.POST.get('Contact_Number', '')
                            Contact_Email = request.POST.get('Contact_Email', '')
                            corporate_location = request.POST.get('Company_Location', '')
                            message = "Thank you for contacting us, our sales person will get in touch with you as earliest as possible.<br><br>Regards,<br>CoTrav"
                            signup = SignupEmail(Company_Name, corporate_location, Contact_Name, Contact_Number,
                                                 Contact_Email, message)
                            resp1 = signup.send_email()
                            print(resp1)
                        if is_sms:
                            print("in smsm")
                            sender_id = 'COTRAV'
                            exotel_sid = "novuslogic1"
                            exotel_key = "6ae4c99860c31346203da94dc98a4de7fd002addc5848182"
                            exotel_token = "a2c78520d23942ad9ad457b81de2ee3f3be743a8188f8c39"
                            Contact_no = request.POST.get('Contact_Number')
                            sms_body = "Thank you for contacting us, our sales person will get in touch with you as earliest as possible.<br><br>Regards,<br>CoTrav";

                            requests.post(
                                'https://twilix.exotel.in/v1/Accounts/{exotel_sid}/Sms/send.json'.format(
                                    exotel_sid=exotel_sid),
                                auth=(exotel_key, exotel_token),
                                data={
                                    'From': sender_id,
                                    'To': Contact_no,
                                    'Body': sms_body
                                })

                        messages.success(request, "Lead Created Successfully..!")
                        data = {'success': 1, 'message': 'Lead created Successfully..!'}
                    else:
                        print("eoorr listing")
                        print(form.errors)
                        messages.error(request, "Lead Status Not Created ..!")
                        data = {'success': 0, 'message': 'Lead Not Created..Parameter Missing!'}


                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def update_lead(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')
        lead_id = request.POST.get('lead_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    # cursor = connection.cursor()
                    # cursor.callproc('addNewLeadDetails', [contact_name,company_name,contact_number,contact_email,company_location,contact_address,company_website,
                    # message,hear_about_us,assigned_sales_person,status,lead_source,lead_communication,attachments,comments,user_id])
                    # company = dictfetchall(cursor)
                    # cursor.close()
                    lead = get_object_or_404(Leadgeneration, pk=lead_id)
                    form = LeadUpdateForm(request.POST or None, instance=lead, initial={'Comments': ''})

                    if form.is_valid():
                        edit_lead = form.save()
                        if request.FILES:
                            resp = file_upload(request, edit_lead.pk)
                        new_comment = form.cleaned_data['Comments']
                        status_action = form.cleaned_data['Status']
                        # print(new_lead.pk)
                        # print(form.cleaned_data['Comments'])
                        cmt = LeadComments()
                        cmt.lead_id = edit_lead.pk
                        cmt.comment = new_comment
                        cmt.created_by = Corporate_Agent.objects.get(pk=user_id)
                        cmt.created_at = timezone.now()
                        cmt.save()
                        log = LeadLog()
                        log.lead_id = edit_lead.pk
                        log.comment = new_comment
                        log.status_action = status_action
                        log.action_initiated_by = user_id
                        log.save()

                        data = {'success': 1, 'message': 'Lead Updated Successfully..!'}
                    else:
                        print("eoorr listing")
                        print(form.errors)
                        messages.error(request, "Lead  Not Update ..!")
                        data = {'success': 0, 'message': 'Lead Not Update..Parameter Missing!'}


                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_lead(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')
        lead_id = request.POST.get('lead_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    lead = get_object_or_404(Leadgeneration, pk=lead_id)
                    lead.delete()
                    data = {'success': 1, 'message': 'Lead Deleted Successfully..!'}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_lead_document(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')
        lead_id = request.POST.get('lead_doc_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    lead = get_object_or_404(Document, pk=lead_id)
                    lead.delete()
                    data = {'success': 1, 'message': 'Lead Deleted Successfully..!'}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_po_number_by_corporate(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')

        if not corporate_id:
            corporate_id = 0
        print("corporate id")
        print(corporate_id)
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getallCorporatePODetails', [corporate_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'PO_NUMBERS': company}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def getUserinfoFromAccessToken(user_token=None, user_type=None):
    try:
        user = {}
        user_info = {}
        if user_type == '1':
            user = Corporate_Login_Access_Token.objects.get(access_token=user_token)
            print("sdsds")
            print(user)
        elif user_type == '2':
            user = Corporate_Approves_1_Login_Access_Token.objects.get(access_token=user_token)
        elif user_type == '3':
            user = Corporate_Approves_2_Login_Access_Token.objects.get(access_token=user_token)
        elif user_type == '4':
            user = Corporate_Spoc_Login_Access_Token.objects.get(access_token=user_token)
        elif user_type == '6':
            user = Corporate_Employee_Login_Access_Token.objects.get(access_token=user_token)
        elif user_type == '10':
            user = Corporate_Agent_Login_Access_Token.objects.get(access_token=user_token)
        elif user_type == '7':
            user = Operator_Login_Access_Token.objects.get(access_token=user_token)
        elif user_type == '8':
            user = Operator_Driver_Access_Token.objects.get(access_token=user_token)

        timezone.activate(pytz.timezone("Asia/Kolkata"))
        present = timezone.localtime(timezone.now())

        if user.expiry_date.date() < present.date():
            return None
        else:

            if user_type == '1':
                user_info = Corporate_Login.objects.get(id=user.corporate_login_id)
            elif user_type == '2':
                user_info = Corporate_Approves_1_Login.objects.get(id=user.subgroup_authenticater_id)
            elif user_type == '3':
                user_info = Corporate_Approves_2_Login.objects.get(id=user.group_authenticater_id)
            elif user_type == '4':
                user_info = Corporate_Spoc_Login.objects.get(id=user.spoc_id)
            elif user_type == '6':
                user_info = Corporate_Employee_Login.objects.get(id=user.employee_id)
            elif user_type == '10':
                user_info = Corporate_Agent.objects.get(id=user.agent_id)
            elif user_type == '7':
                print(user)
                user_info = Operator_Login.objects.get(id=user.operator_id)
            elif user_type == '8':
                print(user)
                user_info = Operator_Driver.objects.get(id=user.driver_id)
            else:
                return None

            return user_info

    except Exception as e:
        print(e)
        return None


def corporate_management_tax(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        corporate_id = request.POST.get('corporate_id', '')
        service_type = request.POST.get('service_type', '')
        cotrav_billing_entity = request.POST.get('cotrav_billing_entity', '')
        corporate_billing_entity = request.POST.get('corporate_billing_entity', '')
        ticket_price = request.POST.get('ticket_price', '')

        no_of_passanger = request.POST.get('no_of_passanger', '')
        oper_ticket_price = request.POST.get('oper_ticket_price', '')
        oper_cotrav_billing_entity = request.POST.get('oper_cotrav_billing_entity', '')
        oper_billing_entity = request.POST.get('oper_billing_entity', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    tx = TaxCalc( corporateid= corporate_id , service_type= service_type , cotrav_billing_entity= cotrav_billing_entity ,
                                 corporate_billing_entity= corporate_billing_entity , ticket_price= ticket_price , no_of_passanger= no_of_passanger , oper_ticket_price= oper_ticket_price , oper_cotrav_billing_entity= oper_cotrav_billing_entity , oper_billing_entity= oper_billing_entity )

                    txx = tx.taxOnManagement()

                    if(service_type == 6):
                        txxx = tx.hotel_gst()
                    else:
                        txxx = tx.gst()


                    total_billing_amount = tx.total_billing_amount()

                    operator_calc = tx.oper_tax_calc()

                    details = tx.detailTax()

                    print(details)

                    #details_json = json.dumps(details)

                    data = {'success': 1, 'Tax': details}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_country_provided_by_cotrav(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('getCountryProvidedbyCotrav', [])
                    company = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'Country': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_visa_document(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        document_id = request.POST.get('document_id', '')
        visa_type = request.POST.get('visa_type', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('deleteVisaDocument', [document_id,visa_type])
                    company = dictfetchall(cursor)
                    cursor.close()
                    if company:
                        data = {'success': 0, 'message': 'Document Not Deleted..!'}
                    else:
                        data = {'success': 1, 'message': 'Document Deleted Successfully..!'}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e)), 'message': 'Document Not Deleted..!'}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def company_visa_services(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_id = request.POST.get('user_id', '')
        visa_type = request.POST.get('visa_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0

        if page_no:
            limit_from = (int(page_no) - 1) * 10
            limit_to = 10
        else:
            limit_from = 0
            limit_to = 2147483647
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('getAllCompanyVisaRequests', [visa_type, limit_from, limit_to, user_id, user_type])
                emp = dictfetchall(cursor)

                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        print(booking_id)
                        cursor1.callproc('getAllAgentVisaFamily', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['FamailyDocs'] = passanger
                        cursor1.close()

                        cursor2 = connection.cursor()
                        cursor2.callproc('getAllAgentVisaEmployeeDocuments', [booking_id])
                        passanger1 = dictfetchall(cursor2)
                        e['EmployeesDocs'] = passanger1
                        cursor2.close()

                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            print(invoice_id)
                            print("iiiiiiinnnnnvvvvvoooo")
                            cursor2.callproc('getallVisaInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['visa_type'] = visa_type
                    except Exception as e:
                        data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Visa': emp, 'visa_type': visa_type}
                return JsonResponse(data)
            else:
                data = {'success': 0, 'message': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def company_visa_services_bill(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_id = request.POST.get('user_id', '')
        visa_type = request.POST.get('visa_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0
        print("daatata")
        print(user_id)
        print(visa_type)
        print(user_type)
        if page_no:
            limit_from = (int(page_no) - 1) * 10
            limit_to = 10
        else:
            limit_from = 0
            limit_to = 2147483647
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('getAllCompanyVisaRequestsInvoice', [visa_type, user_id, user_type])
                emp = dictfetchall(cursor)

                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        print(booking_id)
                        cursor1.callproc('getAllAgentVisaFamily', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['FamailyDocs'] = passanger
                        cursor1.close()

                        cursor2 = connection.cursor()
                        cursor2.callproc('getAllAgentVisaEmployeeDocuments', [booking_id])
                        passanger1 = dictfetchall(cursor2)
                        e['EmployeesDocs'] = passanger1
                        cursor2.close()

                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            print(invoice_id)
                            print("iiiiiiinnnnnvvvvvoooo")
                            cursor2.callproc('getallVisaInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['visa_type'] = visa_type
                    except Exception as e:
                        data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Visa': emp, 'visa_type': visa_type}
                return JsonResponse(data)
            else:
                data = {'success': 0, 'message': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def company_frro_services_bill(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_id = request.POST.get('user_id', '')
        visa_type = request.POST.get('visa_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0
        print("daatata")
        print(user_id)
        print(visa_type)
        print(user_type)
        if page_no:
            limit_from = (int(page_no) - 1) * 10
            limit_to = 10
        else:
            limit_from = 0
            limit_to = 2147483647
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('getAllCompanyFrroRequestsInvoice', [visa_type, limit_from, limit_to, user_id, user_type])
                emp = dictfetchall(cursor)

                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']

                        cursor2 = connection.cursor()
                        cursor2.callproc('getAllAgentFrroEmployeeDocuments', [booking_id])
                        passanger1 = dictfetchall(cursor2)
                        e['EmployeesDocs'] = passanger1
                        cursor2.close()

                        cursor1 = connection.cursor()
                        cursor1.callproc('getAllFrroBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()

                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            cursor2.callproc('getallFrroInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['visa_type'] = visa_type
                    except Exception as e:
                        data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Visa': emp, 'visa_type': visa_type}
                return JsonResponse(data)
            else:
                data = {'success': 0, 'message': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)



def get_visa_type_by_country(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        country_id = request.POST.get('country_id')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('getVisaTypebyCountry', [country_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'Visa': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)
    

def get_request_visa_type_by_country(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        country_id = request.POST.get('country_id')
        visa_type = request.POST.get('visa_type')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('getVisaRequestTypebyCountry', [country_id,visa_type])
                    company = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'Visa': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_consulate_office_by_country(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        country_id = request.POST.get('country_id')
        visa_type = request.POST.get('visa_type')
        visa_request_type = request.POST.get('visa_request_type')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('getConsulateOfficebyCountry', [country_id,visa_type,visa_request_type])
                    company = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'Visa': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_instruction_and_link(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        country_id = request.POST.get('country_id')
        visa_type = request.POST.get('visa_type')
        visa_request_type = request.POST.get('visa_request_type')
        consulate_office_id = request.POST.get('consulate_office_id')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('getInstructionAndLink', [country_id,visa_type,visa_request_type,consulate_office_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'Visa': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_visa_requests(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id')
        corporate_id = request.POST.get('corporate_id')
        request_type = request.POST.get('request_type')
        visa_request_type = request.POST.get('visa_request_type')
        spoc_id = request.POST.get('spoc_id')
        group_id = request.POST.get('group_id')
        subgroup_id = request.POST.get('subgroup_id')
        billing_entity_id = request.POST.get('billing_entity_id')
        country_id = request.POST.get('country_id')
        visa_type = request.POST.get('visa_type')
        visa_duration = request.POST.get('visa_duration')
        purpose_of_trip = request.POST.get('purpose_of_trip')
        current_country_id = request.POST.get('current_country_id')
        current_state_id = request.POST.get('current_state_id')
        consulate_office_id = request.POST.get('consulate_office_id')
        no_of_employees = request.POST.get('no_of_employees')
        no_of_family_member = request.POST.get('no_of_family_member')
        application_form_link = request.POST.get('application_form_link')

        employee_ids = request.POST.getlist('employee_ids')
        employees = list(filter(None, employee_ids))
        employees = ",".join(employees)
        print("EMPLOYEEE ID")
        print(employees)
        
        emp_no_of_document = request.POST.getlist('emp_no_of_document')
        emp_document = request.POST.getlist('emp_document')
        emp_document_txt = request.POST.getlist('emp_document_txt')

        family_members_name = request.POST.getlist('family_members_name')
        family_members_relationship = request.POST.getlist('family_members_relationship')
        empf_no_of_document = request.POST.getlist('empf_no_of_document')
        empf_document = request.POST.getlist('empf_document')
        empf_document_path = request.POST.getlist('empf_document_path')
        empf_document_txt = request.POST.getlist('empf_document_txt')

        employee_application_form = request.POST.getlist('employee_application_form')
        employee_docs = request.POST.getlist('employee_docs')
        
        employeef_application_form = request.POST.getlist('employeef_application_form')
        employeef_docs = request.POST.getlist('employeef_docs')

        is_email = request.POST.get('is_email')
        is_sms = request.POST.get('is_sms')
       
        user = {}
        last_booking_id = 0
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('addNewVisaRequestDetails', [corporate_id,spoc_id,group_id,subgroup_id,country_id,visa_type,purpose_of_trip,current_country_id,
                    current_state_id,consulate_office_id,no_of_employees,request_type,visa_request_type,visa_duration,
                    no_of_family_member,application_form_link,user_id,user_type,'@last_request_id',employees,billing_entity_id])
                    company = dictfetchall(cursor)
                    cursor.close()
                    print(company)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        cursor1 = connection.cursor()
                        cursor1.execute("SELECT @last_request_id")
                        last_booking_id = cursor1.fetchone()[0]
                        cursor1.close()

                    final_emp_no = int(no_of_employees)
                    final_no_of_family = int(no_of_family_member)
                    cnt_1 = 0
                    cnt_2 = 0
                    cnt_3 = 0
                    cnt_4 = 0
                    print("lelelelelel")
                    print(empf_no_of_document)
                    print(len(empf_no_of_document))
                    if request_type == 'Family':
                        for i1 in range(final_no_of_family):
                            if len(employeef_application_form) >= 1:
                                finl_empf_no_of_document = int(empf_no_of_document[i1])
                                cursor2 = connection.cursor()
                                cursor2.callproc('addVisaRequestFamily', [last_booking_id, employee_ids[0], family_members_name[i1], family_members_relationship[i1], "Application Form",  employeef_application_form[i1]])
                                company = dictfetchall(cursor2)
                                cursor2.close()
                                for ii2 in range(finl_empf_no_of_document):
                                    if empf_document[cnt_4] == 'Other Document':
                                        empf_document[cnt_4] = empf_document_txt[cnt_4]
                                    print("counter 4")
                                    print(cnt_4)
                                    cursor2 = connection.cursor()
                                    cursor2.callproc('addVisaRequestFamily',[last_booking_id, employee_ids[0], family_members_name[i1], family_members_relationship[i1], empf_document[cnt_4],  employeef_docs[cnt_3]])
                                    company = dictfetchall(cursor2)
                                    cursor2.close()
                                    cnt_3 = cnt_3 + 1
                                    cnt_4 = cnt_4 + 1
                                cnt1 = 4 - finl_empf_no_of_document
                                cnt_4 = cnt_4 + cnt1
                    else:
                        for i in range(final_emp_no):
                            if len(employee_application_form) >= 1:
                                finl_emp_no_of_document = int(emp_no_of_document[i])
                                cursor2 = connection.cursor()
                                cursor2.callproc('addVisaRequestEmployee', [last_booking_id, employee_ids[i], 'Application Form', employee_application_form[i]])
                                company = dictfetchall(cursor2)
                                cursor2.close()
                                emp_no_docs = int(emp_no_of_document[i])
                                for ii in range(finl_emp_no_of_document):
                                    if emp_document[cnt_2] == 'Other Document':
                                        emp_document[cnt_2] = emp_document_txt[cnt_2]
                                    cursor3 = connection.cursor()
                                    cursor3.callproc('addVisaRequestEmployee', [last_booking_id, employee_ids[i], emp_document[cnt_2], employee_docs[cnt_1]])
                                    company = dictfetchall(cursor3)
                                    cursor3.close()

                                    cnt_1 = cnt_1 + 1
                                    cnt_2 = cnt_2 + 1
                                cnt = 4 - finl_emp_no_of_document
                                cnt_2 = cnt_2 + cnt

                    cursor = connection.cursor()
                    cursor.callproc('viewVisadDetails', [last_booking_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllAgentVisaFamily', [last_booking_id])
                    passanger = dictfetchall(cursor1)
                    company[0]['FamailyDocs'] = passanger
                    cursor1.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllAgentVisaEmployeeDocuments', [last_booking_id])
                    passanger1 = dictfetchall(cursor2)
                    company[0]['EmployeesDocs'] = passanger1
                    cursor2.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllApproverByBookingID', [last_booking_id, 6])
                    approvers = dictfetchall(cursor3)
                    cursor3.close()

                    add_booking_email = AddBooking_Email()
                    
                    if is_email == '1':
                        thread = Thread(target=add_booking_email.send_taxi_email, args=(company, approvers, "Visa"))
                        thread.start()
                    if is_sms == '1':
                        thread = Thread(target=add_booking_email.send_taxi_msg, args=(company, approvers, "Visa"))
                        thread.start()

                    fcm = FCM()
                    thread = Thread(target=fcm.send_notification_add, args=(company, approvers, "Visa"))
                    thread.start()

                    data = {'success': 1, 'message': 'Visa Request Added Successfully..!', 'Visa': company}

                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    data = {'success': 0, 'message': getattr(e, 'message', str(e)), 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_new_employee_visa_document(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id')
        is_document_family = request.POST.get('is_document_family')
        visa_request_id = request.POST.get('visa_request_id')

        no_of_employees = request.POST.get('no_of_employees')
        no_of_family_member = request.POST.get('no_of_family_member')

        employee_ids = request.POST.getlist('employee_ids')
        emp_no_of_document = request.POST.getlist('emp_no_of_document')
        emp_document = request.POST.getlist('emp_document')
        emp_document_txt = request.POST.getlist('emp_document_txt')

        family_members_name = request.POST.getlist('family_members_name')
        family_members_relationship = request.POST.getlist('family_members_relationship')
        empf_no_of_document = request.POST.getlist('empf_no_of_document')
        empf_document = request.POST.getlist('empf_document')
        empf_document_path = request.POST.getlist('empf_document_path')
        empf_document_txt = request.POST.getlist('empf_document_txt')
        print(family_members_name)
        print(family_members_relationship)
        print(empf_no_of_document)

        employee_application_form = request.POST.getlist('employee_application_form')
        employee_docs = request.POST.getlist('employee_docs')

        employeef_application_form = request.POST.getlist('employeef_application_form')
        employeef_docs = request.POST.getlist('employeef_docs')

        user = {}
        last_booking_id = visa_request_id
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    final_emp_no = int(no_of_employees)
                    final_no_of_family = int(no_of_family_member)
                    cnt_1 = 0
                    cnt_2 = 0
                    cnt_3 = 0
                    cnt_4 = 0

                    if is_document_family == '1' or is_document_family == 1:
                        for i1 in range(final_no_of_family):
                            finl_empf_no_of_document = int(empf_no_of_document[i1])
                            cursor2 = connection.cursor()
                            cursor2.callproc('addVisaRequestFamily', [last_booking_id, employee_ids[0], family_members_name[i1], family_members_relationship[i1], "Application Form",  employeef_application_form[i1]])
                            company = dictfetchall(cursor2)
                            print("1 f output")
                            print(company)
                            cursor2.close()
                            for ii2 in range(finl_empf_no_of_document):
                                if empf_document[cnt_4] == 'Other Document':
                                    empf_document[cnt_4] = empf_document_txt[cnt_4]
                                print("counter 4")
                                print(cnt_4)
                                cursor2 = connection.cursor()
                                cursor2.callproc('addVisaRequestFamily',[last_booking_id, employee_ids[0], family_members_name[i1], family_members_relationship[i1], empf_document[cnt_4],  employeef_docs[cnt_3]])
                                company1 = dictfetchall(cursor2)
                                print("2 f output")
                                print(company1)
                                cursor2.close()
                                cnt_3 = cnt_3 + 1
                                cnt_4 = cnt_4 + 1
                            cnt1 = 4 - finl_empf_no_of_document
                            cnt_4 = cnt_4 + cnt1
                    else:
                        for i in range(final_emp_no):
                            finl_emp_no_of_document = int(emp_no_of_document[i])
                            cursor2 = connection.cursor()
                            cursor2.callproc('addVisaRequestEmployee',
                                             [last_booking_id, employee_ids[i], 'Application Form',
                                              employee_application_form[i]])
                            company = dictfetchall(cursor2)
                            cursor2.close()
                            emp_no_docs = int(emp_no_of_document[i])
                            for ii in range(finl_emp_no_of_document):

                                if emp_document[cnt_2] == 'Other Document':
                                    emp_document[cnt_2] = emp_document_txt[cnt_2]
                                cursor3 = connection.cursor()
                                cursor3.callproc('addVisaRequestEmployee',
                                                 [last_booking_id, employee_ids[i], emp_document[cnt_2],
                                                  employee_docs[cnt_1]])
                                company = dictfetchall(cursor3)
                                cursor3.close()

                                cnt_1 = cnt_1 + 1
                                cnt_2 = cnt_2 + 1
                            cnt = 4 - finl_emp_no_of_document
                            cnt_2 = cnt_2 + cnt

                    data = {'success': 1, 'message': "Document Added Successfully..!"}

                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    data = {'success': 0, 'message': "Document Not Added..!", 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)




def view_visa_request(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        visa_id = request.POST.get('visa_id')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('viewVisadDetails', [visa_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllAgentVisaFamily', [visa_id])
                    passanger = dictfetchall(cursor1)
                    company[0]['FamailyDocs'] = passanger
                    cursor1.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllAgentVisaEmployeeDocuments', [visa_id])
                    passanger1 = dictfetchall(cursor2)
                    company[0]['EmployeesDocs'] = passanger1
                    cursor2.close()

                    data = {'success': 1, 'Visa': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_booking_feedback(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        booking_type = request.POST.get('booking_type', '')
        user_rating = request.POST.get('user_rating', '')
        user_actual_rating = request.POST.get('user_actual_rating', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addClientBookingRaiseIssue', [user_id,user_type,booking_id,user_rating,user_actual_rating,booking_type])
                    company = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'message': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'message': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def agent_dashboard_sales_by_city(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        login_type = int(request.POST.get('login_type', ''))

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            print("datatatatattatat")
            print(user_token[1])
            print(user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [1, login_type, user.id, user.id])
                    city_taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [2, login_type, user.id, user.id])
                    city_bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [3, login_type, user.id, user.id])
                    city_train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [4, login_type, user.id, user.id])
                    city_flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [5, login_type, user.id, user.id])
                    city_hotel = dictfetchall(cursor)
                    cursor.close()

                    print('## dashboard_sales_by_city ##')
                    print(city_taxi)
                    print(city_bus)
                    print(city_train)
                    print(city_flight)
                    print(city_hotel)
                    print('#####')

                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Sales': [city_taxi, city_bus, city_train, city_flight, city_hotel]}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def agent_payment_pending_from_client(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        login_type = int(request.POST.get('login_type', ''))

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            print("datatatatattatat")
            print(user_token[1])
            print(user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getallPaymentPendingFromClient', [login_type, user.id, 1])
                    city_taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getallPaymentPendingFromClient', [login_type, user.id, 2])
                    city_bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getallPaymentPendingFromClient', [login_type, user.id, 3])
                    city_train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getallPaymentPendingFromClient', [login_type, user.id, 4])
                    city_flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getallPaymentPendingFromClient', [login_type, user.id, 5])
                    city_hotel = dictfetchall(cursor)
                    cursor.close()

                    print('## sadjsakjdgaskgdaksgdkajsgdkgsakdga ##')
                    print(city_taxi)
                    print(city_bus)
                    print(city_train)
                    print(city_flight)
                    print(city_hotel)
                    print('## sadjsakjdgaskgdaksgdkajsgdkgsakdga ##')

                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Sales': [city_taxi, city_bus, city_train, city_flight, city_hotel]}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': getattr(e, 'message', str(e))}
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


def get_public_api_access_token(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getPublicApiCorporateAccessToken', [])
                    company = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'message': 'data found', 'Data':company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': getattr(e, 'message', str(e))}
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


def add_api_access_token(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        
        corporate_id = request.POST.get('corporate_id', '')
        spoc_id = request.POST.get('spoc_id', '')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        user_id = request.POST.get('user_id', '')
        user_password = request.POST.get('user_password', '')
        user_access_token = request.POST.get('user_access_token', '')
        is_active = request.POST.get('is_active', '')

        if user_password:
            user_password= make_password(user_password)
        else:
            user_password = make_password("taxi123")
        
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addPublicApiAccessToken', [corporate_id,spoc_id,billing_entity_id,user_id,user_password,user_access_token,is_active])
                    cities = dictfetchall(cursor)
                    print(cities)
                    data = {'success': 1, 'message': "Public Api Access Token Added Successfully", 'id' : cities}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': getattr(e, 'message', str(e))}
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


def update_api_access_token(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        
        corporate_id = request.POST.get('corporate_id', '')
        spoc_id = request.POST.get('spoc_id', '')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        user_id = request.POST.get('user_id', '')
        user_password = request.POST.get('user_password', '')
        user_access_token = request.POST.get('user_access_token', '')
        is_active = request.POST.get('is_active', '')
        token_id = request.POST.get('token_id', '')
        
        if user_password:
            user_password= make_password(user_password)
        else:
            user_password = make_password("taxi123")
        
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('updatePublicApiAccessToken', [corporate_id,spoc_id,billing_entity_id,user_id,user_password,user_access_token,is_active,token_id])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Public Api Access Token Updated Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': getattr(e, 'message', str(e))}
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


def delete_api_access_token(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        token_id = request.POST.get('token_id', '')
        user_id = request.POST.get('user_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('deletePublicApiAccessToken', [token_id])
                    cities = dictfetchall(cursor)
                    cursor.close()
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Public Api Access Token Deleted Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': getattr(e, 'message', str(e))}
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


def add_frro_requests(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id')

        corporate_id = request.POST.get('corporate_id')
        request_type = request.POST.get('request_type')
        spoc_id = request.POST.get('spoc_id')
        group_id = request.POST.get('group_id')
        subgroup_id = request.POST.get('subgroup_id')
        billing_entity_id = request.POST.get('entity_id')
        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no')
        booking_email = request.POST.get('booking_email')
        no_of_employees = request.POST.get('no_of_employees')

        employee_ids = request.POST.getlist('employee_ids')
        employees = list(filter(None, employee_ids))
        employees = ",".join(employees)
        
        employee_text_index = request.POST.getlist('employee_text_index')
        employee_docs = request.POST.get('employee_docs')

        city_id = request.POST.get('city_id')
        registered_email = request.POST.get('registered_email')
        reason_of_booking = request.POST.get('reason_of_booking')
        registered_username = request.POST.get('registered_username')
        registered_password = request.POST.get('registered_password')

        father_name = request.POST.get('father_name')
        mother_name = request.POST.get('mother_name')
        spouse_name = request.POST.get('spouse_name')
        height = request.POST.get('height')
        relegion = request.POST.get('relegion')
        outind_address = request.POST.get('outind_address')
        outind_city = request.POST.get('outind_city')
        outind_country = request.POST.get('outind_country')
        ind_address = request.POST.get('ind_address')
        ind_city = request.POST.get('ind_city')
        ind_country = request.POST.get('ind_country')
        embarkation_place = request.POST.get('embarkation_place')
        embarkation_city = request.POST.get('embarkation_city')
        embarkation_country = request.POST.get('embarkation_country')
        date_of_arrival = request.POST.get('date_of_arrival')
        disembarkation_place = request.POST.get('disembarkation_place')
        mode_of_journey = request.POST.get('mode_of_journey')
        trip_number = request.POST.get('trip_number')
        purpose_of_visit = request.POST.get('purpose_of_visit')
        is_military = request.POST.get('is_military')

        passport_issue_date = ''
        passport_issue_date = ''
        passport_issue_date = ''
        passport_issue_date = ''
        passport_issue_date = ''

        passport_no = request.POST.get('passport_no')
        passport_issue_date = request.POST.get('passport_issue_date')
        passport_expiry_date = request.POST.get('passport_expiry_date')
        visa_number = request.POST.get('visa_number')
        visa_expiry_date = request.POST.get('visa_expiry_date')
        current_location = request.POST.get('current_location')
        current_stay_address = request.POST.get('current_stay_address')
        company_contract_expiry_date = request.POST.get('company_contract_expiry_date')
        formc_expiry_date = request.POST.get('formc_expiry_date')
        lease_status = request.POST.get('lease_status')

        if passport_issue_date:
            passport_issue_date = datetime.strptime(passport_issue_date, '%d-%m-%Y')
        if passport_expiry_date:
            passport_expiry_date = datetime.strptime(passport_expiry_date, '%d-%m-%Y')
        if visa_expiry_date:
            visa_expiry_date = datetime.strptime(visa_expiry_date, '%d-%m-%Y')
        if company_contract_expiry_date:
            company_contract_expiry_date = datetime.strptime(company_contract_expiry_date, '%d-%m-%Y')
        if formc_expiry_date:
            formc_expiry_date = datetime.strptime(formc_expiry_date, '%d-%m-%Y')
        if date_of_arrival:
            date_of_arrival = datetime.strptime(date_of_arrival, '%d-%m-%Y')


        is_email = request.POST.get('is_email')
        is_sms = request.POST.get('is_sms')

        doc_files = request.POST.get('doc_files')
        print("employeee docesssssss")
        print(doc_files)
        user = {}
        last_booking_id = 0
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    print("employee id")
                    print(employee_ids[0])
                    cursor = connection.cursor()
                    cursor.callproc('addNewFrroRequestDetails', [corporate_id, spoc_id, group_id, subgroup_id, request_type, bta_code_travel_req_no,
                    booking_email, no_of_employees, user_id, user_type, '@last_request_id', employees, billing_entity_id,city_id,registered_email,
                    reason_of_booking,registered_username,registered_password,father_name,mother_name,spouse_name,height,relegion,outind_address,outind_city,
                    outind_country,ind_address,ind_city,ind_country,embarkation_place,embarkation_city,embarkation_country,date_of_arrival,disembarkation_place,
                    mode_of_journey,trip_number,purpose_of_visit,is_military,employee_ids[0],passport_no,passport_issue_date,passport_expiry_date,
                    visa_number,visa_expiry_date,current_location,current_stay_address,company_contract_expiry_date,formc_expiry_date,lease_status])
                    company = dictfetchall(cursor)
                    cursor.close()
                    print(company)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        cursor1 = connection.cursor()
                        cursor1.execute("SELECT @last_request_id")
                        last_booking_id = cursor1.fetchone()[0]
                        cursor1.close()


                    for the_key, the_value in json.loads(doc_files).items():
                        cursor3 = connection.cursor()
                        cursor3.callproc('addFrroEmployeeDocument', [last_booking_id, employee_ids[0], the_key, the_value])
                        company = dictfetchall(cursor3)
                        cursor3.close()

                    cursor = connection.cursor()
                    cursor.callproc('viewFrroDetails', [last_booking_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllFrroBookingPassangers', [last_booking_id])
                    passanger = dictfetchall(cursor1)
                    company[0]['Passangers'] = passanger
                    cursor1.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllAgentFrroEmployeeDocuments', [last_booking_id])
                    passanger1 = dictfetchall(cursor2)
                    company[0]['EmployeesDocs'] = passanger1
                    cursor2.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllApproverByBookingID', [last_booking_id, 7])
                    approvers = dictfetchall(cursor3)
                    cursor3.close()

                    add_booking_email = AddBooking_Email()

                    if is_email == '1':
                        thread = Thread(target=add_booking_email.send_taxi_email, args=(company, approvers, "Frro"))
                        thread.start()
                    if is_sms == '1':
                        thread = Thread(target=add_booking_email.send_taxi_msg, args=(company, approvers, "Frro"))
                        thread.start()

                    fcm = FCM()
                    thread = Thread(target=fcm.send_notification_add, args=(company, approvers, "Frro"))
                    thread.start()

                    data = {'success': 1, 'message': 'Frro Request Added Successfully..Your Booking ID is : FRRO0000'+str(last_booking_id), 'Frro': company}

                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
                    data = {'success': 0, 'message': getattr(e, 'message', str(e)),
                            'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def view_frro_request(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        visa_id = request.POST.get('frro_id')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:

                    cursor = connection.cursor()
                    cursor.callproc('viewFrroDetails', [visa_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllAgentFrroEmployeeDocuments', [visa_id])
                    passanger1 = dictfetchall(cursor2)
                    company[0]['EmployeesDocs'] = passanger1
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllFrroBookingPassangers', [visa_id])
                    passanger = dictfetchall(cursor1)
                    company[0]['Passangers'] = passanger
                    cursor1.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllFrroBookingActionLogs', [visa_id])
                    passanger = dictfetchall(cursor3)
                    company[0]['ActionLogs'] = passanger
                    cursor3.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllFrroBookingRequestLetterDetails', [visa_id])
                    passanger = dictfetchall(cursor3)
                    company[0]['RequestLetters'] = passanger
                    cursor3.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllFrroBookingOfficeStatusDetails', [visa_id])
                    passanger = dictfetchall(cursor3)
                    company[0]['OfficeStatus'] = passanger
                    cursor3.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getFrroBookingPendingDocumentActionLogs', [visa_id])
                    passanger = dictfetchall(cursor3)
                    company[0]['PendingDocumentActionLogs'] = passanger
                    cursor3.close()


                    data = {'success': 1, 'Frro': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def frro_change_document(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        visa_id = request.POST.get('document_id')
        document_file = request.POST.get('document_file')


        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('FrroChangeDoucumentFile', [visa_id, document_file])
                    company = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Frro': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def frro_change_document_letter(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        booking_id = request.POST.get('booking_id', '')
        booking_id_main = request.POST.get('booking_id_main', '')
        document_file = request.POST.get('document_file')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('FrroChangeDoucumentRequestLetter', [booking_id, booking_id_main, document_file])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('viewFrroDetails', [booking_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    add_booking_email = FrroChangeDoucumentRequestLetter_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(company, "Frro", document_file))
                    thread.start()


                    data = {'success': 1, 'Frro': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def frro_change_office_status(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        booking_id = request.POST.get('booking_id', '')
        booking_id_main = request.POST.get('booking_id_main', '')
        status_type = request.POST.get('status_type', '')
        status = request.POST.get('status', '')
        status_comment = request.POST.get('status_comment', '')
        document_file = request.POST.get('document_file')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':

            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('FrroChangeOfficeStatus', [booking_id, booking_id_main, status_type, status, status_comment, document_file, user.id, user_type])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('viewFrroDetails', [booking_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    add_booking_email = FrroChangeOfficeStatus_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(company, "Frro", status_type, status, status_comment, document_file))
                    thread.start()
                    
                    
                    data = {'success': 1, 'Frro': company}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_travelport_locator_code(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        book_id = request.POST.get('book_id', '')
        book_ref = request.POST.get('book_ref', '')
        uni_record_locator = request.POST.get('uni_record_locator', '')
        provider_locator_code = request.POST.get('provider_locator_code', '')
        reservation_locator_code = request.POST.get('reservation_locator_code', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('addTravelportLocatorCode', [book_id , book_ref , uni_record_locator , provider_locator_code , reservation_locator_code ])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company,'id':company}
                    else:
                        data = {'success': 1, 'message': "Locator Code Saved"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_travelport_locator_code(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        book_id = request.POST.get('book_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getTravelportLocatorCode', [book_id])
                    codes = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Codes': codes}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_all_frro_status(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']


        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getallFrroStatus', [])
                    codes = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Status': codes}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def upload_document_get_path(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        base64_string = request.POST.get('base64_string', '')
        file_extension = request.POST.get('file_extension', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    file_path = upload_frro_doc_get_path(base64_string, file_extension)
                    data = {'success': 1, 'path': file_path}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_guesthouse_from_city_area(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        from_city = request.POST.get('from_city', '')
        area = request.POST.get('preferred_hotel_area', '')
        check_in_date = request.POST.get('check_in_date', '')
        check_out_date = request.POST.get('check_out_date', '')
        if check_in_date:
            check_in_date = datetime.strptime(check_in_date, '%d-%m-%Y %H:%M')
        if check_out_date:
            check_out_date = datetime.strptime(check_out_date, '%d-%m-%Y %H:%M')
        print(check_in_date)
        print(check_out_date)
        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getGuestHouseFromCityArea', [from_city,area,check_in_date,check_out_date])
                    Guesthouse = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Guesthouse': Guesthouse}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_guesthouse_by_corporate(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        corporate_id = request.POST.get('corporate_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getGuestHouseByCorporate', [corporate_id])
                    Guesthouse = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Guesthouse': Guesthouse}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def get_guesthouse_details(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        guesthouse_id = request.POST.get('guesthouse_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':

            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getallCorporateGuesthouseDetails', [guesthouse_id])
                    Guesthouse = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Guesthouse': Guesthouse}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def add_guesthouse_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')

        bta_code_travel_req_no = request.POST.get('bta_code_travel_req_no', '')
        corporate_id = request.POST.get('corporate_id', '')
        booking_email = request.POST.get('booking_email', '')
        spoc_id = request.POST.get('spoc_id', '')
        group_id = request.POST.get('group_id', '')
        subgroup_id = request.POST.get('subgroup_id', '')

        booking_datetime = request.POST.get('booking_datetime', '')
        if booking_datetime:
            booking_datetime = datetime.strptime(booking_datetime, '%d-%m-%Y %H:%M:%S')
        else:
            timezone.activate(pytz.timezone("Asia/Kolkata"))
            booking_datetime = timezone.localtime(timezone.now())

        checkin_datetime = request.POST.get('checkin_datetime', '')
        checkin_datetime = datetime.strptime(checkin_datetime, '%d-%m-%Y %H:%M:%S')
        checkout_datetime = request.POST.get('checkout_datetime', '')
        checkout_datetime = datetime.strptime(checkout_datetime, '%d-%m-%Y %H:%M:%S')
        no_of_nights = request.POST.get('no_of_nights', '')
        
        if not no_of_nights:
            no_of_nights = 1
            
        city_id = request.POST.get('city_id', '')
        room_id = request.POST.get('room_id', '')
        guesthouse_id = request.POST.get('guesthouse_id', '')
        preferred_hotel = request.POST.get('preferred_hotel', '')
        billing_entity_id = request.POST.get('billing_entity_id', '')
        assessment_code = request.POST.get('assessment_code', '')
        assessment_city_id = request.POST.get('assessment_city_id', '')
        is_email = request.POST.get('is_email', '')
        is_sms = request.POST.get('is_sms', '')

        if booking_email:
            pass
        else:
            booking_email = ''

        if assessment_code:
            pass
        else:
            assessment_code = 0

        if assessment_city_id:
            pass
        else:
            assessment_city_id = 0

        reason_booking = request.POST.get('reason_booking', '')
        no_of_seats = request.POST.get('no_of_seats', '')

        employees = request.POST.getlist('employees', '')
        employees = ",".join(employees)
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    booking_reference_no = ''
                    cursor.callproc('addGuestHouseBooking',
                                    [checkin_datetime, checkout_datetime, room_id,
                                     guesthouse_id, preferred_hotel, booking_datetime, assessment_code,
                                     assessment_city_id, no_of_seats, group_id, subgroup_id, spoc_id,
                                     corporate_id, billing_entity_id, reason_booking, user_id, user_type, employees,
                                     booking_email, '@last_booking_id', no_of_nights, '@booking_reference_no',
                                     bta_code_travel_req_no,city_id])
                    booking_id = dictfetchall(cursor)
                    print(booking_id)
                    if booking_id:
                        data = {'success': 0, 'message': booking_id}
                    else:
                        cursor.execute("SELECT @last_booking_id")
                        last_booking_id = cursor.fetchone()[0]
                        print(last_booking_id)
                        cursor.close()

                        cursor12 = connection.cursor()
                        cursor12.execute("SELECT @booking_reference_no")
                        booking_reference_no = cursor12.fetchone()[0]
                        print("Booking Refrence no")
                        print(booking_reference_no)
                        cursor12.close()

                        cursor2 = connection.cursor()
                        cursor2.callproc('viewGuestHouseBooking', [last_booking_id])
                        emp = dictfetchall(cursor2)
                        cursor2.close()

                        cursor1 = connection.cursor()
                        cursor1.callproc('getAllGuestHouseBookingPassangers', [last_booking_id])
                        passanger = dictfetchall(cursor1)
                        emp[0]['Passangers'] = passanger
                        cursor1.close()

                        cursor3 = connection.cursor()
                        cursor3.callproc('getAllApproverByBookingID', [last_booking_id, 8])
                        approvers = dictfetchall(cursor3)
                        cursor3.close()

                        fcm = FCM()
                        thread = Thread(target=fcm.send_notification_add, args=(emp, approvers, "Guesthouse"))
                        thread.start()

                        add_booking_email = AddBooking_Email()
                        if is_email == '1':
                            thread = Thread(target=add_booking_email.send_taxi_email, args=(emp, approvers, "Guesthouse"))
                            thread.start()
                        if is_sms == '1':
                            thread = Thread(target=add_booking_email.send_taxi_msg, args=(emp, approvers, "Guesthouse"))
                            thread.start()

                    data = {'success': 1, 'message': "GuestHouse Booking Added Successfully..! Your Booking ID is : " + str(
                        booking_reference_no), 'booking_reference_no': booking_reference_no}
                    return JsonResponse(data)

                except Exception as e:
                    print("EXCEPTION")
                    print(e)
                    data = {'success': 0, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def company_guesthouse_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        visa_type = request.POST.get('request_type', '')
        page_no = request.POST.get('page_no', '')
        user_id = request.POST.get('user_id', '')
        limit_from = 0
        limit_to = 0
        print(page_no)
        if page_no:
            limit_from = (int(page_no) - 1) * 10
            limit_to = 10
        else:
            limit_from = 0
            limit_to = 2147483647
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('getAllCorporateGuestHouseBookings', [visa_type,limit_from,limit_to,user_id,user_type])
                emp = dictfetchall(cursor)
                cursor.close()

                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']

                        cursor1 = connection.cursor()
                        cursor1.callproc('getAllGuesthouseBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()

                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            cursor2.callproc('getallGuesthouseInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['request_type'] = visa_type
                    except Exception as e:
                        data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp, 'request_type':visa_type}
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
    

def view_guesthouse_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:

                try:
                    cursor = connection.cursor()
                    cursor.callproc('viewGuestHouseBooking', [booking_id])
                    emp = dictfetchall(cursor)

                    cursor.close()
                    cursor1 = connection.cursor()
                    booking_id = emp[0]['id']
                    corporate_id = emp[0]['corporate_id']

                    cursor1.callproc('getAllGuesthouseBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    cursor1.close()

                    cursor4 = connection.cursor()
                    cursor4.callproc('getAllCorporateBillingEntitiesDetails', [corporate_id, user.id, user_type])
                    actions1 = dictfetchall(cursor4)
                    emp[0]['ClientEntity'] = actions1
                    cursor4.close()

                    cursor5 = connection.cursor()
                    cursor5.callproc('getAllCotravBillingEntities', [])
                    actions2 = dictfetchall(cursor5)
                    emp[0]['CotravEntity'] = actions2
                    cursor5.close()

                    cursor7 = connection.cursor()
                    cursor7.callproc('getAllCorporateEmployeesDetails', [corporate_id, user.id, user_type])
                    actions6 = dictfetchall(cursor7)
                    emp[0]['Employees'] = actions6
                    cursor7.close()

                    cursor8 = connection.cursor()
                    cursor8.callproc('getAllCorporateSpocsDetails', [corporate_id, user.id, user_type])
                    actions63 = dictfetchall(cursor8)
                    emp[0]['Spocs'] = actions63
                    cursor8.close()

                    cursor9 = connection.cursor()
                    cursor9.callproc('getAllCorporateAssessmentCities', [corporate_id, user.id, user_type])
                    actions62 = dictfetchall(cursor9)
                    emp[0]['AssCities'] = actions62
                    cursor9.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCorporateAssessmentCodes', [corporate_id, user.id, user_type])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['AssCodes'] = actions61
                    cursor81.close()

                    cursor81 = connection.cursor()
                    cursor81.callproc('getAllCity', [])
                    actions61 = dictfetchall(cursor81)
                    emp[0]['cities'] = actions61
                    cursor81.close()

                    
                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllTrackingStatusByBookingID', [8, booking_id])
                    flights = dictfetchall(cursor2)
                    emp[0]['TrackingStatus'] = flights
                    cursor2.close()

                    cursor3 = connection.cursor()
                    cursor3.callproc('getAllGuesthouseBookingsActionLogs', [booking_id])
                    actions = dictfetchall(cursor3)
                    cursor3.close()

                    cursor21 = connection.cursor()
                    cursor21.callproc('getAllBookingFeedbackByBookingID', [8, booking_id])
                    flights1 = dictfetchall(cursor21)
                    emp[0]['BookingFeedbacks'] = flights1
                    cursor21.close()

                    if emp[0]['is_invoice']:
                        cursor2 = connection.cursor()
                        invoice_id = emp[0]['invoice_id']
                        print(invoice_id)
                        cursor2.callproc('getallGuesthouseInvoiceActionLog', [invoice_id])
                        invoicess = dictfetchall(cursor2)
                        emp[0]['InvoiceActionLog'] = invoicess
                        cursor2.close()

                    emp[0]['Passangers'] = passanger
                    emp[0]['ActionLogs'] = actions

                    data = {'success': 1, 'Bookings': emp}

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def report_guesthouse_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        filter_by = request.POST.get('filter_by', '')
        from_date = request.POST.get('booking_from_datetime', '')
        if from_date:
            from_date = datetime.strptime(from_date, '%d-%m-%Y')
        to_date = request.POST.get('booking_to_datetime', '')
        if to_date:
            to_date = datetime.strptime(to_date, '%d-%m-%Y')
        booking_status = request.POST.get('booking_status', '')
        company_name = request.POST.get('company_name', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('reportGuesthouseBookings', [filter_by, from_date, to_date, booking_status, company_name ,user_id,user_type])
                emp = dictfetchall(cursor)
                print(emp)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        # print(booking_id)
                        cursor1.callproc('getAllGuesthouseBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()
                        cursor2 = connection.cursor()
                        booking_id = e['id']
                        # print(booking_id)
                        cursor2.callproc('getAllGuesthouseBookingsActionLogs', [booking_id])
                        action = dictfetchall(cursor2)
                        e['Actions'] = action
                        cursor2.close()
                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp}
                return JsonResponse(data)

                # data = {'success': 1, 'Bookings': emp}
                # return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def agent_guesthouse_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        visa_type = request.POST.get('request_type', '')
        page_no = request.POST.get('page_no', '')
        user_id = request.POST.get('user_id', '')
        limit_from = 0
        limit_to = 0
        print('user id')
        print(user_id)
        print(page_no)
        if page_no:
            limit_from = (int(page_no) - 1) * 10
            limit_to = 10
        else:
            limit_from = 0
            limit_to = 2147483647
        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('getAllAgentGuesthouseBookings', [visa_type,limit_from,limit_to,user_id])
                emp = dictfetchall(cursor)
                cursor.close()

                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']

                        cursor1 = connection.cursor()
                        cursor1.callproc('getAllGuesthouseBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        cursor1.close()

                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            cursor2.callproc('getallGuesthouseInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['request_type'] = visa_type
                    except Exception as e:
                        data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp, 'request_type':visa_type}
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


def add_guesthouse(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        guesthouse_id = request.POST.get('guesthouse_id', '')
        corporate_id = request.POST.get('corporate_id', '')
        city_id = request.POST.get('city_id', '')
        guest_house_id = request.POST.get('guest_house_id', '')
        guest_house_code = request.POST.get('guest_house_code', '')
        guest_house_name = request.POST.get('guest_house_name', '')
        area_location = request.POST.get('area_location', '')
        contact_person_name = request.POST.get('contact_person_name', '')
        contact_person_no = request.POST.get('contact_person_no', '')
        contact_person_email = request.POST.get('contact_person_email', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('addGuesthouseDetails', [user_id,user_type,guesthouse_id,corporate_id,city_id,guest_house_id,guest_house_code,
                guest_house_name,area_location,contact_person_name,contact_person_no,contact_person_email])
                emp = dictfetchall(cursor)
                cursor.close()

                data = {'success': 1, 'message': "Guesthouse Added/Edited Successfully ..!"}
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


def add_guesthouses_amenities(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        guesthouse_id = request.POST.get('guesthouse_id', '')
        bed_type = request.POST.get('bed_type', '')
        tv = request.POST.get('tv', '')
        queen_size_bed = request.POST.get('queen_size_bed', '')
        ac = request.POST.get('ac', '')
        functional_living_area = request.POST.get('functional_living_area', '')
        power_backup = request.POST.get('power_backup', '')
        geyser = request.POST.get('geyser', '')
        elevator = request.POST.get('elevator', '')
        cctv_cameras = request.POST.get('cctv_cameras', '')
        security = request.POST.get('security', '')
        fire_extinguisher = request.POST.get('fire_extinguisher', '')
        room_facilities = request.POST.get('room_facilities', '')
        intercom = request.POST.get('intercom', '')
        fan = request.POST.get('fan', '')
        telephone = request.POST.get('telephone', '')
        wifi = request.POST.get('wifi', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('addGuesthouseAmenitiesDetails', [user_id,user_type,guesthouse_id,bed_type,tv,queen_size_bed,
                ac,functional_living_area,power_backup,geyser,elevator,cctv_cameras, security, fire_extinguisher, room_facilities,
                intercom,fan, telephone, wifi])
                emp = dictfetchall(cursor)

                cursor.close()

                data = {'success': 1, 'message': "Guesthouse Added/Edited Successfully ..!"}
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


def add_guesthouses_rooms(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        guesthouse_id = request.POST.get('guesthouse_id', '')
        room_id = request.POST.get('room_id', '')
        room_code = request.POST.get('room_code', '')
        room_number = request.POST.get('room_number', '')
        room_name = request.POST.get('room_name', '')
        room_size_id = request.POST.get('room_size_id', '')
        room_per_night_fee = request.POST.get('room_per_night_fee', '')
        room_fixed_fee = request.POST.get('room_fixed_fee', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('addGuesthouseRoomsDetails', [user_id,user_type,guesthouse_id,room_id,room_code,room_number,room_name,room_size_id,room_per_night_fee,room_fixed_fee])
                emp = dictfetchall(cursor)

                cursor.close()

                data = {'success': 1, 'message': "Guesthouse Room Added/Edited Successfully ..!"}
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


def get_guesthouse_rooms(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        visa_type = request.POST.get('guesthouse_id', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('getAllGuesthouseRooms', [visa_type])
                emp = dictfetchall(cursor)
                cursor.close()

                data = {'success': 1, 'Rooms': emp}
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


def get_guesthouse_rooms_type(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('getAllGuesthouseRoomsType', [])
                emp = dictfetchall(cursor)
                cursor.close()

                data = {'success': 1, 'Types': emp}
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


def add_guesthouses_room_types(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        user_id = request.POST.get('user_id', '')
        room_id = request.POST.get('room_id', '')
        room_code = request.POST.get('room_code', '')
        room_number = request.POST.get('room_number', '')

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                cursor.callproc('addGuesthouseRoomTypesDetails', [user_id,user_type,room_id,room_code,room_number])
                emp = dictfetchall(cursor)

                cursor.close()

                data = {'success': 1, 'message': "Guesthouse Room Type Added/Edited Successfully ..!"}
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


def delete_guesthouse(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        guesthouse_id = request.POST.get('guesthouse_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCorporateGuesthouse', [user_id,user_type,guesthouse_id])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Guesthouse Deleted Successfully..!"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_guesthouseroom(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        guesthouse_id = request.POST.get('guesthouse_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCorporateGuesthouseRooms', [user_id,user_type,guesthouse_id])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Guesthouse Deleted Successfully..!"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def delete_guesthouseroomtype(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        user_id = request.POST.get('user_id', '')

        guesthouse_id = request.POST.get('guesthouse_id', '')

        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = {}
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                cursor = connection.cursor()
                try:
                    cursor.callproc('deleteCorporateGuesthouseRoomsType', [user_id,user_type,guesthouse_id])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Corporate Guesthouse Deleted Successfully..!"}
                    cursor.close()
                    return JsonResponse(data)
                except Exception as e:
                    print(e)
                    data = {'success': 1, 'message': "Error in Data Insert"}
                    return JsonResponse(data)

            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)










def upload_frro_doc_get_path(file_name_string, file_extension):
    a = datetime.now()
    file_name_add = str(int(a.strftime('%d%m%Y%H%M')))
    modified_name = "{}_{}_{}".format(file_name_add, '1', str('FRRO.'+file_extension))
    imgdata = base64.b64decode(file_name_string)
    filename = os.path.join(settings.MEDIA_ROOT, 'frro_doc/', modified_name)  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
        f.write(imgdata)
        f.close()
    download_path = os.path.join(settings.MEDIA_URL,'frro_doc/', str(filename.rsplit('/', 1)[-1]))
    return download_path


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
    ]

