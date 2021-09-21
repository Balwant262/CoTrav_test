import json
import socket
import os
import traceback
import string
import random
from django.db import connection
from django.shortcuts import render , redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django_global_request.middleware import get_request
from CoTrav import settings
from Common.VIEW.Agent.agent_views import dictfetchall, getDataFromAPI
from Common.models import Corporate, Corporate_Agent

from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from datetime import timedelta
import requests
from landing.forms import LeadGenerationModelForm
from landing.models import Leadgeneration, LeadComments, LeadLog
from django.contrib import messages
from landing.utils import render_to_pdf
from Common.email_settings import SignIn_OTP
import base64
from string import Template
from threading import Thread, activeCount
COTRAV_EMAILS = list(Corporate_Agent.objects.filter(is_super_admin=1).exclude(email='').values_list('email', flat=True))
COTRAV_NUMBERS = Corporate_Agent.objects.filter(is_super_admin=1).exclude(contact_no='').values_list('contact_no', flat=True)

from selenium import webdriver

# Create your views here.
def index_cs(request):
    return render(request,'comingsoon.html')


def index(request):
    return render(request,'cotrav_index.html')


def about(request):
    return render(request,'cotrav_about.html')


def login(request):
    return render(request,'cotrav_login.html')


def signup(request):
    if request.method == 'POST':

        corporate_name = request.POST.get('corporate_name')
        contact_person_name = request.POST.get('contact_person_name')
        contact_person_no = request.POST.get('contact_person_no')
        contact_person_email = request.POST.get('contact_person_email')
        corporate_location = request.POST.get('corporate_location')
        Lead_Source = request.POST.get('Lead_Source')
        Hear_About_Us = request.POST.get('Hear_About_Us')
        if Hear_About_Us == 'other':
            Hear_About_Us = request.POST.get('input_Hear_About_Us')
        message = request.POST.get('message')

        Newcompany = Leadgeneration()

        Newcompany.Company_Name = corporate_name
        Newcompany.Company_Location = corporate_location
        Newcompany.Contact_Name = contact_person_name
        Newcompany.Contact_Number = contact_person_no
        Newcompany.Contact_Email = contact_person_email
        Newcompany.Company_Website = ''
        Newcompany.Message = message
        Newcompany.Assigned_Sales_Person = 0
        Newcompany.Status = 'Lead Created'
        Newcompany.Lead_Source = Lead_Source
        Newcompany.Hear_About_Us = Hear_About_Us
        Newcompany.Attachments = ''
        Newcompany.Lead_Communication = ''
        Newcompany.Comments = ''

        try:
            ref = Leadgeneration.objects.get(Company_Name=corporate_name)
            print("Company with same name allready exist")
            # return redirect('signup')
            err_msg = "Company with same name allready exist"
            return render(request, 'cotrav_signup.html',
                          {'company': corporate_name, 'name': contact_person_name, 'number': contact_person_no,
                           'email': contact_person_email, 'city': corporate_location, 'message': message,
                           'err_msg': err_msg})
        except ObjectDoesNotExist:

            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            ''' End reCAPTCHA validation '''

            if result['success']:
                Newcompany.save()
                messages.success(request, "A Cotrav Official would be contacting you in 24 hours to discuss business solutions for your team..!")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')

        return redirect('signup')

    else:
        return render(request, 'cotrav_signup.html')



def contact(request):
    if request.method == 'POST':
        corporate_name = request.POST.get('corporate_name')
        contact_person_name = request.POST.get('contact_person_name')
        contact_person_no = request.POST.get('contact_person_no')
        contact_person_email = request.POST.get('contact_person_email')
        corporate_location = 'NA'
        Lead_Source = 'Contact Us'
        message = request.POST.get('message')

        Newcompany = Leadgeneration()

        Newcompany.Company_Name = corporate_name
        Newcompany.Company_Location = corporate_location
        Newcompany.Contact_Name = contact_person_name
        Newcompany.Contact_Number = contact_person_no
        Newcompany.Contact_Email = contact_person_email
        Newcompany.Company_Website = ''
        Newcompany.Message = message
        Newcompany.Assigned_Sales_Person = 0
        Newcompany.Status = 'Lead Created'
        Newcompany.Lead_Source = Lead_Source
        Newcompany.Attachments = ''
        Newcompany.Lead_Communication = ''
        Newcompany.Comments = ''

        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        ''' End reCAPTCHA validation '''

        if result['success']:
            Newcompany.save()
            messages.success(request, "A Cotrav Official would be contacting you in 24 hours to discuss business solutions for your team..!")
        else:
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')

        return redirect('contact')

    else:

        return render(request, 'cotrav_contact.html')


