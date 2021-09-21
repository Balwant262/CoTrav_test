from django.http import JsonResponse
from django.db import connection
from Common.VIEW.Api.api_views import getUserinfoFromAccessToken, dictfetchall
from datetime import datetime
from Common.email_settings import AcceptBooking_Email, FCM, RejectBooking_Email
from threading import Thread

def approver_1_taxi_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        approver_1_id = request.POST.get('approver_1_id', '')
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
                cursor.callproc('getAllApprover_1TaxiBookings', [approver_1_id,booking_type,limit_from,limit_to])
                emp = dictfetchall(cursor)
                cursor.close()
                for e in emp:
                    try:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllTaxiBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type
                        cursor1.close()
                    except Exception as e:
                        data = {'success': 0, 'error': getattr(e, 'message', str(e))}
                        return JsonResponse(data)
                data = {'success': 1, 'Bookings': emp}
                return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def approver_1_accept_taxi_booking(request):
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
                    cursor.callproc('acceptApprover_1TaxiBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Approved Successfully"}
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

                    add_booking_email = AcceptBooking_Email()
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


def approver_1_reject_taxi_booking(request):
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
                    cursor.callproc('rejectApprover_1TaxiBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Rejected Successfully"}
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

########################## BUS #################3

def approver_1_bus_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        approver_1_id = request.POST.get('approver_1_id', '')
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
                    cursor.callproc('getAllApprover_1BusBookings', [approver_1_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllBusBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type
                        cursor1.close()
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


def approver_1_accept_bus_booking(request):
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
                    cursor.callproc('acceptApprover_1BusBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    print(emp)
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
                    print("i m hererererere")

                    add_booking_email = AcceptBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Bus"))
                    thread.start()

                    data = {'success': 1, 'message': "Booking Approved Successfully"}

                    return JsonResponse(data)
                except Exception as e:
                    print("exception")
                    print(e)
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


def approver_1_reject_bus_booking(request):
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
                    cursor.callproc('rejectApprover_1BusBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Rejected Successfully"}
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


########################## TRAIN #################3


def approver_1_train_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        approver_1_id = request.POST.get('approver_1_id', '')
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
                    cursor.callproc('getAllApprover_1TrainBookings', [approver_1_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllTrainBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type
                        cursor1.close()
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


def approver_1_accept_train_booking(request):
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
                    cursor.callproc('acceptApprover_1TrainBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Approved Successfully"}
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

                    add_booking_email = AcceptBooking_Email()
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


def approver_1_reject_train_booking(request):
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
                    cursor.callproc('rejectApprover_1TrainBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Rejected Successfully"}
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



########################## hotel #################3

def approver_1_hotel_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        approver_1_id = request.POST.get('approver_1_id', '')
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
                    cursor.callproc('getAllApprover_1HotelBookings', [approver_1_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllHotelBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type
                        cursor1.close()
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


def approver_1_accept_hotel_booking(request):
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
                    cursor.callproc('acceptApprover_1HotelBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Approved Successfully"}
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

                    add_booking_email = AcceptBooking_Email()
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


def approver_1_reject_hotel_booking(request):
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
                    cursor.callproc('rejectApprover_1HotelBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Rejected Successfully"}
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


########################## Flight #################3

def approver_1_flight_bookings(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        approver_1_id = request.POST.get('approver_1_id', '')
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
                    cursor.callproc('getAllApprover_1FlightBookings', [approver_1_id,booking_type,limit_from,limit_to])
                    emp = dictfetchall(cursor)
                    cursor.close()
                    for e in emp:
                        cursor1 = connection.cursor()
                        booking_id = e['id']
                        cursor1.callproc('getAllFlightBookingPassangers', [booking_id])
                        passanger = dictfetchall(cursor1)
                        e['Passangers'] = passanger
                        e['booking_type'] = booking_type
                        cursor1.close()
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


def approver_1_accept_flight_booking(request):
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
                    cursor.callproc('acceptApprover_1FlightBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Approved Successfully"}
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

                    add_booking_email = AcceptBooking_Email()
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


def approver_1_reject_flight_booking(request):
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
                    cursor.callproc('rejectApprover_1FlightBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Rejected Successfully"}
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


def approver_2_accept_visa_booking(request):
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
                    cursor.callproc('acceptApprover_1VisaBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Visa Request Approved Successfully..!"}
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('viewVisadDetails', [booking_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllAgentVisaFamily', [booking_id])
                    passanger = dictfetchall(cursor1)
                    company[0]['FamailyDocs'] = passanger
                    cursor1.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllAgentVisaEmployeeDocuments', [booking_id])
                    passanger1 = dictfetchall(cursor2)
                    company[0]['EmployeesDocs'] = passanger1
                    cursor2.close()

                    add_booking_email = AcceptBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(company, "Visa"))
                    thread.start()

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': 'Visa Request Not Approved .!', 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def approver_2_reject_visa_booking(request):
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
                    cursor.callproc('rejectApprover_1VisaBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Visa Request Rejected Successfully..!"}
                    cursor.close()

                    cursor = connection.cursor()
                    cursor.callproc('viewVisadDetails', [booking_id])
                    company = dictfetchall(cursor)
                    cursor.close()

                    cursor1 = connection.cursor()
                    cursor1.callproc('getAllAgentVisaFamily', [booking_id])
                    passanger = dictfetchall(cursor1)
                    company[0]['FamailyDocs'] = passanger
                    cursor1.close()

                    cursor2 = connection.cursor()
                    cursor2.callproc('getAllAgentVisaEmployeeDocuments', [booking_id])
                    passanger1 = dictfetchall(cursor2)
                    company[0]['EmployeesDocs'] = passanger1
                    cursor2.close()

                    add_booking_email = RejectBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(company, "Visa"))
                    thread.start()

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message':'Visa Request Not Rejected..!', 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def approver_2_accept_frro_booking(request):
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
                    cursor.callproc('acceptApprover_1FrroBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "FRRO Request Approved Successfully..!"}
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

                    add_booking_email = AcceptBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(company, "Frro"))
                    thread.start()

                    return JsonResponse(data)
                except Exception as e:
                    data = {'success': 0, 'message': 'Frro Request Not Approved .!', 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


def approver_2_reject_frro_booking(request):
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
                    cursor.callproc('rejectApprover_1FrroBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "FRRO Request Rejected Successfully..!"}
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
                    data = {'success': 0, 'message':'FRRO Request Not Rejected..!', 'error': getattr(e, 'message', str(e))}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'error': "User Information Not Found"}
                return JsonResponse(data)
        else:
            data = {'success': 0, 'Corporates': "Token Not Found"}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)


###################################### Guest House ##############


def approver_1_accept_guesthouse_booking(request):
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
                    cursor.callproc('acceptApprover_1GuesthouseBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Approved Successfully"}
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

                    add_booking_email = AcceptBooking_Email()
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Guesthouse"))
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


def approver_1_reject_guesthouse_booking(request):
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
                    cursor.callproc('rejectApprover_1GuesthouseBookings', [user_id,user_type,booking_id,user_comment])
                    emp = dictfetchall(cursor)
                    data = {'success': 1, 'message': "Booking Rejected Successfully"}
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
                    thread = Thread(target=add_booking_email.send_email_sms_ntf, args=(emp, "Guesthouse"))
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

