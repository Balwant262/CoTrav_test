from pyfcm import FCMNotification
import requests
from CoTrav import settings
import os
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string


from Common.models import Corporate_Agent
#COTRAV_FROM_EMAIL = "bookings@cotrav.co"
COTRAV_FROM_EMAIL = settings.EMAIL_HOST_USER
#COTRAV_EMAILS = list(Corporate_Agent.objects.filter(is_super_admin=1).exclude(email='').values_list('email', flat=True))
#COTRAV_NUMBERS = list(Corporate_Agent.objects.filter(is_super_admin=1).exclude(contact_no='').values_list('contact_no', flat=True))
COTRAV_EMAILS = 'balwant@taxivaxi.in'
COTRAV_NUMBERS = "9579477262"
COTRAV_SIGNUP_EMAILS = "vinod@taxivaxi.com"
COTRAV_FROM_EMAIL_SIGNUP = settings.DEFAULT_FROM_USER
COTRAV_SUPPORT_PWD = settings.DEFAULT_FROM_PWD

API_ACCESS_KEY_EMPLOYEE = 'AAAAE7JHFiU:APA91bH8hJWfLlFEjL9TiSKIT0so-HL1PXqDXgKWtU_19W-3ViuJHZC8Iswkq3eXl-Tjd8jKBm7X9UxCFMKpJaBQt5Ar-9qJeAB07R753hpmamQXW6lP917Fa0S6w02qzi6tNai3Kmsh'
API_ACCESS_KEY_SPOC = ''

COTRAV_CC_EMAILS = "balwant@taxivaxi.in"
COTRAV_CC_EMAILS = COTRAV_CC_EMAILS.split(",")
COTRAV_BCC_EMAILS = "balwant@taxivaxi.in"
COTRAV_BCC_EMAILS = COTRAV_BCC_EMAILS.split(",")

sender_id = 'COTRAV'
exotel_sid = "novuslogic1"
exotel_key = "6ae4c99860c31346203da94dc98a4de7fd002addc5848182"
exotel_token = "a2c78520d23942ad9ad457b81de2ee3f3be743a8188f8c39"


class SignIn_OTP:
    def send_email(self, email_to, email_subject, email_body):
        #email_subject = "Cotrav - Verify Your Email"
        #email_body = "Dear User,<br><br>"+generate_otp+" is your verification code to access your profile and bookings on Cotrav app, you need to verify your email first. <br><br>Rgrds,<br>CoTrav."
        connection = get_connection(username=COTRAV_FROM_EMAIL_SIGNUP, password=COTRAV_SUPPORT_PWD)  # uses SMTP server specified in settings.py
        #connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL_SIGNUP, [email_to], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg.content_subtype = "html"
        res = msg.send(fail_silently=True)
        #connection.close()  # Cleanup
        res = 1
        return (res)


