from datetime import datetime, timezone

import pytz
from django.db import connection
from django.http import JsonResponse

from Common.VIEW.Api.api_views import dictfetchall

user_type = 10
user_id = 1

corporate_id = 1
booking_email = ""
entity_id = 1
spoc_id = 1
group_id = 1
subgroup_id = 1

tour_type = 1
pickup_city = 276
pickup_location = "Pune, Maharashtra, India"
pickup_location_train = 412
drop_location = "Mumbai, Maharashtra, India"
drop_location_train = 323
pickup_datetime = "2019-07-24 05:00:00"
booking_datetime = "2019-07-24 03:00:00"
taxi_type = "1"
package_id = "1"
no_of_days = "1"
assessment_code = "1"
assessment_city_id = "1"
reason_booking = "Test From Script"
no_of_seats = "2"
employees = "1,2"

vendor_booking_id = "1"
operator_id = "1"
driver_id ="1"
taxi_id = "1"

management_fee = "100"
tax_on_management_fee = "100"
tax_on_management_fee_percentage = "18"
management_fee_igst = "18"
management_fee_cgst = "0"
management_fee_sgst = "0"
management_fee_igst_rate = "18"
management_fee_cgst_rate = "0"
management_fee_sgst_rate = "0"
igst = "18"
igst_amount = "18"
cgst = "0"
cgst_amount = "0"
sgst = "0"
sgst_amount = "0"

hours_done = "10"
allowed_hours = "10"
extra_hours = "0"
charge_hour = "0"
days = "1"
start_km = "0"
end_km = "100"
kms_done = "100"
allowed_kms = "100"
extra_kms = "0"
extra_km_rate ="0"
tax_mng_amt ="0"

cotrav_billing_entity = "1"
bb_entity = "1"
radio_rate = "1"

base_rate = "1200"
extra_hr_charges = "0"
extra_km_charges ="0"
driver_allowance ="0"
total_excluding_tax = "0"
other_charges = "0"
total = "2000"
sub_total = "2200"

bus_type = "1"
preferred_bus = "msrtc luxury bus"
ticket_no = "TICKET113213"
pnr_no = "PNR12345"
assign_bus_type_id = "1"
seat_no = "11"
portal_used = "1"
operator_name = "Mahesh Kumar"
operator_contact = "9876543131"
boarding_point = "Pune Bus Stand"
boarding_datetime = "2019-07-23 12:00:00"

oper_ticket_price = "1000"
oper_commission = "200"
oper_commission_type = "1"
oper_cotrav_billing_entity = "1"
oper_igst = "12"
oper_cgst = "0"
oper_sgst = "0"
client_ticket_path = ""
vender_ticket_path = ""
preferred_area = ""
assign_room_type = ""
agent_booking_id = ""
comment = "test"
usage_type = "Flight"
journey_type = "One Way"
flight_class = "Economy"
no_of_stops = "0"
flight_from = ["Pune","Mumbai"]
departure_time = ["2019-07-12 12:00:00","2019-07-15 05:30:33"]
arrival_time = ["2019-07-15 23:00:00","2019-07-17 07:00:00"]
flight_name = ["Spice Jet","Spice Jet"]
flight_no = ["Fligh4444","Fligh76565"]
flight_to = ["Bengalore","Kolkata"]
is_return_flight = ["0","0"]
finalpass = 1
employee_booking_id = ["1","2"]
ticket_number = ["Ti123","Ti456"]
train_name = "Indrayani Exp"