def support(request):
        return render(request,'cotrav_support.html')

def cab(request):
    return render(request, 'cab_booking.html')

def hotel(request):
    return render(request, 'hotel_booking.html')

def mice(request):
    return render(request, 'mice.html')

def ticketing(request):
    return render(request, 'ticketing_booking.html')

def travel(request):
    return render(request, 'travel_reimbursement.html')

def visa(request):
    return render(request, 'visa_services.html')

def ourservices(request):
    return render(request,'cotrav_ourservices.html')

def policy(request):
    return render(request, 'private_policy.html')

def error_404_view(request, *args, **argv):
    data = {"name": "ThePythonDjango.com"}
    print(request.get_full_path())
    urlll = request.get_full_path()
    url = urlll.split("/")
    if url[1] == 'api':
        return JsonResponse({
            'success': 0,
            'message': 'api not found'
        })

    return render(request, 'error_404.html', data)


def error_500_view(request, *args, **arg):
    data = {"name": "ThePythonDjango.com"}
    print(request.get_full_path())
    urlll = request.get_full_path()
    url = urlll.split("/")
    if url[1] == 'api':
        return JsonResponse({
            'success': 0,
            'message': 'api not found'
        })

    return render(request, 'error_404.html', data)

def testsignup(request):
    try:
        ref = Corporate.objects.get(corporate_name = "tcs")
    except ObjectDoesNotExist:
        print("duplicate entry")
    return HttpResponse("test")


def testemail(request):
    email_to = "balwant@taxivaxi.in"
    subject = "Test"
    body = "Hiii"
    resp1 = 1
    try:
        signup = SignIn_OTP()
        print(COTRAV_EMAILS)
        print(type(COTRAV_EMAILS))
        resp1 = signup.send_email(COTRAV_EMAILS,subject,body)
        print(resp1)
    except Exception as e:
        print("exception")
        print(e)
        print("duplicate entry")
    return HttpResponse(resp1)


def voucher(request):
    path = ''
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        a = datetime.now()
        path = os.path.join(BASE_DIR, '/visa_doc/' + str(int(a.strftime('%d%m%Y%H%M'))) + "/")
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        path = traceback.format_exc()
    return HttpResponse(settings.MEDIA_ROOT)



def export_movies_to_xlsx(request):
    """
    Downloads all movies as Excel file with a single worksheet
    """
    movie_queryset = Corporate.objects.all()

    print(movie_queryset)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename={date}-movies.xlsx'.format(
        date=datetime.now().strftime('%Y-%m-%d'),
    )

    return response