class AddBooking_Email:
    def send_taxi_email(self, booking, approvers, booking_type):
        global booking_tempalte
        global email_body
        global email_subject
        global email_content
        global email_title

        if booking_type == "Taxi":
            booking_tempalte = "Email_Templates/taxi_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Taxi Booking Received"
            email_content = "New booking request for Taxi received. Details as below,"
            email_title = "New Taxi Booking Received"

        elif booking_type == "Bus":
            print("in bus booking")
            booking_tempalte = "Email_Templates/bus_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Bus Booking Received"
            email_content = "New booking request for Bus received. Details as below,"
            email_title = "New Bus Booking Received"

        elif booking_type == "Train":
            booking_tempalte = "Email_Templates/train_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Train Booking Received"
            email_content = "New booking request for Train received. Details as below,"
            email_title = "New Train Booking Received"

        elif booking_type == "Flight":
            booking_tempalte = "Email_Templates/flight_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Flight Booking Received"
            email_content = "New booking request for Flight received. Details as below,"
            email_title = "New Flight Booking Received"

        elif booking_type == "Visa":
            booking_tempalte = "Email_Templates/visa_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Visa Request Received"
            email_content = "New booking request for Visa Request received. Details as below,"
            email_title = "New Visa Request Received"

        elif booking_type == "Frro":
            booking_tempalte = "Email_Templates/Frro_Email_Templates/welcomeEmailFRRO.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "| FRRO Request Approved | CoTrav Introduction"
            email_content = "New booking request for FRRO Request received. Details as below,"
            email_title = "New FRRO Request Received"

        elif booking_type == "Guesthouse":
            booking_tempalte = "Email_Templates/guesthouse_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "| Guesthouse Request Received"
            email_content = "New booking request for Guesthouse Request received. Details as below,"
            email_title = "New Guesthouse Request Received"

        else:
            print("in hotel booking")
            booking_tempalte = "Email_Templates/hotel_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Hotel Booking Received"
            email_content = "New booking request for Hotel received. Details as below,"
            email_title = "New Hotel Booking Received"

        employee_name = ''
        employee_emails = ''
        name_approver_1 = ''
        name_approver_2 = ''
        email_approver_1 = ''
        email_approver_2 = ''
        is_send_email_approver_1 = ''
        is_send_sms_approver_1 = ''
        is_send_email_approver_2 = ''
        is_send_sms_approver_2 = ''

        spoc_email = booking[0]['user_email']

        if booking_type == "Visa" or booking_type == "Frro":
            for passangerss in booking[0]['EmployeesDocs']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
        else:
            for passangerss in booking[0]['Passangers']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))

        if booking[0]['status_client'] == 1 or booking[0]['status_client'] == '1':
            for approver in approvers:
                if approver['email_approver_1']:
                    name_approver_1 = "".join(map(str, approver['approver_1']))
                    email_approver_1 = "".join(map(str, approver['email_approver_1']))
                    is_send_email_approver_1 = approver['is_send_email_approver_1']

                if approver['email_approver_2']:
                    name_approver_2 = "".join(map(str, approver['approver_2']))
                    email_approver_2 = "".join(map(str, approver['email_approver_2']))
                    is_send_email_approver_2 = approver['is_send_email_approver_2']

        if email_approver_1:
            if booking_type == "Taxi":
                email_content = "Booking request for Taxi is pending for approval. Details as below,"
            elif booking_type == "Bus":
                email_content = "Booking request for Bus is pending for approval. Details as below,"
            elif booking_type == "Train":
                email_content = "Booking request for Train is pending for approval. Details as below,"
            elif booking_type == "Hotel":
                email_content = "Booking request for Hotel is pending for approval. Details as below,"
            elif booking_type == "Flight":
                email_content = "Booking request for Flight is pending for approval. Details as below,"
            elif booking_type == "Visa":
                email_content = "Visa Request is pending for approval. Details as below,"
            elif booking_type == "Frro":
                email_content = "New FRRO Request |"+ booking[0]['reference_no']
                email_subject = "New FRRO Request |"+ booking[0]['reference_no']
            elif booking_type == "Guesthouse":
                email_content = "Booking request for Guesthouse is pending for approval. Details as below,"


            if is_send_email_approver_1:
                if booking_type == "Frro":
                    booking_tempalte = "Email_Templates/Frro_Email_Templates/welcomeEmailFRRO.html"
                    email_body = ""
                    email_subject = "" + booking[0]['reference_no'] + "| FRRO Request Approved | CoTrav Introduction"
                self.send_mail_to_approvel(booking, email_approver_1, name_approver_1, email_subject, email_body,booking_tempalte, email_content, email_title)
                self.send_mail_to_employee(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte, email_content, email_title)
                if booking[0]['spoc_is_send_email'] == 1:
                    self.send_mail_to_spoc(booking, spoc_email, booking[0]['user_name'], email_subject, email_body,booking_tempalte, email_content, email_title)
                self.send_mail_to_cotrav_agent(booking, COTRAV_EMAILS, "Team", email_subject, email_body,booking_tempalte, email_content, email_title)
        else:
            if booking_type == "Frro":
                booking_tempalte = "Email_Templates/Frro_Email_Templates/frroBookingCreatedToSPOC.html"
            self.send_mail_to_employee(booking, employee_emails, employee_name, email_subject, email_body,booking_tempalte, email_content, email_title)
            if booking[0]['spoc_is_send_email'] == 1:
                if booking_type == "Frro":
                    booking_tempalte = "Email_Templates/Frro_Email_Templates/frroBookingCreatedToSPOC.html"
                self.send_mail_to_spoc(booking, spoc_email, booking[0]['user_name'], email_subject, email_body, booking_tempalte, email_content, email_title)
            self.send_mail_to_cotrav_agent(booking, COTRAV_EMAILS, "Team", email_subject, email_body, booking_tempalte,email_content, email_title)
        if email_approver_2:
            if booking_type == "Taxi":
                email_content = "Booking request for Taxi is pending for approval. Details as below,"
            elif booking_type == "Bus":
                email_content = "Booking request for Bus is pending for approval. Details as below,"
            elif booking_type == "Train":
                email_content = "Booking request for Train is pending for approval. Details as below,"
            elif booking_type == "Hotel":
                email_content = "Booking request for Hotel is pending for approval. Details as below,"
            elif booking_type == "Flight":
                email_content = "Booking request for Flight is pending for approval. Details as below,"
            elif booking_type == "Visa":
                email_content = "Visa Request is pending for approval. Details as below,"
            elif booking_type == "Guesthouse":
                email_content = "Booking request for Guesthouse is pending for approval. Details as below,"
            if is_send_email_approver_2:
                if booking_type == "Frro":
                    booking_tempalte = "Email_Templates/Frro_Email_Templates/welcomeEmailFRRO.html"
                    email_body = ""
                    email_subject = "" + booking[0]['reference_no'] + "| FRRO Request Approved | CoTrav Introduction"
                self.send_mail_to_approvel2(booking, email_approver_2, name_approver_2, email_subject, email_body,booking_tempalte, email_content, email_title)

        return 1

    def send_mail_to_cotrav_agent(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_to_employee(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_to_spoc(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_to_approvel(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_to_approvel2(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1


    def send_taxi_msg(self, booking, approvers,booking_type):
        employee_numbers = ''
        employee_name = ''
        name_approver_1 = ''
        name_approver_2 = ''
        contact_approver_1 = ''
        contact_approver_2 = ''
        is_send_sms_approver_1 = ''
        is_send_sms_approver_2 = ''

        if booking_type == "Visa" or booking_type == "Frro":
            for passangerss in booking[0]['EmployeesDocs']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
        else:
            for passangerss in booking[0]['Passangers']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))

        if approvers:
            for approver in approvers:
                if approver['email_approver_1']:
                    name_approver_1 = "".join(map(str, approver['approver_1']))
                    is_send_sms_approver_1 = approver['is_send_sms_approver_1']
                if approver['email_approver_2']:
                    is_send_sms_approver_2 = approver['is_send_sms_approver_2']
                    name_approver_2 = "".join(map(str, approver['approver_2']))
                if approver['contact_approver_1']:
                    contact_approver_1 = "".join(map(str, approver['contact_approver_1']))
                if approver['contact_approver_2']:
                    contact_approver_2 = "".join(map(str, approver['contact_approver_2']))
            if contact_approver_1 and is_send_sms_approver_1:
                self.send_sms_to_taxi_for_approve(booking, contact_approver_1, name_approver_1, booking_type)
            if contact_approver_2 and is_send_sms_approver_2:
                self.send_sms_to_taxi_for_approve(booking, contact_approver_2, name_approver_2, booking_type)
            if employee_numbers:
                self.send_sms_to_taxi_for_approve(booking, employee_numbers, employee_name,booking_type)
            if booking[0]['user_contact']:
                self.send_sms_to_taxi_for_approve(booking, employee_numbers, employee_name,booking_type)
            self.send_sms_to_taxi_for_approve(booking, COTRAV_NUMBERS, "Team", booking_type)
        else:
            # if No Approvels
            if employee_numbers:
                self.send_sms_to_taxi(booking, employee_numbers, employee_name,booking_type)
            if booking[0]['user_contact']:
                self.send_sms_to_taxi(booking, employee_numbers, employee_name,booking_type)
            self.send_sms_to_taxi(booking, COTRAV_NUMBERS, "Team" ,booking_type)

        return 1

    def send_sms_to_taxi_for_approve(self,booking, phone_number, name, booking_type):

        global sms_body

        if booking_type == "Taxi":
            tour_type = str(booking[0]['tour_type'])
            if tour_type == '1':
                tour_type = "Radio"
            if tour_type == '2':
                tour_type = "Local"
            if tour_type == '3':
                tour_type = "Outstation"
            sms_body = "Dear " + name + ",\n\nYour Taxi Booking is created and sent for approval. " + booking[0]['reference_no'] + ".\n\nPickup from " + \
                booking[0]['pickup_location'] + " on " + booking[0]['pickup_datetime'] + ".\nDrop: " + booking[0]['drop_location'] + "\nTrip Type: " + \
                str(tour_type) + ".\nTaxi Type: " + str(booking[0]['taxi_type_request']) + ".\n\nPlease call at " + COTRAV_NUMBERS + \
                            " for any query.\n\nRgrds,\nCotrav."
        elif booking_type == "Bus":
            sms_body = "Dear "+name+",\n\nYour Bus Booking is created and sent for approval.\n\nID: "+booking[0]['reference_no']+"\n\nFrom: "+\
                       booking[0]['pickup_location']+"\nTo: "+booking[0]['drop_location']+"\nJourney Date: "+booking[0]['pickup_from_datetime']+"\nBus Type: "+\
                       booking[0]['bus_type_priority_1']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav."

        elif booking_type == "Train":
            sms_body = "Dear "+name+",\n\nYour Train Booking is created and sent for approval.\n\nID: "+\
                       booking[0]['reference_no']+"\nFrom: "+booking[0]['pickup_location']+"\nTo: "+booking[0]['drop_location']+"\nJourney Date: "+\
                       booking[0]['pickup_from_datetime']+"\nCoach Type: "+booking[0]['train_type_priority_1']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav"
        elif booking_type == "Flight":
            sms_body = "Dear "+name+",\n\nYour Flight Booking is created and sent for approval.\n\nID: "+booking[0]['reference_no']+"\nFrom: "+booking[0]['from_location']+\
                       "\nTo: "+booking[0]['to_location']+"\nJourney Date: "+booking[0]['departure_datetime']+"\nTrip Type: "+\
                       booking[0]['usage_type']+"\nSeat Type: "+booking[0]['journey_type']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav"
        elif booking_type == "Visa":
            sms_body = "Dear "+name+",\n\nYour Visa Request is created and sent for approval.\n\nID: "+booking[0]['reference_no']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav"

        elif booking_type == "Frro":
            sms_body = "Dear " + name + ",\n\nYour FRRO Request is created and sent for approval.\n\nID: " + booking[0][
                'reference_no'] + "\n\nPlease call at " + COTRAV_NUMBERS + " for any query.\n\nRgrds,\nCotrav"

        elif booking_type == "Guesthouse":
            sms_body =  "Dear "+name+",\n\nYour Guesthouse Booking is created and sent for approval.\n\nID: "+booking[0]['reference_no']+"\nArea: "+\
                        str(booking[0]['from_city_name'])+"\nCheck-In Date: "+booking[0]['checkin_datetime']+"\nRoom Type: "+str(booking[0]['title'])+\
                        "\nRoom Occupancy: "+str(booking[0]['room_type_id'])+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav."
        else:
            sms_body =  "Dear "+name+",\n\nYour Hotel Booking is created and sent for approval.\n\nID: "+booking[0]['reference_no']+"\nArea: "+\
                        str(booking[0]['from_area_id_name'])+"\nCheck-In Date: "+booking[0]['checkin_datetime']+"\nRoom Type: "+str(booking[0]['bucket_priority_1'])+\
                        "\nRoom Occupancy: "+str(booking[0]['description'])+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav."

        sms = SMS()
        sms.send_sms(phone_number, sms_body)

        return 1

    def send_sms_to_taxi(self,booking, phone_number, name, booking_type):
        global sms_body

        if booking_type == "Taxi":
            tour_type = str(booking[0]['tour_type'])
            if tour_type == '1':
                tour_type = "Radio"
            if tour_type == '2':
                tour_type = "Local"
            if tour_type == '3':
                tour_type = "Outstation"
            sms_body = "Dear " + name + ",\n\nYour Bus Booking is created.\n\nID: " + booking[0]['reference_no'] + ".\n\nPickup from " + \
                booking[0]['pickup_location'] + " on " + booking[0]['pickup_datetime'] + ".\nDrop: " + booking[0]['drop_location'] + "\nTrip Type: " + \
                str(tour_type) + ".\nTaxi Type: " + str(booking[0]['taxi_type_request']) + ".\n\nPlease call at " + COTRAV_NUMBERS + \
                            " for any query.\n\nRgrds,\nCotrav."

        elif booking_type == "Bus":
            sms_body = "Dear "+name+",\n\nYour Bus Booking is created.\n\nID: "+booking[0]['reference_no']+"\n\nFrom: "+\
                       booking[0]['pickup_location']+"\nTo: "+booking[0]['drop_location']+"\nJourney Date: "+booking[0]['pickup_from_datetime']+"\nBus Type: "+\
                       booking[0]['bus_type_priority_1']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav."

        elif booking_type == "Train":
            sms_body = "Dear "+name+",\n\nYour Train Booking is created.\n\nID: "+\
                       booking[0]['reference_no']+"\nFrom: "+booking[0]['pickup_location']+"\nTo: "+booking[0]['drop_location']+"\nJourney Date: "+\
                       booking[0]['pickup_from_datetime']+"\nCoach Type: "+booking[0]['train_type_priority_1']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav"

        elif booking_type == "Flight":
            sms_body = "Dear "+name+",\n\nYour Flight Booking is created.\n\nID: "+booking[0]['reference_no']+"\nFrom: "+booking[0]['from_location']+\
                       "\nTo: "+booking[0]['to_location']+"\nJourney Date: "+booking[0]['departure_datetime']+"\nTrip Type: "+\
                       booking[0]['usage_type']+"\nSeat Type: "+booking[0]['journey_type']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav"

        elif booking_type == "Visa":
            sms_body = "Dear "+name+",\n\nYour Visa Requsest is created.\n\nID: "+booking[0]['reference_no']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav"

        elif booking_type == "Frro":
            sms_body = "Dear "+name+",\n\nYour FRRO Requsest is created.\n\nID: "+booking[0]['reference_no']+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav"

        elif booking_type == "Guesthouse":
            sms_body =  "Dear "+name+",\n\nYour Guesthouse Booking is created \n\nID: "+booking[0]['reference_no']+"\nCity: "+\
                        str(booking[0]['from_city_name'])+"\nCheck-In Date: "+booking[0]['checkin_datetime']+"\nRoom Type: "+str(booking[0]['title'])+\
                        "\nRoom Occupancy: "+str(booking[0]['description'])+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav."
        else:
            sms_body =  "Dear "+name+",\n\nYour Hotel Booking is created \n\nID: "+booking[0]['reference_no']+"\nArea: "+\
                        str(booking[0]['from_area_id_name'])+"\nCheck-In Date: "+booking[0]['checkin_datetime']+"\nRoom Type: "+str(booking[0]['bucket_priority_1'])+\
                        "\nRoom Occupancy: "+str(booking[0]['room_type_id'])+"\n\nPlease call at "+COTRAV_NUMBERS+" for any query.\n\nRgrds,\nCotrav."

        sms = SMS()
        sms.send_sms(phone_number, sms_body)

        return 1

    def new_user_send_email(self, username, password, user_type):
        email_subject = "CoTrav New User Login Credentials"
        email_body = "Dear " + username + ",<br> Url: cotrav.co/login <br> Email:" + username + "<br> Password:" + password + "<br> UserType:" + user_type + \
                     "<br> Thank you for Signup. <br><br>Please call at  for any query. <br><br>Rgrds,<br>CoTrav."
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [username], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.content_subtype = "html"
        res = msg.send(fail_silently=True)
        return 1

    def send_sms(self):
        sms_body = "New Taxi Booking - " + "TV132131" + ".<br><br>Pickup from: " + "Pune" + "<br>Pickup Time: " + "10-10-2019 12:12 AM" + ".<br>Trip Type: " + "Local" + ".<br>Taxi Type: " + "N/A" + ".<br><br>Regards,<br>Cotrav"
        sms = SMS()
        sms.send_sms(COTRAV_NUMBERS, sms_body)

        return 1


class newUserAdd_Email:
    def new_user_send_email(self, name, username_email, password, user_type):
        email_subject = "CoTrav New User Login Credentials"
        tempalte = "Email_Templates/New_User_Add/add_new_user_email_template.html"
        email_body = ""
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(tempalte, {'password':password, 'user_name': name,'user_type':user_type, 'username_email':username_email })
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [username_email], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1


class Assign_Booking_Email:
    def is_client_email(self,booking, booking_type, gen_voucher_path):
        global booking_tempalte
        global email_body

        if booking_type == "Taxi":
            booking_tempalte = "Email_Templates/Assign_Booking/taxi_email_template.html"
        elif booking_type == "Bus":
            print("in bus booking")
            booking_tempalte = "Email_Templates/Assign_Booking/bus_email_template.html"

        elif booking_type == "Train":
            booking_tempalte = "Email_Templates/Assign_Booking/train_email_template.html"

        elif booking_type == "Flight":
            booking_tempalte = "Email_Templates/Assign_Booking/flight_email_template.html"
        else:
            print("in hotel booking")
            booking_tempalte = "Email_Templates/Assign_Booking/hotel_email_template.html"

        employee_name = ''
        employee_emails = ''
        email_body = ''

        spoc_email = booking[0]['user_email']

        if not booking_type == "Visa":
            for passangerss in booking[0]['Passangers']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
        else:
            for passangerss in booking[0]['EmployeesDocs']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))

        email_subject = "" + booking[0]['reference_no'] + "- Ride Details Confirmed"

        if booking_type == "Hotel":
            email_subject = "" + booking[0]['reference_no'] + "- Hotel Booking Confirmed"

        # self.send_mail_to_cotrav_agent(booking, COTRAV_EMAILS, "Team", email_subject, email_body, booking_tempalte, gen_voucher_path)
        print("email_send")
        self.send_mail_to_employee(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte, gen_voucher_path)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail_to_spoc(booking, spoc_email, booking[0]['user_name'], email_subject, email_body,booking_tempalte, gen_voucher_path)

    def send_mail_to_cotrav_agent(self, booking, emails, name, email_subject, email_body, booking_tempalte, gen_voucher_path):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        if gen_voucher_path:
            msg.attach_file(gen_voucher_path)
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_to_employee(self, booking, emails, name, email_subject, email_body, booking_tempalte, gen_voucher_path):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        if gen_voucher_path:
            msg.attach_file(gen_voucher_path)
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_to_spoc(self, booking, emails, name, email_subject, email_body, booking_tempalte, gen_voucher_path):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        if gen_voucher_path:
            msg.attach_file(gen_voucher_path)
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1


    def send_client_sms(self,booking, booking_type):
        employee_numbers = ''
        employee_name = ''
        if not booking_type == "Visa":
            for passangerss in booking[0]['Passangers']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
        else:
            for passangerss in booking[0]['EmployeesDocs']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))

        if employee_numbers:
            self.send_sms_to_employee(booking, employee_numbers, employee_name, booking_type)


    def send_sms_to_employee(self,booking, phone_number, name, booking_type):

        global sms_body

        if booking_type == "Taxi":
            sms_body = "Dear "+name+"\n\nYour Booking ID " +booking[0]['reference_no']+" is confirmed.\n\nPickup From: "+booking[0]['pickup_location']+\
                       "\nPickup on: "+booking[0]['drop_location']+"\nCar: "+booking[0]["model_name"]+" ("+booking[0]["taxi_reg_no"]+")\nDriver: "+\
                       booking[0]["driver_name"]+ " (" +booking[0]["driver_contact"]+")\nPassenger: " +name+ "\n\nFor any assistance, please call us at " +\
                       COTRAV_NUMBERS+ "\n\n$sms_sender_name"
        elif booking_type == "Bus":
            sms_body = "Dear "+name+"\n\nYour Booking ID "+booking[0]['reference_no']+" is assigned.\n\nOperator: "+booking[0]['operator_name']+\
                       "\nPNR No: "+booking[0]['pnr_no']+"\nTicket No: "+booking[0]['ticket_no']+"\nSeat No:"+booking[0]['seat_no']+"\nBus Type: "+\
                       booking[0]['assign_bus_type_id']+"\nBoarding Time: "+booking[0]['boarding_datetime']+"\nBoarding Point: "+booking[0]['boarding_point']+\
                       "\n\nIn case of any query, please call at "+COTRAV_NUMBERS+".\n\nRgrds,\nCotrav"

        elif booking_type == "Train":
            sms_body = "Dear "+name+",\n\nYour Booking ID "+booking[0]['reference_no']+" assigned by Cotrav.\n\nTrain: "+booking[0]['train_name']+\
                       "\nTrain No.:"+booking[0]['train_name']+"\nPNR No.: "+booking[0]['pnr_no']+"\nCoach No.:"+booking[0]['seat_no']+"\nSeat No.: "+\
                       booking[0]['seat_no']+"\nCoach Type: "+booking[0]['assign_bus_type_id']+"\nBoarding Time: "+booking[0]['boarding_datetime']+\
                       "\nBoarding Station: "+booking[0]['boarding_point']+"\n\nIn case of any query, please call at "+COTRAV_NUMBERS+\
                       ".\n\nRegards,\nCotrav"

        elif booking_type == "Flight":
            sms_body =  "Dear "+name+",\n\nYour Booking ID "+booking[0]['reference_no']+" assigned by Cotrav.\n\nFlight: "+booking[0]['Flights'][0]['flight_name']+\
                        " ("+booking[0]['Flights'][0]['flight_no']+")\nPNR No.: "+booking[0]['Flights'][0]['pnr_no']+"\nFlight Type: "+booking[0]['journey_type']+"\nSeat Type: "+\
                        booking[0]['flight_class']+"\nTrip Type: "+booking[0]['usage_type']+"\nBoarding Time: "+str(booking[0]['Flights'][0]['departure_datetime'])+\
                        "\nBoarding at:"+booking[0]['from_location']+"\n\nIn case of any query, please call at "+COTRAV_NUMBERS+".\n\nRegards,\nCotrav"

        else:
            sms_body = "Dear "+name+",\n\nYour Booking ID "+booking[0]['reference_no']+" assigned by Cotrav.\n\nHotel: "+booking[0]['operator_name']+\
                       "\nHotel Address: "+booking[0]['operator_contact']+"\nHotel Contact: "+booking[0]['operator_contact']+"\nVoucher No.: "+\
                       booking[0]['reference_no']+"\nRoom Type: "+booking[0]['hotel_type_name']+"\nCheck-In Date: "+booking[0]['checkin_datetime']+\
                       "\n\nIn case of any query, please call at "+COTRAV_NUMBERS+"\n\nRegards,\nCotrav"

        sms = SMS()
        sms.send_sms(phone_number, sms_body)

        return 1


