from datetime import datetime
import sys
from threading import Thread
import datetime
from django.http import JsonResponse
from django.db import connection
from Common.VIEW.Api.api_views import getUserinfoFromAccessToken, dictfetchall
from Common.email_settings import RejectBooking_Email


def spoc_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        spoc_id = request.POST.get('spoc_id', '')
        user = {}
        booking_type = request.POST.get('booking_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0
        print(page_no)
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
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllSPOCTaxiBookings', [spoc_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        cursor1.close()
                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            print(invoice_id)
                            print("iiiiiiinnnnnvvvvvoooo")
                            cursor2.callproc('getallTaxiInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type

                    data = {'success': 1, 'Bookings': emp, 'booking_type':booking_type}
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


def spoc_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        spoc_id = request.POST.get('spoc_id', '')
        user = {}
        booking_type = request.POST.get('booking_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0
        print(page_no)
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
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllSPOCBusBookings', [spoc_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllBusBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        cursor1.close()
                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            print(invoice_id)
                            print("iiiiiiinnnnnvvvvvoooo")
                            cursor2.callproc('getallBusInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type

                    data = {'success': 1, 'Bookings': emp, 'booking_type':booking_type}
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


def spoc_train_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        spoc_id = request.POST.get('spoc_id', '')
        user = {}
        booking_type = request.POST.get('booking_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0
        print(page_no)
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
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllSPOCTrainBookings', [spoc_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllTrainBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        cursor1.close()
                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            print(invoice_id)
                            print("iiiiiiinnnnnvvvvvoooo")
                            cursor2.callproc('getallTrainInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type

                    data = {'success': 1, 'Bookings': emp, 'booking_type':booking_type}
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


def spoc_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        spoc_id = request.POST.get('spoc_id', '')
        user = {}
        booking_type = request.POST.get('booking_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0
        print(page_no)
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
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllSPOCHotelBookings', [spoc_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllHotelBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        cursor1.close()
                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            print(invoice_id)
                            print("iiiiiiinnnnnvvvvvoooo")
                            cursor2.callproc('getallHotelInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type

                    data = {'success': 1, 'Bookings': emp, 'booking_type':booking_type}
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


def spoc_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        spoc_id = request.POST.get('spoc_id', '')
        user = {}
        booking_type = request.POST.get('booking_type', '')
        page_no = request.POST.get('page_no', '')
        limit_from = 0
        limit_to = 0
        print(page_no)
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
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getAllSPOCFlightBookings', [spoc_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllFlightBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        cursor1.close()
                        if e['is_invoice']:
                            cursor2 = connection.cursor()
                            invoice_id = e['invoice_id']
                            print(invoice_id)
                            print("iiiiiiinnnnnvvvvvoooo")
                            cursor2.callproc('getallFlightInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type

                    data = {'success': 1, 'Bookings': emp, 'booking_type':booking_type}
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


def spoc_reject_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocTaxiBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Cancelled Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewTaxiBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Taxi"))
                    thread.start()

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


def spoc_reject_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocBusBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    print(emp)
                    data = {'success': 1, 'message': "Booking Cancelled Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewBusBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllBusBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Bus"))
                    thread.start()

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


def spoc_reject_train_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocTrainBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Cancelled Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewTrainBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllTrainBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Train"))
                    thread.start()

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


def spoc_reject_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocFlightBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Cancelled Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewFlightBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllFlightBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Flight"))
                    thread.start()

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


def spoc_reject_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocHotelBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Cancelled Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewHotelBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllHotelBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Hotel"))
                    thread.start()

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


def spoc_reject_visa_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocVisaBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Cancelled Successfully"}
                    cursor.close()

                    # cursor2 = connection.cursor()
                    # cursor2.callproc('viewTaxiBooking', [booking_id])
                    # emp = dictfetchall(cursor2)
                    # cursor2.close()
                    #
                    # cursor1 = connection.cursor()
                    # cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                    # passanger = dictfetchall(cursor1)
                    # emp[0]['Passangers'] = passanger
                    # cursor1.close()
                    #
                    # add_booking_email = RejectBooking_Email()
                    # thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Hotel"))
                    # thread.start()

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


def spoc_accept_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('acceptSpocTaxiBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Accepted Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewTaxiBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Taxi"))
                    thread.start()

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


def spoc_accept_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('acceptSpocBusBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    print(emp)
                    data = {'success': 1, 'message': "Booking Accepted Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewBusBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllBusBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Bus"))
                    thread.start()

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


def spoc_accept_train_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('acceptSpocTrainBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Accepted Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewTrainBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllTrainBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Train"))
                    thread.start()

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


def spoc_accept_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('acceptSpocFlightBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Accepted Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewFlightBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllFlightBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Flight"))
                    thread.start()

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


def spoc_accept_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('acceptSpocHotelBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Accepted Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewHotelBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllHotelBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Hotel"))
                    thread.start()

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


def spoc_verify_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocTaxiBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocTaxiBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_verify_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocBusBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocBusBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_verify_train_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocTrainBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_train_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocTrainBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_verify_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocHotelBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocHotelBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_verify_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocFlightBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocFlightBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_verify_visa_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocVisaBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_verify_frro_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocFrroBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_visa_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocVisaBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_frro_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocFrroBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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




def spoc_dashboard_bookings_for_six_months(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        month = int(request.POST.get('month', ''))
        year = int(request.POST.get('year', ''))
        print("month and year")
        print(month)
        print(year)
        #dt_date = datetime.datetime(year, month, 25)
        dt_date = datetime.datetime.strptime(str(25)+"-"+str(month)+'-'+str(year), '%d-%m-%Y')

        print(dt_date)

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 1, 4, user.corporate_id , user.id ])
                    taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 2, 4, user.corporate_id , user.id ])
                    bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 3, 4, user.corporate_id , user.id ])
                    train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 4, 4, user.corporate_id , user.id ])
                    flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 5, 4, user.corporate_id , user.id ])
                    hotel = dictfetchall(cursor)
                    cursor.close()

                    print(taxi)
                    print(bus)
                    print(train)
                    print(flight)
                    print(hotel)

                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Sales': [taxi, bus, train, flight, hotel]}
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


def spoc_dashboard_bookings_by_month(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        month = request.POST.get('month', '')
        year = request.POST.get('year', '')
        print("month and year")
        print(month)
        print(year)

        flag_taxi = 1
        flag_bus = 1
        flag_train = 1
        flag_flight = 1
        flag_hotel = 1

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getDashboardBookingsByMonth', [year, month, 4, user.corporate_id , user.id , flag_taxi , flag_bus , flag_train , flag_flight , flag_hotel ])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    print('### sales data ###')
                    print(emp)
                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Sales': emp}
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


def spoc_cancel_frro_booking(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocFrroBookings', [booking_id, user_id, user_type, user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Frro Request Cancelled Successfully"}
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('viewFrroDetails', [booking_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllAgentFrroEmployeeDocuments', [booking_id])
                    passanger1 = dictfetchall(cursor2)
                    company[0]['EmployeesDocs'] = passanger1
                    cursor2.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(company, "Frro"))
                    thread.start()

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


def spoc_reject_guesthouse_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        booking_id = request.POST.get('booking_id', '')
        user_id = request.POST.get('user_id', '')
        user_comment = request.POST.get('user_comment', '')
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
                    cursor.callproc('rejectSpocGuesthouseBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Cancelled Successfully"}
                    cursor.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('viewGuesthouseBooking', [booking_id])
                    emp = dictfetchall(cursor2)
                    cursor2.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllGuesthouseBookingPassangers', [booking_id])
                    passanger = dictfetchall(cursor1)
                    emp[0]['Passangers'] = passanger
                    cursor1.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Hotel"))
                    thread.start()

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



def spoc_verify_guesthouse_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id in zip(verify_id, corporate_ids, invoice_ids):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('verifyInvoiceSpocGuesthouseBookings', [booking_id,user_id,user_type,corporate_id,invoice_id])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Verify Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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


def spoc_revise_guesthouse_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
        user_id = request.POST.get('user_id', '')
        print(verify_id)
        print(corporate_ids)
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
                    for booking_id, corporate_id, invoice_id, invoice_comment in zip(verify_id, corporate_ids, invoice_ids, invoice_comments):
                        print(booking_id)
                        print(corporate_id)
                        cursor.callproc('correctionInvoiceRequestSpocGuesthouseBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
                        emp = dictfetchall(cursor)
                        print(emp)
                    cursor.close()

                    data = {'success': 1, 'message': "invoice Revise Successfully"}
                    return JsonResponse(data)
                except Exception as e:
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
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