def pdf_render_test(request):
    # payload = {'bill_id': 106}
    # url = settings.API_BASE_URL + "view_bill"
    # company = getDataFromAPI("10", "W6UC9UJJ63BT1XSQ9ZXSKEWVCF90WME8I9YWP9106V1688GZZ0ZINGQEY33C", url, payload)
    # print(company['Bill'][0])
    # voucher = {'bill_datas':company['Bill'][0]}
    # pdf = render_to_pdf('pdf_voucher_template/bill_template/bill_single_invoice.html', voucher)

    #return render(request,'train_email_temp.html')

    # cursor2 = connection.cursor()
    # cursor2.callproc('viewFlightBooking', [220])
    # emp = dictfetchall(cursor2)
    # cursor2.close()
    #
    # cursor1 = connection.cursor()
    # cursor1.callproc('getAllFlightBookingPassangers', [220])
    # passanger = dictfetchall(cursor1)
    # emp[0]['Passangers'] = passanger
    # cursor1.close()
    #
    # cursor3 = connection.cursor()
    # cursor3.callproc('getAllFlightBookingFlights', [220])
    # flights = dictfetchall(cursor3)
    # cursor3.close()
    #
    # emp[0]['Flights'] = flights
    #
    # DEP_DATE_0 = ''
    # for i, f in enumerate(flights):
    #     print(f)
    #
    #     ARRV_DATE_i = f['arrival_datetime']
    #     DEP_DATE_i = f['departure_datetime']
    #     adDate = datetime.strptime(str(DEP_DATE_i), "%d-%m-%Y %H:%M")
    #     ddDate = datetime.strptime(str(ARRV_DATE_i), "%d-%m-%Y %H:%M")
    #     dayHours_onword_i = timesince(adDate, ddDate)
    #     if i == 0:
    #         DEP_DATE_0 = f['arrival_datetime']
    #     if i == 1 or i == 2 or i == 3:
    #         ii = i - 1
    #         adDate = datetime.strptime(str(DEP_DATE_0), "%d-%m-%Y %H:%M")
    #         ddDate = datetime.strptime(str(DEP_DATE_i), "%d-%m-%Y %H:%M")
    #         emp[0]['DELAY_' + str(i)] = timesince(adDate, ddDate)
    #         DEP_DATE_0 = f['arrival_datetime']
    #     emp[0]['DURATION_' + str(i)] = dayHours_onword_i


    cursor2 = connection.cursor()
    cursor2.callproc('viewBusBooking', [120])
    emp = dictfetchall(cursor2)
    cursor2.close()

    cursor1 = connection.cursor()
    cursor1.callproc('getAllBusBookingPassangers', [120])
    passanger = dictfetchall(cursor1)
    emp[0]['Passangers'] = passanger
    cursor1.close()
    print(emp[0])
    #
    # cursor2 = connection.cursor()
    # cursor2.callproc('viewHotelBooking', [106])
    # emp = dictfetchall(cursor2)
    # cursor2.close()
    #
    # cursor1 = connection.cursor()
    # cursor1.callproc('getAllHotelBookingPassangers', [106])
    # passanger = dictfetchall(cursor1)
    # emp[0]['Passangers'] = passanger
    # cursor1.close()

    print(emp[0])

    pdf = render_to_pdf('pdf_voucher_template/bus_voucher.html', emp[0])
    return HttpResponse(pdf, content_type='application/pdf')


def get_flights(request):
    if request.method == 'POST':
        try:
            url = "http://mdt.ksofttechnology.com/API/FLIGHT"
            payload = {
                "TYPE": "AIR",
                "NAME": "GET_FLIGHT",
                "STR": [
                    {
                        "AUTH_TOKEN": "19d7c89d-41e2-4ddb-918f-b12a8f219686",
                        "SESSION_ID": "0vv5ycqeaxmndcdqhtatcscx",
                        "TRIP": "1",
                        "SECTOR": "D",
                        "SRC": "DEL",
                        "DES": "BOM",
                        "DEP_DATE": "2019-12-20",
                        "RET_DATE": "",
                        "ADT": "1",
                        "CHD": "0",
                        "INF": "1",
                        "PC": "",
                        "PF": "",
                        "HS": "D"
                    }
                ]
            }

            headers = {}
            r = requests.post(url, json=payload)
            print(r)
            api_response = r.json()
            print("response")
            print(socket.gethostname())
            messages.success(request, api_response)
            return render(request, 'api_call.html', {'response': api_response})
        except Exception as e:
            messages.error(request, e)
            return redirect('create_token')
    else:

        return render(request, 'api_call.html')