class SignupEmail():

    def __init__(self, company, company_location, cp_name, cp_no, cp_email, message):
        self.company = company
        self.company_location = company_location
        self.cp_name = cp_name
        self.cp_no = cp_no
        self.cp_email = cp_email
        self.message = message
        self.send_to = cp_email

    def send_email(self):
        email_subject=''
        tempalte= ''
        email_body=''
        if self.company_location == 'contactus':
            email_subject = "Welcome to CoTrav"
            tempalte = "contact_welcome.html"
            email_body = 'Thank You For Showing Interest. We will Contact You Soon'
        else:
            email_subject = "Welcome to CoTrav"
            tempalte = "signup_welcome.html"
            email_body = 'Thanks for signing up. A CoTrav official would be contacting you in 24 hours to discuss the business solutions for your team.'
        connection = get_connection(username=COTRAV_FROM_EMAIL_SIGNUP, password=COTRAV_SUPPORT_PWD)  # uses SMTP server specified in settings.py
        #connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(tempalte, {'company': self.company, 'location': self.company_location,
        'user_name': self.cp_name, 'cp_no': self.cp_no,'cp_email': self.cp_email, 'message': self.message, 'cp_name': self.cp_name,'email_body':email_body })
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL_SIGNUP, [self.send_to], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg.attach_alternative(html_content, "text/html")
        res11 = msg.send(fail_silently=True)
        print("in second email")

        email_body2 = "Someone has contacted us through signup form. Please find the details below."
        html_content2 = render_to_string(tempalte, {'company': self.company, 'location': self.company_location, 'user_name': "CoTrav Team", 'cp_no': self.cp_no,
        'cp_email': self.cp_email, 'message': self.message, 'cp_name': self.cp_name, 'email_body':email_body2})
        msg1 = EmailMultiAlternatives("New Lead Created | "+self.company,  email_body2 , COTRAV_FROM_EMAIL_SIGNUP, [COTRAV_SIGNUP_EMAILS], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg1.attach_alternative(html_content2, "text/html")
        res12 = msg1.send(fail_silently=True)
        print("in second sent email")
        #connection.close()  # Cleanup
        # res = 1
        sms_body = "Dear "+self.cp_name +"\n\nThank you for signing up with CoTrav.\nA CoTrav official would be contacting you in 24 hours to discuss the business solution for your team.\n\nRegards,\nCotrav"
        sms = SMS()
        sms.send_sms(self.cp_no, sms_body)

        return (1)


    def reminder_email(self):
        email_subject = "Lead Generation Reminder"
        tempalte = "signup_welcome.html"
        email_body = 'Lead With Following Company Details Contacted US Again..!'
        connection = get_connection(username=COTRAV_FROM_EMAIL_SIGNUP, password=COTRAV_SUPPORT_PWD)  # uses SMTP server specified in settings.py
        html_content = render_to_string(tempalte, {'company': self.company, 'location': self.company_location,
                                                   'cp_name': self.cp_name, 'cp_no': self.cp_no,
                                                   'cp_email': self.cp_email, 'message': self.message})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL_SIGNUP, [self.cp_email], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        return (res)


class Lead_Email_To_Company_assign_agent():
    def __init__(self, message,ag_email,ag_name,ag_no,Contact_Name,Contact_Email,Contact_Number):
        self.cp_email = Contact_Email
        self.message = message
        self.ag_email = ag_email
        self.ag_name = ag_name
        self.ag_no = ag_no
        self.company_c_name = Contact_Name
        self.Contact_Number = Contact_Number

    def send_email(self):
        tempalte = "assign_agent_email_template.html"
        email_subject = "Cotrav | Relationship Manager Assigned"
        email_title = "Dear " + self.company_c_name + ","
        email_body = self.message
        connection = get_connection(username=COTRAV_FROM_EMAIL_SIGNUP, password=COTRAV_SUPPORT_PWD)  # uses SMTP server specified in settings.py
        html_content = render_to_string(tempalte, {'cp_email': self.cp_email, 'message': '','body_message':email_body,
            'email_title':email_title, 'ag_no':  self.ag_no, 'company_c_name':  self.company_c_name , 'ag_email': self.ag_email, 'ag_name':self.ag_name })
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL_SIGNUP, [self.cp_email], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        sms_body = "Dear "+self.company_c_name +"\n\nA Relationship Manager has been assigned to you to solve all your queries.\n\nContact Details -"+self.ag_email+"/"+self.ag_no+" will connect with you for further follow-ups.\n\nRegards,\nCotrav"
        sms = SMS()
        sms.send_sms(self.Contact_Number, sms_body)

        return (1)


class Lead_Status_Change_Email():
    def __init__(self, message,status,ag_email,ag_name,Company_Name,Contact_Name,Contact_Email,Contact_Number,Company_Location):
        self.cp_email = Contact_Email
        self.message = message
        self.send_to = ag_email
        self.ag_name = ag_name
        self.status = status
        self.Company_Name = Company_Name
        self.Contact_Name = Contact_Name
        self.Contact_Number = Contact_Number
        self.Company_Location = Company_Location

    def send_email(self):
        tempalte = "signup_email_template.html"
        email_subject = "Lead Update | "+self.Company_Name
        email_title = "Dear " + self.ag_name + ","
        email_body = self.message
        connection = get_connection(username=COTRAV_FROM_EMAIL_SIGNUP, password=COTRAV_SUPPORT_PWD) # uses SMTP server specified in settings.py
        #connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(tempalte, {'company': self.Company_Name, 'location': self.Company_Location,
            'cp_name': self.Contact_Name, 'cp_no': self.Contact_Number, 'cp_email': self.cp_email, 'message': '','body_message':email_body,
            'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL_SIGNUP, [self.send_to], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg.attach_alternative(html_content, "text/html")

        res = msg.send(fail_silently=True)
        #connection.close()  # Cleanup

        sms_body = "Dear "+self.Contact_Name+"\n\nWelcome to Cotrav!\n\nLooking forward to serve you.\n\nIn case of any query, please call at "+COTRAV_NUMBERS+".\n\nRegards,\nCotrav"
        sms = SMS()
        sms.send_sms(self.Contact_Number, sms_body)

        return (1)

    def send_email_lost(self):
        tempalte = "signup_email_template.html"
        email_subject = "Lead Assigned | "+self.Company_Name
        email_title = "Dear " + self.ag_name + ","
        email_body = self.message
        connection = get_connection(username=COTRAV_FROM_EMAIL_SIGNUP, password=COTRAV_SUPPORT_PWD)  # uses SMTP server specified in settings.py
        #connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(tempalte, {'company': self.Company_Name, 'location': self.Company_Location,
            'cp_name': self.Contact_Name, 'cp_no': self.Contact_Number, 'cp_email': self.cp_email, 'message': '','body_message':email_body,
            'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL_SIGNUP, [self.send_to], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg.attach_alternative(html_content, "text/html")

        res = msg.send(fail_silently=True)
        #connection.close()  # Cleanup
        email_subject1 = "Welcome to CoTrav "
        email_title1 = "Dear " + self.ag_name + ","
        email_body1 = self.message
        html_content1 = render_to_string(tempalte, {'company': self.Company_Name, 'location': self.Company_Location, 'cp_name': self.Contact_Name, 'cp_no': self.Contact_Number,
                                                   'cp_email': self.cp_email, 'message': '', 'body_message': email_body, 'email_title': email_title1})
        msg = EmailMultiAlternatives(email_subject1, email_body1, COTRAV_FROM_EMAIL_SIGNUP, [self.cp_email], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS, connection=connection)
        msg.attach_alternative(html_content1, "text/html")
        res = msg.send(fail_silently=True)

        sms_body = "Dear "+self.Contact_Name+"\n\nSorry to lose you! Let us know if we could be of any help in future."
        sms = SMS()
        sms.send_sms(self.Contact_Number, sms_body)

        return (1)


class FCM:

    def send_notification_add(self, booking, approvers, booking_type):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)

        registration_id = list()
        registration_id.append(booking[0]['spoc_fcm_reg_id'])

        message_body = ""
        if booking_type == "Visa" or booking_type == "Frro":
            for passangerss in booking[0]['EmployeesDocs']:
                registration_id.append(passangerss['employee_fcm_regid'])
        else:
            for passangerss in booking[0]['Passangers']:
                registration_id.append(passangerss['employee_fcm_regid'])

        if approvers:

            if booking_type == "Taxi":
                message_body = booking[0]['reference_no']+" Taxi Booking Received."
            elif booking_type == "Bus":
                message_body = booking[0]['reference_no'] + " Bus Booking Received."
            elif booking_type == "Train":
                message_body = booking[0]['reference_no'] + " Train Booking Received."
            elif booking_type == "Flight":
                message_body = booking[0]['reference_no'] + " Flight Booking Received."
            elif booking_type == "Visa":
                message_body = booking[0]['reference_no'] + " Visa Request Received."
            elif booking_type == "Frro":
                message_body = booking[0]['reference_no'] + " FRRO Request Received."
            elif booking_type == "Guesthouse":
                message_body = booking[0]['reference_no'] + " Guesthouse Request Received."
            else:
                message_body = booking[0]['reference_no'] + " Hotel Booking Received."

            for approver in approvers:
                if approver['approver1_regid']:
                    registration_id.append(approver['approver1_regid'])
                if approver['approver2_regid']:
                    registration_id.append(approver['approver2_regid'])

        else:
            if booking_type == "Taxi":
                message_body = booking[0]['reference_no']+" Taxi Booking Received."
            elif booking_type == "Bus":
                message_body = booking[0]['reference_no'] + " Bus Booking Received."
            elif booking_type == "Train":
                message_body = booking[0]['reference_no'] + " Train Booking Received."
            elif booking_type == "Flight":
                message_body = booking[0]['reference_no'] + " Flight Booking Received."
            elif booking_type == "Visa":
                message_body = booking[0]['reference_no'] + " Visa Request Received."
            elif booking_type == "Frro":
                message_body = booking[0]['reference_no'] + " FRRO Request Received."
            elif booking_type == "Guesthouse":
                message_body = booking[0]['reference_no'] + " Guesthouse Request Received."
            else:
                message_body = booking[0]['reference_no'] + " Hotel Booking Received."



        message_title = "CoTrav Notification"
        # message_body = "Your new booking request has been received..!"

        if booking_type == "Taxi":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Taxi",
            }

        elif booking_type == "Bus":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Bus",
            }

        elif booking_type == "Train":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Train",
            }

        elif booking_type == "Flight":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['departure_datetime'],
                "pickup_from": booking[0]['from_location'],
                "drop_to": booking[0]['to_location'],
                "type": "Flight",
            }

        elif booking_type == "Visa":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "type": "Visa",
            }

        elif booking_type == "Frro":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "type": "Frro",
            }

        elif booking_type == "Guesthouse":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "Checkin": booking[0]['checkin_datetime'],
                "Checkout": booking[0]['checkin_datetime'],
                "City": booking[0]['from_city_name'],
                "type": "Guesthouse",
            }

        else:
            data_message = {
                "booking_id": booking[0]['id'],
                "message": message_body,
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "Checkin": booking[0]['checkin_datetime'],
                "Checkout": booking[0]['checkin_datetime'],
                "pickup_from": booking[0]['from_area_id_name'],
                "type": "Hotel",
            }

        if registration_id:
            result = push_service.notify_multiple_devices(registration_ids=registration_id, message_title=message_title, message_body=message_body, data_message=data_message)
        return 1


    def send_notification(self, booking, approvers, booking_type):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)

        registration_id = list()
        registration_id.append(booking[0]['spoc_fcm_reg_id'])
        for passangerss in booking[0]['Passangers']:
            registration_id.append(passangerss['employee_fcm_regid'])
        if approvers:
            for approver in approvers:
                if approver['email_approver_1']:
                    registration_id.append(approver['approver1_regid'])
                if approver['email_approver_2']:
                    registration_id.append(approver['approver2_regid'])

        message_title = "CoTrav Notification"
        message_body = "Your new booking request has been received..!"

        if booking_type == "Taxi":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": booking[0]['reference_no']+" Taxi Booking Confirmed",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Taxi",
            }

        elif booking_type == "Bus":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": booking[0]['reference_no'] + " Bus Booking Confirmed",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Bus",
            }

        elif booking_type == "Train":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": booking[0]['reference_no'] + " Train Booking Confirmed",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Train",
            }

        elif booking_type == "Flight":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": booking[0]['reference_no'] + " Flight Booking Confirmed",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['departure_datetime'],
                "pickup_from": booking[0]['from_location'],
                "drop_to": booking[0]['to_location'],
                "type": "Flight",
            }

        elif booking_type == "Visa":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": booking[0]['reference_no'] + " Flight Booking Confirmed",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['departure_datetime'],
                "pickup_from": booking[0]['from_location'],
                "drop_to": booking[0]['to_location'],
                "type": "Flight",
            }

        else:
            data_message = {
                "booking_id": booking[0]['id'],
                "message": booking[0]['reference_no'] + " Hotel Booking Confirmed",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "Checkin": booking[0]['checkin_datetime'],
                "Checkout": booking[0]['checkin_datetime'],
                "pickup_from": booking[0]['from_area_id_name'],
                "type": "Hotel",
            }

        if registration_id:
            result = push_service.notify_multiple_devices(registration_ids=registration_id, message_title=message_title, message_body=message_body, data_message=data_message)
        return 1

    def send_custome_msg_notification(self, booking):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = ['cyaPMxbAwyQ:APA91bFKQgIHRSHYB-YjGYfX97EZhzXaa-vaRzrTmRxxqUOU3uSSB9Bf77DQgDSUjtotUb8nw8NooFIaxRMDY1HcO1Xg3vu3P5f8D6yKw4pZe1z72Utwtv0K_f61OBbbXhmZHl9hOK1v',
                           'eKbxdr2iCIc:APA91bGH7Go0qr_FMR5zC_46Yk3BYsvVuwaQfFgxbmm_BjtjJpfqjWS9zGPmmH59wn5mO4zKtx6_O1X6E8bl2EyCv3Z28cE1-o1LuZzKaYGaTqn4ZGuSmEnUzGkhHfdNR1n5yeC-3y1U',
                           'eUWpIIbiHdM:APA91bEvYbednDUHI1zNmpR2NWQvez9pJVGrR8WOUy3z0CjgtlurWBskK5goX6cMqExQaXM14zaqXkJOFB4hLXcq0cA0JK0fcHlxo0WFcPBkJUS7yHq9gqDmLZ3lK7HbeYh1ntMaL1ni',
                           'fTGSm3aO5mg:APA91bFiGt-ItCbxNPx7icpPzmWL61t75FDvZEOthGlYBz-J8gRWwU18T9dTdOl-92voJKl_aQTbXsX_sUq8fgeouWRROYmiKXDV1dKtY01r4moTLlU9QZB5KeIQucTzeEs-qkgxjjal']
        # #registration_id.append(booking[0]['spoc_fcm_reg_id'])
        data_message = {
            "reference_no": "CTTXI000001",
            "spoc_name": "Shreyash P",
            "pickup_time": "20-02-2020 03:20",
            "pickup_from": "Pune Railway Station, Sadhu Vaswani Road, Koregaon Park, Pune, Maharashtra, India",
            "drop_to": "Pimple Saudagar, Pimpri-Chinchwad, Maharashtra, India",
            "type": "Taxi"
        }
        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)
        return 1

    def send_custome_notification(self, registration_id, data):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        data_message = data
        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)

        return 1

    def send_broadcast_notification(self, msg_head, msg_title, msg_text):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)

        data_message = {
            "ContentHead": ""+msg_head,
            "ContentTitle": ""+msg_title,
            "ContentText": ""+msg_text,
            "type": "broadcast",
            "image":"http://cotrav.co/static/email_template_images/bg_1.png",
        }
        result = push_service.notify_topic_subscribers(topic_name="news", data_message=data_message)
        return 1

    def send_message_to_moblies(self, mobile_nos, msg_text):
        sms = SMS()
        sms.send_sms(mobile_nos, msg_text)

        return 1

    def send_mail_to_user(self,email_subject, email_body, email_to):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [email_to], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.content_subtype = "html"
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup

        return 1