def add_flight(request):
    for x in range(1, 10):
        cursor3 = connection.cursor()
        cursor3.callproc('addFlightBooking',
                        [usage_type, journey_type, flight_class, pickup_location, drop_location, booking_datetime,boarding_datetime,
                         boarding_point, assessment_code, no_of_seats,group_id, subgroup_id, spoc_id, corporate_id, cotrav_billing_entity, reason_booking, user_id,
                         user_type, employees, booking_email, assessment_city_id, '@last_booking_id'])
        booking_id = dictfetchall(cursor3)
        cursor3.execute("SELECT @last_booking_id")
        last_booking_id = cursor3.fetchone()[0]
        print(last_booking_id)
        cursor3.close()

        cursor11 = connection.cursor()
        cursor11.callproc('acceptFlightBooking',[last_booking_id, user_id,user_type])
        data = dictfetchall(cursor11)
        cursor11.close()

        cursor = connection.cursor()
        cursor.callproc('assignFlightBooking',
                        [usage_type, flight_class, journey_type, no_of_stops, last_booking_id, bus_type, bus_type,
                         user_id, user_type, base_rate, management_fee, tax_on_management_fee,
                         tax_on_management_fee_percentage, sub_total, cotrav_billing_entity, igst, cgst, sgst,
                         management_fee_igst, management_fee_cgst, management_fee_sgst, management_fee_igst_rate,
                         management_fee_cgst_rate, management_fee_sgst_rate, tax_mng_amt, oper_ticket_price,
                         oper_commission, oper_commission_type, oper_cotrav_billing_entity, oper_igst, oper_cgst,
                         oper_sgst, client_ticket_path, vender_ticket_path, igst_amount, cgst_amount, sgst_amount,
                         operator_id, vendor_booking_id])
        result = dictfetchall(cursor)

        cursor.close()

        for x in range(len(flight_from)):
            cursor1 = connection.cursor()
            cursor1.callproc('addFlightBookingFlights',
                             [flight_name[x], flight_no[x], pnr_no[x], flight_from[x], flight_to[x], departure_time[x],
                              arrival_time[x], last_booking_id, user_id, user_type, is_return_flight[x]])
            result = dictfetchall(cursor1)
            cursor1.close()

        for xx in range(finalpass):
            print("1i m here")
            print(employee_booking_id[xx])
            print(booking_id)
            print("herer 2")
            cursor2 = connection.cursor()
            cursor2.callproc('updateFlightPassangerTickectNo', [ticket_number[xx], employee_booking_id[xx], last_booking_id])
            result = dictfetchall(cursor2)

            cursor2.close()

    data = {'success':1, 'message':'data insert Successfully..!'}
    return JsonResponse(data)


def add_hotel(request):
    for x in range(1, 10):
        cursor = connection.cursor()
        cursor.callproc('addHotelBooking',
                        [pickup_city, pickup_city, preferred_area, boarding_datetime, boarding_datetime,
                         bus_type, bus_type,
                         bus_type, bus_type, booking_datetime, assessment_code, assessment_city_id,
                         no_of_seats,
                         group_id, subgroup_id, spoc_id, corporate_id, cotrav_billing_entity, reason_booking, user_id,
                         user_type, employees, booking_email, '@last_booking_id'])
        booking_id = dictfetchall(cursor)
        cursor.execute("SELECT @last_booking_id")
        last_booking_id = cursor.fetchone()[0]
        print(last_booking_id)
        cursor.close()

        cursor1 = connection.cursor()
        cursor1.callproc('acceptHotelBooking',[last_booking_id, user_id,user_type])
        data = dictfetchall(cursor1)
        cursor1.close()

        cursor2 = connection.cursor()
        cursor2.callproc('assignHotelBooking',
                        [pickup_city, assign_room_type, assign_room_type, assign_room_type, assign_room_type, agent_booking_id,
                         comment, last_booking_id, user_id, user_type, base_rate, agent_booking_id, portal_used,
                         oper_commission, base_rate, management_fee,
                         tax_on_management_fee, tax_on_management_fee_percentage, sub_total, cotrav_billing_entity,
                         igst, cgst, sgst, management_fee_igst,
                         management_fee_cgst, management_fee_sgst, management_fee_igst_rate, management_fee_cgst_rate,
                         management_fee_sgst_rate, tax_mng_amt,
                         oper_ticket_price, oper_commission, oper_commission_type, oper_igst, oper_cgst, oper_sgst,
                         client_ticket_path, vender_ticket_path, igst_amount, cgst_amount, sgst_amount])
        company = dictfetchall(cursor2)

    data = {'success':1, 'message':'data insert Successfully..!'}
    return JsonResponse(data)


def add_train(request):
    for x in range(1, 10):
        cursor = connection.cursor()
        cursor.callproc('addTrainBooking',
                        [user_type, user_id, corporate_id, spoc_id, group_id, subgroup_id, pickup_location_train,
                         drop_location_train, bus_type, bus_type, bus_type, booking_datetime, pickup_datetime,
                         entity_id, preferred_bus, reason_booking, no_of_seats, assessment_code, assessment_city_id,
                         employees, booking_email, pickup_datetime, '@last_booking_id'])
        cursor.execute("SELECT @last_booking_id")
        last_booking_id = cursor.fetchone()[0]
        print(last_booking_id)
        cursor.close()

        cursor1 = connection.cursor()
        cursor1.callproc('acceptTrainBooking',[last_booking_id, user_id,user_type])
        data = dictfetchall(cursor1)
        cursor1.close()

        cursor2 = connection.cursor()
        cursor2.callproc('assignTrainBooking',
                        [ticket_no, pnr_no, assign_bus_type_id, seat_no, portal_used, operator_name, operator_contact,
                         boarding_point, boarding_datetime, last_booking_id, user_id, user_type, train_name, base_rate,
                         management_fee, tax_on_management_fee, tax_on_management_fee_percentage, sub_total,
                         cotrav_billing_entity, igst, cgst, sgst, management_fee_igst, management_fee_cgst,
                         management_fee_sgst, management_fee_igst_rate, management_fee_cgst_rate,
                         management_fee_sgst_rate, tax_mng_amt, client_ticket_path])
        company = dictfetchall(cursor2)

    data = {'success':1, 'message':'data insert Successfully..!'}
    return JsonResponse(data)