def get_pnr(request):
    if request.method == 'POST':
        try:
            url = "http://mdt.ksofttechnology.com/API/FLIGHT"
            payload = {
                    "NAME": "PNR_RETRIVE",
                    "STR": [
                        {
                            "BOOKINGID": "APIU637124397889286020Ua2e9",
                            "CLIENT_SESSIONID": "069764a1-8a35-42ff-baed-ab168d0b1341",
                            "HS": "D",
                            "MODULE": "B2B"
                        }
                    ],
                    "TYPE": "DC"
                }

            headers = {}
            r = requests.post(url, json=payload)
            print(r)
            api_response = r.json()
            print("response")
            print(socket.gethostname())
            messages.success(request, api_response)
            return render(request, 'api_call.html', {'response': api_response})
        except Exception as e:
            messages.error(request, e)
            return redirect('create_token')
    else:

        return render(request, 'api_call.html')


def api_documentation_guide(request):
    return render(request,'api_documentation_guide.html')


def api_test_guide(request):
    if request.method == 'POST':
        current_url = request.POST.get('current_url')
        api_name = request.POST.get('api_name')
        auth_value = request.POST.get('auth_value')
        body_value_r = request.POST.get('body_value')
        try:
            url = settings.API_BASE_URL + ""+api_name
            headers = {'content-type': 'application/json', 'Authorization': auth_value}
            body_value = json.loads(body_value_r)
            r = requests.post(url, json=body_value, headers=headers)
            api_response = r.json()
            messages.success(request, "Data Received")
            return render(request, 'api_test_guide.html', {'api_data': api_response, 'api_name':api_name, 'auth_value':auth_value, 'body_value':body_value_r})
        except Exception as e:
            messages.error(request, e)
            return HttpResponseRedirect(current_url, {})
    else:
        return render(request,'api_test_guide.html')


def send_otp_to_user(request):
    generate_otp = ''.join(random.choice(string.digits) for _ in range(6))
    body = "Dear User,\n\n" + generate_otp + " is your verification code to access your profile and bookings on Cotrav app, you need to verify your email first. \n\nRgrds,\nCoTrav."
    subject = "Cotrav - Verify Your Email"
    email = request.POST.get('email')
    signup = SignIn_OTP()
    resp1 = signup.send_email(email, subject, body)
    print("otp access")
    print(generate_otp)
    return HttpResponse(generate_otp, content_type='json')


def Create_Token(request):
    if request.method == 'POST':
        try:

            payload = """
           <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
 <soapenv:Header/>
 <soapenv:Body>
  <air:AirPriceReq xmlns:com="http://www.travelport.com/schema/common_v50_0" xmlns:air="http://www.travelport.com/schema/air_v50_0" TargetBranch="P7038885" CheckOBFees="All" AuthorizedBy="user" TraceId="P7038885">
   <com:BillingPointOfSaleInfo OriginApplication="UAPI"/>
   <air:AirItinerary>

    <air:AirSegment Key="cNTBlO4R2BKAgENZCAAAAA==" Group="0" Carrier="AI" FlightNumber="863" Origin="DEL" Destination="BOM" DepartureTime="2020-08-08T23:00:00.000+05:30" ArrivalTime="2020-08-09T01:15:00.000+05:30" FlightTime="135" Distance="708" ETicketability="Yes" Equipment="32B" ChangeOfPlane="false" ParticipantLevel="Secure Sell" LinkAvailability="true" PolledAvailabilityOption="Polled avail exists" OptionalServicesIndicator="false" AvailabilitySource="A" AvailabilityDisplayType="Fare Shop/Optimal Shop" NumberOfStops="1" ProviderCode="1G" />

   </air:AirItinerary>
   <air:AirPricingModifiers FaresIndicator="AllFares">

   </air:AirPricingModifiers>
   <com:SearchPassenger Code="ADT" Key="1" Age="50"/>

   <air:AirPricingCommand/>
  </air:AirPriceReq>
 </soapenv:Body>
</soapenv:Envelope>
                        """

            url = "https://apac.universal-api.pp.travelport.com/B2BGateway/connect/uAPI/AirService"
            CREDENTIALS = 'Universal API/uAPI7648806979-241d6447:rT2xbTHrb4zy9sapAkmA43HHS'
            Provider = '1G'
            RGETBRANCH = 'P7038885'

            userAndPass = base64.b64encode(bytes(CREDENTIALS, 'utf-8')).decode("ascii")
            header = {
                "Content-Type":"text/xml:charset=utf-8",
                "Accept":"gzip,deflate",
                "Connection": "Keep-Alive",
                "Authorization":"Basic %s"%userAndPass,
                "Content-Length": str(len(payload))
            }
            print(header)
            response = requests.post(url, data=payload, headers=header)
            print(response)
            print(response.content)
            messages.success(request, response)
            return render(request, 'api_call.html', {'response': response.content})
        except Exception as e:
            messages.error(request, e)
            print(traceback.print_exc())
            return redirect('create_token')
    else:

        return render(request, 'api_call.html')
    