class AcceptBooking_Email():
    def send_email_sms_ntf(self, booking, booking_type):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title
        email_title = "Approval confirmation"

        if booking_type == "Taxi":
            booking_tempalte = "Email_Templates/taxi_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Taxi Booking Approval confirmation"
            email_content = "Your Booking request for Taxi is Approved by your Approver. Details as below:"

        elif booking_type == "Bus":
            print("in bus booking")
            booking_tempalte = "Email_Templates/bus_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Bus Booking Approval confirmation"
            email_content = "Your Booking request for Bus is Approved by your Approver. Details as below:"

        elif booking_type == "Train":
            booking_tempalte = "Email_Templates/train_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Train Booking Approval confirmation"
            email_content = "Your Booking request for Train is Approved by your Approver. Details as below:"

        elif booking_type == "Flight":
            booking_tempalte = "Email_Templates/flight_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Flight Booking Approval confirmation"
            email_content = "Your Booking request for Flight is Approved by your Approver. Details as below:"

        elif booking_type == "Visa":
            booking_tempalte = "Email_Templates/visa_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Visa Request Approval confirmation"
            email_content = "Your request for Visa is Approved by your Approver. Details as below:"

        elif booking_type == "Frro":
            booking_tempalte = "Email_Templates/Frro_Email_Templates/welcomeEmailFRRO.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- FFRO Request Approval confirmation"
            email_content = "Your request for FFRO is Approved by your Approver. Details as below:"

        elif booking_type == "Guesthouse":
            booking_tempalte = "Email_Templates/guesthouse_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Guesthouse Request Approval confirmation"
            email_content = "Your request for Guesthouse is Approved by your Approver. Details as below:"

        else:
            print("in hotel booking")
            booking_tempalte = "Email_Templates/hotel_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Hotel Booking Approval confirmation"
            email_content = "Your Booking request for Hotel is Approved by your Approver. Details as below:"

        employee_name = ''
        employee_emails = ''

        spoc_email = booking[0]['user_email']
        registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])



        if booking_type == "Visa" or booking_type == "Frro":
            for passangerss in booking[0]['EmployeesDocs']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
                if passangerss['employee_fcm_regid']:
                    registration_id = registration_id.append(passangerss['employee_fcm_regid'])
        else:
            for passangerss in booking[0]['Passangers']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
                if passangerss['employee_fcm_regid']:
                    registration_id = registration_id.append(passangerss['employee_fcm_regid'])


        self.send_mail_agent(booking, COTRAV_EMAILS, "Team", email_subject, email_body, booking_tempalte, email_content, email_title)
        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte, email_content, email_title)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, spoc_email, booking[0]['user_name'], email_subject, email_body,booking_tempalte, email_content, email_title)
        if registration_id:
            self.send_custome_notification(booking, registration_id, booking_type)
        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_agent(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id, booking_type):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id

        if booking_type == "Taxi":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Taxi Booking "+booking[0]['reference_no']+" is Approved ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Taxi",
                "ContentHead": "Taxi Booking Approved",
                "ContentTitle": "Taxi Booking "+booking[0]['reference_no']+" Approved",
                "ContentText": "'Taxi Booking "+booking[0]['reference_no']+" is Approved ",
            }

        elif booking_type == "Bus":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Bus Booking " + booking[0]['reference_no'] + " is Approved ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Bus",
                "ContentHead": "Bus Booking Approved",
                "ContentTitle": "Bus Booking " + booking[0]['reference_no'] + " Approved",
                "ContentText": "'Bus Hotel Booking " + booking[0]['reference_no'] + " is Approved ",
            }

        elif booking_type == "Train":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Train Booking " + booking[0]['reference_no'] + " is Approved ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Train",
                "ContentHead": "Train Booking Approved",
                "ContentTitle": "Train Booking " + booking[0]['reference_no'] + " Approved",
                "ContentText": "'Train Hotel Booking " + booking[0]['reference_no'] + " is Approved ",
            }

        elif booking_type == "Flight":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Flight Booking " + booking[0]['reference_no'] + " is Approved ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['date_of_journey'],
                "pickup_from": booking[0]['from_location'],
                "drop_to": booking[0]['to_location'],
                "type": "Flight",
                "ContentHead": "Flight Booking Approved",
                "ContentTitle": "Flight Booking " + booking[0]['reference_no'] + " Approved",
                "ContentText": "'Flight Hotel Booking " + booking[0]['reference_no'] + " is Approved ",
            }

        elif booking_type == "Visa":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Visa Request " + booking[0]['reference_no'] + " is Approved ",
                "reference_no": booking[0]['reference_no'],
                "type": "Visa",
                "ContentHead": "Visa Request Approved",
                "ContentTitle": "Visa Request " + booking[0]['reference_no'] + " Approved",
                "ContentText": "'Visa Request Booking " + booking[0]['reference_no'] + " is Approved ",
            }

        elif booking_type == "Frro":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'FRRO Request " + booking[0]['reference_no'] + " is Approved ",
                "reference_no": booking[0]['reference_no'],
                "type": "FRRO",
                "ContentHead": "FRRO Request Approved",
                "ContentTitle": "FRRO Request " + booking[0]['reference_no'] + " Approved",
                "ContentText": "'FRRO Request Booking " + booking[0]['reference_no'] + " is Approved ",
            }

        elif booking_type == "Guesthouse":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Guesthouse Request " + booking[0]['reference_no'] + " is Approved ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "Checkin": booking[0]['checkin_datetime'],
                "Checkout": booking[0]['checkin_datetime'],
                "City": booking[0]['from_city_name'],
                "type": "Guesthouse",
            }

        else:
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Hotel Booking " + booking[0]['reference_no'] + " is Approved ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "Checkin": booking[0]['checkin_datetime'],
                "Checkout": booking[0]['checkin_datetime'],
                "pickup_from": booking[0]['from_area_id_name'],
                "type": "Hotel",
                "ContentHead": "Hotel Booking Approved",
                "ContentTitle": "Hotel Booking " + booking[0]['reference_no'] + " Approved",
                "ContentText": "'Hotel Hotel Booking " + booking[0]['reference_no'] + " is Approved ",
            }
        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)
        print(result)


