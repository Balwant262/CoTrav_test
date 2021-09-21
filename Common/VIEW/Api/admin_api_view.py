from datetime import date, datetime
import sys
from django.http import JsonResponse
from django.db import connection
import datetime
from Common.VIEW.Api.api_views import getUserinfoFromAccessToken, dictfetchall


def admin_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
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
                    cursor.callproc('getAllAdminTaxiBookings', [corporate_id,booking_type,limit_from,limit_to])
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


def admin_accept_taxi_booking(request):
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
                    cursor.callproc('acceptAdminTaxiBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Accepted Successfully"}
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


def admin_reject_taxi_booking(request):
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
                    cursor.callproc('rejectAdminTaxiBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    print(emp)
                    cursor.close()
                    data = {'success': 1, 'message': "Booking Reject Successfully"}
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


def admin_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
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
                    cursor.callproc('getAllAdminBusBookings', [corporate_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        print(booking_id)
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

                    data = {'success': 1, 'Bookings': emp,'booking_type':booking_type}
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


def admin_accept_bus_booking(request):
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
                    cursor.callproc('acceptAdminBusBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Accepted Successfully"}
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


def admin_reject_bus_booking(request):
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
                    cursor.callproc('rejectAdminBusBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Rejected Successfully"}
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

############################### TRAIN #################################

def admin_train_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
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
                    cursor.callproc('getAllAdminTrainBookings', [corporate_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        print(booking_id)
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

                    data = {'success': 1, 'Bookings': emp,'booking_type':booking_type}
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


def admin_accept_train_booking(request):
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
                    cursor.callproc('acceptAdminTrainBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Accepted Successfully"}
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


def admin_reject_train_booking(request):
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
                    cursor.callproc('rejectAdminTrainBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Rejected Successfully"}
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


############################### Hotels #################################

def admin_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
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
                    cursor.callproc('getAllAdminHotelBookings', [corporate_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)

                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        print(booking_id)
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

                    data = {'success': 1, 'Bookings': emp,'booking_type':booking_type}
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


def admin_accept_hotel_booking(request):
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
                    cursor.callproc('acceptAdminHotelBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Accepted Successfully"}
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


def admin_reject_hotel_booking(request):
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
                    cursor.callproc('rejectAdminHotelBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Rejected Successfully"}
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

############################### Flight #################################


def admin_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        corporate_id = request.POST.get('corporate_id', '')
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
                cursor = connection.cursor()
                cursor.callproc('getAllAdminFlightBookings', [corporate_id,booking_type,limit_from,limit_to])
                emp = dictfetchall(cursor)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        print(booking_id)
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

                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp,'booking_type':booking_type}
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


def admin_accept_flight_booking(request):
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
                    cursor.callproc('acceptAdminFlightBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Accepted Successfully"}
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


def admin_reject_flight_booking(request):
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
                    cursor.callproc('rejectAdminFlightBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bookings': emp, 'message': "Booking Rejected Successfully"}
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


def admin_verify_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
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
                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        print(booking_id)
                        cursor.callproc('verifyInvoiceAdminTaxiBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_revise_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        print(booking_id)
                        cursor.callproc('correctionInvoiceRequestAdminTaxiBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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


def admin_verify_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
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

                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        cursor = connection.cursor()
                        cursor.callproc('verifyInvoiceAdminBusBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_revise_bus_bookings(request):
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        print(booking_id)

                        cursor.callproc('correctionInvoiceRequestAdminBusBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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


def admin_verify_train_bookings(request):
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
                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        print(booking_id)
                        cursor.callproc('verifyInvoiceAdminTrainBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_revise_train_bookings(request):
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        print(booking_id)
                        cursor.callproc('correctionInvoiceRequestAdminTrainBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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


def admin_verify_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
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
                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        cursor.callproc('verifyInvoiceAdminHotelBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_revise_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        cursor.callproc('correctionInvoiceRequestAdminHotelBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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


def admin_verify_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
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
                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        cursor.callproc('verifyInvoiceAdminFlightBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_revise_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        print(booking_id)
                        cursor.callproc('correctionInvoiceRequestAdminFlightBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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


def admin_verify_visa_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
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
                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        cursor.callproc('verifyInvoiceAdminVisaBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_verify_frro_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
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
                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        cursor.callproc('verifyInvoiceAdminFrroBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_revise_visa_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        print(booking_id)
                        cursor.callproc('correctionInvoiceRequestAdminVisaBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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


def admin_revise_frro_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        print(booking_id)
                        cursor.callproc('correctionInvoiceRequestAdminFrroBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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


def accept_bill(request):
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
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('acceptAdminBill', [user_id,user_type,booking_id,user_comment])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Bill Accepted Successfully"}
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


def reject_bill(request):
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
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('rejectAdminBill', [user_id,user_type,booking_id,user_comment])
                    company = dictfetchall(cursor)
                    if company:
                        data = {'success': 0, 'message': company}
                    else:
                        data = {'success': 1, 'message': "Bill Accepted Successfully"}
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


def admin_dashboard_sales_by_month(request):
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
        flag_visa = 1
        flag_frro = 1

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getSalesByMonth', [year, month, 1, user.corporate_id, user.id , flag_taxi , flag_bus , flag_train , flag_flight , flag_hotel , flag_visa , flag_frro ])
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


def admin_dashboard_bookings_by_month(request):
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
        flag_visa = 1
        flag_frro = 1

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getDashboardBookingsByMonth', [year, month , 1, user.corporate_id, user.id , flag_taxi , flag_bus , flag_train , flag_flight , flag_hotel, flag_visa, flag_frro ] )
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


def admin_dashboard_sales_for_six_months(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        month = int(request.POST.get('month', ''))
        year = int(request.POST.get('year', ''))
        print("month and year")
        print(month)
        print(year)
        dt_date = datetime.datetime(year, month, 25)

        print(dt_date)

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getSalesForPrevSixMonths', [dt_date, 1, 1, user.corporate_id, user.id])
                    taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesForPrevSixMonths', [dt_date, 2, 1, user.corporate_id, user.id])
                    bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesForPrevSixMonths', [dt_date, 3, 1, user.corporate_id, user.id])
                    train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesForPrevSixMonths', [dt_date, 4, 1, user.corporate_id, user.id])
                    flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesForPrevSixMonths', [dt_date, 5, 1, user.corporate_id, user.id])
                    hotel = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesForPrevSixMonths', [dt_date, 6, 1, user.corporate_id, user.id])
                    visa = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesForPrevSixMonths', [dt_date, 7, 1, user.corporate_id, user.id])
                    frro = dictfetchall(cursor)
                    cursor.close()

                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Sales': [taxi, bus, train, flight, hotel, visa, frro]}

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


def admin_dashboard_bookings_for_six_months(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        month = int(request.POST.get('month', ''))
        year = int(request.POST.get('year', ''))
        print("month and year")
        print(month)
        print(year)
        dt_date = datetime.datetime(year, month, 25)

        print(dt_date)

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 1, 1, user.corporate_id, user.id])
                    taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 2, 1, user.corporate_id, user.id])
                    bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 3, 1, user.corporate_id, user.id])
                    train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 4, 1, user.corporate_id, user.id])
                    flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 5, 1, user.corporate_id, user.id])
                    hotel = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 6, 1, user.corporate_id, user.id])
                    visa = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getBookingsForPrevSixMonths', [dt_date, 7, 1, user.corporate_id, user.id])
                    frro = dictfetchall(cursor)
                    cursor.close()

                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Sales': [taxi, bus, train, flight, hotel, visa, frro]}
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


def admin_dashboard_sales_by_city(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        # serveType = int(request.POST.get('serveType', ''))

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [1, 1, user.corporate_id, user.id])
                    city_taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [2, 1, user.corporate_id, user.id])
                    city_bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [3, 1, user.corporate_id, user.id])
                    city_train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [4, 1, user.corporate_id, user.id])
                    city_flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [5, 1, user.corporate_id, user.id])
                    city_hotel = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [6, 1, user.corporate_id, user.id])
                    city_visa = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCity', [7, 1, user.corporate_id, user.id])
                    city_frro = dictfetchall(cursor)
                    cursor.close()

                    print('## dashboard_sales_by_city ##')
                    print(city_taxi)
                    print(city_bus)
                    print(city_train)
                    print(city_flight)
                    print(city_hotel)
                    print(city_visa)
                    print(city_frro)
                    print('#####')

                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Sales': [city_taxi, city_bus, city_train, city_flight, city_hotel, city_visa,city_frro]}
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


def admin_dashboard_sales_by_city_for_month(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        # serveType = int(request.POST.get('serveType', ''))
        month = request.POST.get('month', '')
        year = request.POST.get('year', '')
        yr = year
        mnth =  month

        print("year and month")
        print(yr)
        print(mnth)

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCityForMonth', [1, yr, mnth , 1, user.corporate_id, user.id])
                    city_taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCityForMonth', [2, yr, mnth , 1, user.corporate_id , user.id])
                    city_bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCityForMonth', [3, yr, mnth, 1, user.corporate_id , user.id])
                    city_train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCityForMonth', [4, yr, mnth, 1, user.corporate_id , user.id])
                    city_flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCityForMonth', [5, yr, mnth, 1, user.corporate_id , user.id])
                    city_hotel = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCityForMonth', [6, yr, mnth, 1, user.corporate_id, user.id])
                    city_visa = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getSalesByCityForMonth', [7, yr, mnth, 1, user.corporate_id, user.id])
                    city_frro = dictfetchall(cursor)
                    cursor.close()
                    print("dsadasdsadasdsadsadas")
                    print(city_frro)
                    print("dasdsadasdas")
                    data = {'success': 1, 'Sales': [city_taxi, city_bus, city_train, city_flight, city_hotel, city_visa, city_frro]}
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


def admin_dashboard_taxable_amount_table(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        # serveType = int(request.POST.get('serveType', ''))
        frm_date = request.POST.get('from_date', '')
        to_date = request.POST.get('to_date', '')
        print("tax from to date")
        print(frm_date)
        print(to_date)

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('getTaxableDataForDashboard', [1, frm_date, to_date , user.id , 1])
                    city_taxi = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getTaxableDataForDashboard', [2, frm_date, to_date , user.id , 1])
                    city_bus = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getTaxableDataForDashboard', [3, frm_date, to_date , user.id , 1])
                    city_train = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getTaxableDataForDashboard', [4, frm_date, to_date , user.id , 1])
                    city_flight = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getTaxableDataForDashboard', [5, frm_date, to_date , user.id , 1])
                    city_hotel = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getTaxableDataForDashboard', [6, frm_date, to_date, user.id, 1])
                    city_visa = dictfetchall(cursor)
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('getTaxableDataForDashboard', [7, frm_date, to_date, user.id, 1])
                    city_frro = dictfetchall(cursor)
                    cursor.close()


                    print('## city wise ##')
                    print(city_taxi)
                    print(city_bus)
                    print(city_train)
                    print(city_flight)
                    print(city_hotel)
                    print('#####')

                    # emp = {'taxi':43,'bus':73,'train':86,'flight':62,'hotel':77}
                    data = {'success': 1, 'Tax': [city_taxi, city_bus, city_train, city_flight, city_hotel, city_visa, city_frro]}
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


def dashboard_search_admin_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        whereClause = request.POST.get('whereClause', '')
        serveType = request.POST.get('serveType', '')

        bookingType = int(request.POST.get('booking_type', ''))

        print(whereClause)
        print(serveType)

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            user = getUserinfoFromAccessToken(user_token[1], user_type)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('dashboardSearch', [serveType,whereClause,bookingType])
                    search_result = dictfetchall(cursor)
                    cursor.close()

                    data = {'success': 1, 'Result': search_result}
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



def admin_report_invoice(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        service_type = int(request.POST.get('service_type', ''))
        date_type = int(request.POST.get('date_type', ''))

        from_date = request.POST.get('from_date', '')
        #from_date = datetime.datetime.strptime(from_date, '%m-%d-%Y %H:%M:%S')
        if from_date:
            from_date = from_date + ' 00:00:00'
            from_date_object = datetime.datetime.strptime(from_date, '%d-%m-%Y %H:%M:%S')
            from_date = from_date_object.strftime("%Y-%m-%d (%H:%M:%S.%f)")

            print("from_date......")
            print(from_date)

        to_date = request.POST.get('to_date', '')
        if to_date:

            #to_date = datetime.datetime.strptime(to_date, '%m-%d-%Y %H:%M:%S')

            to_date = to_date + ' 00:00:00'
            to_date_object = datetime.datetime.strptime(to_date, '%d-%m-%Y %H:%M:%S')
            to_date = to_date_object.strftime("%Y-%m-%d (%H:%M:%S.%f)")

        corporate_id = int(request.POST.get('corporate_id', ''))

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('invoiceReport', [service_type , date_type , from_date , to_date , corporate_id])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Reports': emp}
                    #print(data)
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


def admin_report_client_bills(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        service_type = int(request.POST.get('service_type', ''))
        bill_status = int(request.POST.get('bill_status', ''))

        from_date = request.POST.get('from_date', '')
        #from_date = datetime.datetime.strptime(from_date, '%m-%d-%Y %H:%M:%S')

        from_date = from_date + ' 00:00:00'
        from_date_object = datetime.datetime.strptime(from_date, '%d-%m-%Y %H:%M:%S')
        from_date = from_date_object.strftime("%Y-%m-%d (%H:%M:%S.%f)")

        print("from_date......")
        print(from_date)

        to_date = request.POST.get('to_date', '')
        #to_date = datetime.datetime.strptime(to_date, '%m-%d-%Y %H:%M:%S')

        to_date = to_date + ' 00:00:00'
        to_date_object = datetime.datetime.strptime(to_date, '%d-%m-%Y %H:%M:%S')
        to_date = to_date_object.strftime("%Y-%m-%d (%H:%M:%S.%f)")

        corporate_id = int(request.POST.get('corporate_id', ''))

        user = {}
        user_token = req_token.split()
        if user_token[0] == 'Token':
            try:
                user = getUserinfoFromAccessToken(user_token[1], user_type)
            except Exception as e:
                data = {'success': 0, 'message': "Missing Parameter Value Try Again..."}
                return JsonResponse(data)
            if user:
                try:
                    cursor = connection.cursor()
                    cursor.callproc('reportsClientBills', [service_type , corporate_id , bill_status , from_date , to_date ])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    data = {'success': 1, 'Bill': emp}
                    #print(data)
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


def admin_frro_request(request):
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
                cursor.callproc('getAllAdminFrroRequests', [visa_type,limit_from,limit_to,user_id,user_type])
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
                            cursor2.callproc('getallVisaInvoiceActionLog', [invoice_id])
                            invoicess = dictfetchall(cursor2)
                            e['InvoiceActionLog'] = invoicess
                            cursor2.close()

                        e['visa_type'] = visa_type
                    except Exception as e:
                        data = {'success': 0, 'message': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Frros': emp, 'request_type':visa_type}
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


def admin_verify_guesthouse_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
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
                    for booking_id, invoice_id in zip(verify_id, invoice_ids):
                        cursor.callproc('verifyInvoiceAdminGuesthouseBookings', [booking_id,user_id,user_type,invoice_id])
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


def admin_revise_guesthouse_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']

        verify_id = request.POST.getlist('verify_id', '')
        corporate_ids = request.POST.getlist('corporate_id', '')
        invoice_ids = request.POST.getlist('invoice_id', '')
        invoice_comments = request.POST.getlist('invoice_comments', '')
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
                    for booking_id, invoice_id, invoice_comment in zip(verify_id, invoice_ids, invoice_comments):
                        cursor.callproc('correctionInvoiceRequestAdminGuesthouseBooking', [booking_id,user_id,user_type,invoice_id,invoice_comment])
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