def test_screenshot(request):
    # url of the page we want to scrape


    url = "https://www.makemytrip.com/flight/search?itinerary=BOM-BLR-20/03/2021&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&ccde=IN&lang=eng"

    no_of_flights = 0

    inp_airline = "Go Air"

    inp_depart = "Mumbai"

    inp_arive = "Bengaluru"

    inp_departTime = "07:00"

    inp_ariveTime = "08:35"

    # op = webdriver.ChromeOptions()
    # op.add_argument('headless')

    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome(chrome_options=chrome_options)

    opts = webdriver.ChromeOptions()
    opts.headless = True
    # driver =webdriver.Chrome(ChromeDriverManager().install())

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    opts.add_argument('user-agent={0}'.format(user_agent))

    path = ''
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(_file_)))

    print("base dir path", BASE_DIR)

    path = os.path.join(BASE_DIR, '/chromedriver'  )

    DRIVER = './chromedriver'
    #DRIVER = path
    # driver = webdriver.Chrome(options=chrome_options)

    driver = webdriver.Chrome(DRIVER, options=opts)

    driver.get(url)
    # screenshot = driver.save_screenshot('my_screenshot876.png')

    element = driver.find_element_by_class_name("listingCard")

    all_divs = driver.find_elements_by_class_name("listingCardWrap")

    job_profiles = driver.find_elements_by_class_name("listingCard")

    no_of_flights = len(job_profiles)

    my_div = ""

    # printing top ten job profiles
    count = 0
    count2 = 0
    for jf in range(no_of_flights):

        airlineName = job_profiles[jf].find_element_by_class_name("airlineName")

        # dipTime = job_profile.find_element_by_xpath("//*div[@class='flightTimeSection']/p[@class='blackText fontSize18 blackFont appendBottom2 makeFlex hrtlCenter']/span")

        flightTime = job_profiles[jf].find_elements_by_class_name("flightTimeSection")

        flightTime1 = flightTime[0].find_element_by_tag_name("span")

        departFrom = flightTime[0].find_element_by_css_selector('p.darkText')

        flightTime2 = flightTime[1].find_element_by_tag_name("span")

        ariveTo = flightTime[1].find_element_by_css_selector('p.darkText')

        # counter = len(flightTime)

        # print(counter)

        airline = airlineName.text

        depart = departFrom.text

        departTime = flightTime1.text

        arive = ariveTo.text

        ariveTime = flightTime2.text

        my_div = jf

        if (
                airline == inp_airline and depart == inp_depart and arive == inp_arive and departTime == inp_departTime and ariveTime == inp_ariveTime):
            print("match found")

            print(airlineName.text)

            print(flightTime1.text)

            print(departFrom.text)

            print(flightTime2.text)

            print(ariveTo.text)

            # elem = job_profiles[jf].find_element_by_xpath('..')

            # print (elem.get_attribute("id"))
            # print (elem.get_property("id"))

            # parent_elem_id = elem.get_attribute("id")

            # parent_elem = driver.find_element_by_id(parent_elem_id)

            job_profiles[jf].screenshot('my_sho13.png')

            break

        count = count + 1

        if (jf == no_of_flights):
            # click screenshot
            # job_profile.screenshot('my_sho2.png')

            break

    # my_div.screenshot('my_sho11.png')

    driver.close()  # closing the webdriver

    driver.quit()

    return render(request, 'api_call.html')