class RejectBooking_Email():
    def send_email_sms_ntf(self, booking, booking_type):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title
        if booking[0]['status_cotrav'] <= 2:
            email_title = "Booking "+ booking[0]['client_status']
        else:
            email_title = "Booking " + booking[0]['cotrav_status']+"by Agent"

        if booking_type == "Taxi":
            booking_tempalte = "Email_Templates/taxi_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Taxi Booking Cancelled"
            email_content = "Your Booking request for Taxi is Rejected by your Approver. Details as below:"

        elif booking_type == "Bus":
            print("in bus booking")
            booking_tempalte = "Email_Templates/bus_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Bus Booking Cancelled"
            email_content = "Your Booking request for Bus is Rejected by your Approver. Details as below:"

        elif booking_type == "Train":
            booking_tempalte = "Email_Templates/train_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Train Booking Cancelled"
            email_content = "Your Booking request for Train is Rejected by your Approver. Details as below:"

        elif booking_type == "Flight":
            booking_tempalte = "Email_Templates/flight_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Flight Booking Cancelled"
            email_content = "Your Booking request for Flight is Rejected by your Approver. Details as below:"

        elif booking_type == "Visa":
            booking_tempalte = "Email_Templates/visa_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Visa Request Cancelled"
            email_content = "Your Visa Request is Rejected by your Approver. Details as below:"

        elif booking_type == "Frro":
            booking_tempalte = "Email_Templates/Frro_Email_Templates/frroBookingRejected.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- FRRO Request Cancelled"
            email_content = "Your FRRO Request is Rejected by your Approver. Details as below:"

        elif booking_type == "Guesthouse":
            print("in hotel booking")
            booking_tempalte = "Email_Templates/guesthouse_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Guesthouse Booking Cancelled"
            email_content = "Your Booking request for Guesthouse is Rejected by your Approver. Details as below:"

        else:
            print("in hotel booking")
            booking_tempalte = "Email_Templates/hotel_email_template.html"
            email_body = ""
            email_subject = "" + booking[0]['reference_no'] + "- Hotel Booking Cancelled"
            email_content = "Your Booking request for Hotel is Rejected by your Approver. Details as below:"

        employee_name = ''
        employee_emails = ''

        spoc_email = booking[0]['user_email']
        registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])

        if booking_type == "Visa" or booking_type == "Frro":
            for passangerss in booking[0]['EmployeesDocs']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
                if passangerss['employee_fcm_regid']:
                    registration_id = registration_id.append(passangerss['employee_fcm_regid'])
        else:
            for passangerss in booking[0]['Passangers']:
                employee_emails = "".join(map(str, passangerss['employee_email']))
                employee_name = "".join(map(str, passangerss['employee_name']))
                if passangerss['employee_fcm_regid']:
                    registration_id = registration_id.append(passangerss['employee_fcm_regid'])



        self.send_mail_agent(booking, COTRAV_EMAILS, "Team", email_subject, email_body, booking_tempalte, email_content, email_title)
        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte, email_content, email_title)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, spoc_email, booking[0]['user_name'], email_subject, email_body,booking_tempalte, email_content, email_title)
        if registration_id:
            self.send_custome_notification(booking, registration_id, booking_type)
        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_mail_agent(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id, booking_type):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id

        if booking_type == "Taxi":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Taxi Booking " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Taxi",
                "ContentHead": "Taxi Booking Cancelled",
                "ContentTitle": "Taxi Booking " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Taxi Hotel Booking " + booking[0]['reference_no'] + " is Cancelled ",
            }

        elif booking_type == "Bus":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Bus Booking " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Bus",
                "ContentHead": "Bus Booking Cancelled",
                "ContentTitle": "Bus Booking " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Bus Hotel Booking " + booking[0]['reference_no'] + " is Cancelled ",
            }

        elif booking_type == "Train":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Train Booking " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['pickup_from_datetime'],
                "pickup_from": booking[0]['pickup_location'],
                "drop_to": booking[0]['drop_location'],
                "type": "Train",
                "ContentHead": "Train Booking Cancelled",
                "ContentTitle": "Train Booking " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Train Hotel Booking " + booking[0]['reference_no'] + " is Cancelled ",
            }

        elif booking_type == "Flight":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Flight Booking " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "pickup_time": booking[0]['date_of_journey'],
                "pickup_from": booking[0]['from_location'],
                "drop_to": booking[0]['to_location'],
                "type": "Flight",
                "ContentHead": "Flight Booking Cancelled",
                "ContentTitle": "Flight Booking " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Flight Hotel Booking " + booking[0]['reference_no'] + " is Cancelled ",
            }

        elif booking_type == "Visa":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Visa Request " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "type": "Visa",
                "ContentHead": "Visa Request Cancelled",
                "ContentTitle": "Visa Request " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Visa Request " + booking[0]['reference_no'] + " is Cancelled ",
            }

        elif booking_type == "Frro":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Visa Request " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "type": "Frro",
                "ContentHead": "Frro Request Cancelled",
                "ContentTitle": "Frro Request " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Frro Request " + booking[0]['reference_no'] + " is Cancelled ",
            }

        elif booking_type == "Guesthouse":
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Guesthouse Booking " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "Checkin": booking[0]['checkin_datetime'],
                "Checkout": booking[0]['checkin_datetime'],
                "City": booking[0]['from_city_name'],
                "type": "Guesthouse",
                "ContentHead": "Guesthouse Booking Cancelled",
                "ContentTitle": "Guesthouse Booking " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Guesthouse Hotel Booking " + booking[0]['reference_no'] + " is Cancelled ",
            }
        else:
            data_message = {
                "booking_id": booking[0]['id'],
                "message": "'Hotel Booking " + booking[0]['reference_no'] + " is Cancelled ",
                "reference_no": booking[0]['reference_no'],
                "spoc_name": booking[0]['user_name'],
                "Checkin": booking[0]['checkin_datetime'],
                "Checkout": booking[0]['checkin_datetime'],
                "pickup_from": booking[0]['from_area_id_name'],
                "type": "Hotel",
                "ContentHead": "Hotel Booking Cancelled",
                "ContentTitle": "Hotel Booking " + booking[0]['reference_no'] + " Cancelled",
                "ContentText": "'Hotel Hotel Booking " + booking[0]['reference_no'] + " is Cancelled ",
            }
        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)
        print(result)