def add_bus(request):
    for x in range(1, 10):
        cursor = connection.cursor()
        cursor.callproc('addBusBooking',
                        [user_type, user_id, corporate_id, spoc_id, group_id, subgroup_id, pickup_location,
                         drop_location, bus_type, bus_type, bus_type, booking_datetime, pickup_datetime,
                         entity_id, preferred_bus, reason_booking, no_of_seats, assessment_code, assessment_city_id,
                         employees, booking_email, pickup_datetime, '@last_booking_id'])
        cursor.execute("SELECT @last_booking_id")
        last_booking_id = cursor.fetchone()[0]
        print(last_booking_id)
        cursor.close()

        cursor1 = connection.cursor()
        cursor1.callproc('acceptBusBooking',[last_booking_id, user_id,user_type])
        data = dictfetchall(cursor1)
        cursor1.close()

        cursor2 = connection.cursor()
        cursor2.callproc('assignBusBooking',
                        [ticket_no, pnr_no, assign_bus_type_id, seat_no, portal_used, operator_name, operator_contact,
                         boarding_point, boarding_datetime, last_booking_id, user_id, user_type, base_rate,
                         management_fee, tax_on_management_fee, tax_on_management_fee_percentage, sub_total,
                         cotrav_billing_entity, igst, cgst, sgst, management_fee_igst, management_fee_cgst,
                         management_fee_sgst, management_fee_igst_rate, management_fee_cgst_rate,
                         management_fee_sgst_rate, tax_mng_amt, oper_ticket_price, oper_commission,
                         oper_commission_type, oper_cotrav_billing_entity, oper_igst, oper_cgst, oper_sgst,
                         client_ticket_path, vender_ticket_path, igst_amount, cgst_amount, sgst_amount])
        company = dictfetchall(cursor2)

    data = {'success':1, 'message':'data insert Successfully..!'}
    return JsonResponse(data)

def get_test_data(request):
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

def add_taxi(request):
    for x in range(1, 10):
        cursor = connection.cursor()
        cursor.callproc('addTaxiBooking',[user_type, user_id, entity_id, corporate_id, spoc_id, group_id, subgroup_id, tour_type,
                         pickup_city, pickup_location, drop_location, pickup_datetime,taxi_type, package_id, no_of_days, reason_booking, no_of_seats, assessment_code,
                         assessment_city_id, employees, booking_datetime, booking_email, '@last_booking_id'])
        cursor.execute("SELECT @last_booking_id")
        last_booking_id = cursor.fetchone()[0]
        print(last_booking_id)
        cursor.close()

        cursor1 = connection.cursor()
        cursor1.callproc('acceptTaxiBooking',[last_booking_id, user_id,user_type])
        data = dictfetchall(cursor1)
        cursor1.close()

        cursor2 = connection.cursor()
        cursor2.callproc('assignTaxiBooking', [vendor_booking_id, operator_id, driver_id, taxi_id, last_booking_id, user_id, user_type])
        company = dictfetchall(cursor2)

        cursor3 = connection.cursor()
        cursor3.callproc('addTaxiInvoice',
                        [tax_on_management_fee, tax_on_management_fee_percentage, management_fee_igst, management_fee_cgst,
                         management_fee_sgst, management_fee_igst_rate, management_fee_cgst_rate, management_fee_sgst_rate,
                         igst_amount, cgst_amount, sgst_amount,
                         hours_done, allowed_hours, extra_hours, charge_hour, days, start_km, end_km, kms_done, allowed_kms,
                         extra_kms, extra_km_rate, base_rate, extra_hr_charges,
                         extra_km_charges, driver_allowance, total_excluding_tax, other_charges, total, sub_total,
                         radio_rate, bb_entity, cotrav_billing_entity, last_booking_id, user_id, user_type])
        company = dictfetchall(cursor3)
    data = {'success':1, 'message':'data insert Successfully..!'}
    return JsonResponse(data)