class VisaStatusChange_Email():
    def send_email_sms_ntf(self, booking, booking_type):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/visa_status_change_email_template.html"
        email_subject = "" + booking[0]['reference_no'] + "- Visa Request Status Change"
        email_title = "" + booking[0]['reference_no'] + "- Visa Request Status Change"
        email_content = "Your Visa request status has change. Details as below:"
        for passangerss in booking[0]['EmployeesDocs']:
            employee_emails = "".join(map(str, passangerss['employee_email']))
            employee_name = "".join(map(str, passangerss['employee_name']))
            if passangerss['employee_fcm_regid']:
                registration_id = registration_id.append(passangerss['employee_fcm_regid'])

        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte,
                       email_content, email_title)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, booking[0]['user_email'], booking[0]['user_name'], email_subject, email_body,
                           booking_tempalte,
                           email_content, email_title)
        if booking[0]['spoc_fcm_reg_id']:
            registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])
        if registration_id:
            self.send_custome_notification(booking, registration_id)

        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id
        data_message = {
            "booking_id": booking[0]['id'],
            "message": "'Taxi Booking " + booking[0]['reference_no'] + " is Change Status ",
            "reference_no": booking[0]['reference_no'],
            "spoc_name": booking[0]['user_name'],
            "type": "Visa",
            "status": booking[0]['visa_status'],
            "ContentHead": "Visa Request Status Change",
            "ContentTitle": "Visa Request " + booking[0]['reference_no'] + " Status Change",
            "ContentText": "'Visa Request " + booking[0]['reference_no'] + " is Status Change ",
        }

        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)



class SMS:
    def send_sms(self, mobile_nos, msg_text):
        sender_id = 'COTRAV'
        exotel_sid = "novuslogic1"
        exotel_key = "6ae4c99860c31346203da94dc98a4de7fd002addc5848182"
        exotel_token = "a2c78520d23942ad9ad457b81de2ee3f3be743a8188f8c39"

        requests.post('https://twilix.exotel.in/v1/Accounts/{exotel_sid}/Sms/send.json'.format(exotel_sid=exotel_sid),
                      auth=(exotel_key, exotel_token),
                      data={
                          'From': sender_id,
                          'To': mobile_nos,
                          'Body': msg_text
                      })
        return 1


class FrroStatusChange_Email():
    def send_email_sms_ntf(self, booking, booking_type, status_on_comment, endline):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/Frro_Email_Templates/frroStatusChanged.html"
        email_subject = "" + booking[0]['reference_no'] + "- FRRO Request Status Change"
        email_title = "" + booking[0]['reference_no'] + "- FRRO Request Status Change"
        email_content = "Your FRRO request status has change. Details as below:"
        for passangerss in booking[0]['EmployeesDocs']:
            employee_emails = "".join(map(str, passangerss['employee_email']))
            employee_name = "".join(map(str, passangerss['employee_name']))
            if passangerss['employee_fcm_regid']:
                registration_id = registration_id.append(passangerss['employee_fcm_regid'])

        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte, email_content, email_title,status_on_comment,endline)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, booking[0]['user_email'], booking[0]['user_name'], email_subject, email_body, booking_tempalte, email_content, email_title,status_on_comment,endline)
        if booking[0]['spoc_fcm_reg_id']:
            registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])
        if registration_id:
            self.send_custome_notification(booking, registration_id)
        print("mail send")
        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title,status_on_comment,endline):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'status_on_comment':status_on_comment, 'endline':endline})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")

        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id
        data_message = {
            "booking_id": booking[0]['id'],
            "message": "'FRRO Booking " + booking[0]['reference_no'] + " is Change Status ",
            "reference_no": booking[0]['reference_no'],
            "spoc_name": booking[0]['user_name'],
            "type": "FRRO",
            "status": booking[0]['request_status'],
            "ContentHead": "FRRO Request Status Change",
            "ContentTitle": "FRRO Request " + booking[0]['reference_no'] + " Status Change",
            "ContentText": "'FRRO Request " + booking[0]['reference_no'] + " is Status Change ",
        }

        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)



class FrroChangeDoucumentRequestLetter_Email:
    def send_email_sms_ntf(self, booking, booking_type, document_file):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/Frro_Email_Templates/frroRequestLetterRequest.html"
        email_subject = "" + booking[0]['reference_no'] + "| FRRO Request Letters"
        email_title = "" + booking[0]['reference_no'] + "| FRRO Request Letters"
        email_content = "Your FRRO request status has change. Details as below:"

        self.send_mail(booking, COTRAV_EMAILS, employee_name, email_subject, email_body, booking_tempalte, email_content, email_title,document_file)

        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title,document_file):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'email_content':email_content, 'email_title':email_title})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        if document_file:
            filename = settings.BASE_DIR + document_file
            msg.attach_file(filename)
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1


class FrroChangeOfficeStatus_Email:
    def send_email_sms_ntf(self, booking, booking_type, status_type, status, status_comment, document_file):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/Frro_Email_Templates/frroRequestOfficeStatusChange.html"
        email_subject = "" + booking[0]['reference_no'] + "| FRRO Office Status Change"
        email_title = "" + booking[0]['reference_no'] + "| FRRO Office Status Change"
        email_content = "Your FRRO request status has change. Details as below:"

        self.send_mail(booking, COTRAV_EMAILS, "Cotrav Team", email_subject, email_body, booking_tempalte, email_content, email_title,document_file,status_type, status, status_comment)

        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte, email_content, email_title,document_file,status_type, status, status_comment):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'status_type':status_type, 'status':status, 'status_comment':status_comment})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        if document_file:
            filename = settings.BASE_DIR + document_file
            msg.attach_file(filename)
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1


class FrroAddLetterRequest_Email:
    def send_email_sms_ntf(self, booking, booking_type, document_file,document_name):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/Frro_Email_Templates/frroRequestLetterRequest.html"
        email_subject = "Request Letter | " + booking[0]['reference_no'] + ""
        email_title = "Request Letter |" + booking[0]['user_name'] + booking[0]['reference_no'] + ""
        email_content = "Your FRRO request status has change. Details as below:"

        for passangerss in booking[0]['EmployeesDocs']:
            employee_emails = "".join(map(str, passangerss['employee_email']))
            employee_name = "".join(map(str, passangerss['employee_name']))
            if passangerss['employee_fcm_regid']:
                registration_id = registration_id.append(passangerss['employee_fcm_regid'])

        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte,document_file,document_name)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, booking[0]['user_email'], booking[0]['user_name'], email_subject, email_body, booking_tempalte, document_file,document_name)
        if booking[0]['spoc_fcm_reg_id']:
            registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])
        if registration_id:
            self.send_custome_notification(booking, registration_id,document_name)
        print("mail send")
        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte,document_file,document_name):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'document_name':document_name})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        if document_file:
            filename = settings.BASE_DIR + document_file
            msg.attach_file(filename)
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id,document_name):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id
        data_message = {
            "booking_id": booking[0]['id'],
            "message": "'Request Letter | " + booking[0]['reference_no'] + " ",
            "reference_no": booking[0]['reference_no'],
            "spoc_name": booking[0]['user_name'],
            "type": "FRRO",
            "status": document_name,
            "ContentHead": "FRRO Request Status Change",
            "ContentTitle": "Request Letter | " + booking[0]['reference_no'] + "",
            "ContentText": "'Request Letter | " + booking[0]['reference_no'] + "",
        }

        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)

class FrroAddPendingDocument_Email:
    def send_email_sms_ntf(self, booking, booking_type, list_documents):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/Frro_Email_Templates/frroPendingDocumentsRequest.html"
        email_subject = "Documents Required | " + booking[0]['reference_no'] + ""
        email_title = "Documents Required |" + booking[0]['user_name'] + booking[0]['reference_no'] + ""
        email_content = "Your FRRO request status has change. Details as below:"

        for passangerss in booking[0]['EmployeesDocs']:
            employee_emails = "".join(map(str, passangerss['employee_email']))
            employee_name = "".join(map(str, passangerss['employee_name']))
            if passangerss['employee_fcm_regid']:
                registration_id = registration_id.append(passangerss['employee_fcm_regid'])

        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte,list_documents)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, booking[0]['user_email'], booking[0]['user_name'], email_subject, email_body, booking_tempalte, list_documents)
        if booking[0]['spoc_fcm_reg_id']:
            registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])
        if registration_id:
            self.send_custome_notification(booking, registration_id,list_documents)
        print("mail send")
        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte,list_documents):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'list_documents':list_documents})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")

        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id,document_name):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id
        data_message = {
            "booking_id": booking[0]['id'],
            "message": "Documents Required |" + booking[0]['reference_no'] + " ",
            "reference_no": booking[0]['reference_no'],
            "spoc_name": booking[0]['user_name'],
            "type": "FRRO",
            "documents": document_name,
            "ContentHead": "FRRO Request Status Change",
            "ContentTitle": "Documents Required | " + booking[0]['reference_no'] + "",
            "ContentText": "Documents Required | " + booking[0]['reference_no'] + "",
        }

        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)

class FrroOfficeStatusReply_Email:
    def send_email_sms_ntf(self, booking, booking_type, document_file,document_name):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/Frro_Email_Templates/frroOfficeStatusReply.html"
        email_subject = "" + booking[0]['reference_no'] + "| FRRO Office Status Reply"
        email_title = "" + booking[0]['user_name'] + booking[0]['reference_no'] + "| FRRO Office Status Reply"
        email_content = "Your FRRO request status has change. Details as below:"

        for passangerss in booking[0]['EmployeesDocs']:
            employee_emails = "".join(map(str, passangerss['employee_email']))
            employee_name = "".join(map(str, passangerss['employee_name']))
            if passangerss['employee_fcm_regid']:
                registration_id = registration_id.append(passangerss['employee_fcm_regid'])

        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte,document_file,document_name)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, booking[0]['user_email'], booking[0]['user_name'], email_subject, email_body, booking_tempalte, document_file,document_name)
        if booking[0]['spoc_fcm_reg_id']:
            registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])
        if registration_id:
            self.send_custome_notification(booking, registration_id,document_name)
        print("mail send")
        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte,document_file,document_name):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'document_name':document_name})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")
        if document_file:
            filename = settings.BASE_DIR + document_file
            msg.attach_file(filename)
        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id,document_name):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id
        data_message = {
            "booking_id": booking[0]['id'],
            "message": "" + booking[0]['reference_no'] + "| FRRO Office Status Reply ",
            "reference_no": booking[0]['reference_no'],
            "spoc_name": booking[0]['user_name'],
            "type": "FRRO",
            "status": document_name,
            "ContentHead": "FRRO Request Status Change",
            "ContentTitle": "" + booking[0]['reference_no'] + "| FRRO Office Status Reply",
            "ContentText": "" + booking[0]['reference_no'] + "| FRRO Office Status Reply",
        }

        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)

class FrroAddDocumentIssue_Email:
    def send_email_sms_ntf(self, booking, booking_type, issue_comments):
        global booking_tempalte
        global email_body
        global email_subject
        registration_id = list()
        global email_content
        global email_title

        employee_name = ''
        employee_emails = ''
        email_body = ''

        booking_tempalte = "Email_Templates/Frro_Email_Templates/frroStatusChangedIssueDocuments.html"
        email_subject = "" + booking[0]['reference_no'] + "| FRRO Request for Issue in Documents"
        email_title = "" + booking[0]['user_name'] + booking[0]['reference_no'] + "| FRRO Request for Issue in Documents"
        email_content = "Your FRRO request status has change. Details as below:"

        for passangerss in booking[0]['EmployeesDocs']:
            employee_emails = "".join(map(str, passangerss['employee_email']))
            employee_name = "".join(map(str, passangerss['employee_name']))
            if passangerss['employee_fcm_regid']:
                registration_id = registration_id.append(passangerss['employee_fcm_regid'])

        self.send_mail(booking, employee_emails, employee_name, email_subject, email_body, booking_tempalte,issue_comments)
        if booking[0]['spoc_is_send_email'] == 1:
            self.send_mail(booking, booking[0]['user_email'], booking[0]['user_name'], email_subject, email_body, booking_tempalte, issue_comments)
        if booking[0]['spoc_fcm_reg_id']:
            registration_id = registration_id.append(booking[0]['spoc_fcm_reg_id'])
        if registration_id:
            self.send_custome_notification(booking, registration_id,issue_comments)
        print("mail send")
        return 1

    def send_mail(self, booking, emails, name, email_subject, email_body, booking_tempalte,issue_comments):
        connection = get_connection()  # uses SMTP server specified in settings.py
        connection.open()  # If you don't open the connection manually, Django will automatically open, then tear down the connection in msg.send()
        html_content = render_to_string(booking_tempalte, {'bookings': booking, 'user_name': name, 'issue_comments':issue_comments})
        msg = EmailMultiAlternatives(email_subject, email_body, COTRAV_FROM_EMAIL, [emails], bcc=COTRAV_BCC_EMAILS, cc=COTRAV_CC_EMAILS)
        msg.attach_alternative(html_content, "text/html")

        res = msg.send(fail_silently=True)
        connection.close()  # Cleanup
        # res = 1
        return 1

    def send_custome_notification(self, booking, registration_id,document_name):
        api_access_key = API_ACCESS_KEY_EMPLOYEE
        push_service = FCMNotification(api_key=api_access_key)
        registration_id = registration_id
        data_message = {
            "booking_id": booking[0]['id'],
            "message": "" + booking[0]['reference_no'] + "| FRRO Request for Issue in Documents ",
            "reference_no": booking[0]['reference_no'],
            "spoc_name": booking[0]['user_name'],
            "type": "FRRO",
            "status": document_name,
            "ContentHead": "FRRO Request Status Change",
            "ContentTitle": "" + booking[0]['reference_no'] + "| FRRO Request for Issue in Documents",
            "ContentText": "" + booking[0]['reference_no'] + "| FRRO Request for Issue in Documents",
        }

        result = push_service.multiple_devices_data_message(registration_ids=registration_id, data_message=data_message)

