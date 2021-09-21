
from django.urls import path
from . import views
from . import Cotrav_InsertData_Scripts


urlpatterns = [

path('',views.index, name="index"),

path('index',views.index, name="index"),

path('about',views.about, name="about"),

path('cotrav/login',views.login, name="login"),

path('signup',views.signup, name="signup"),

path('contact',views.contact, name="contact"),

path('send_otp_to_user',views.send_otp_to_user, name="send_otp_to_user"),

path('support',views.support, name="support"),
    
path('ourservices',views.ourservices, name="ourservices"),

path('cab',views.cab, name="cab"),
path('hotel',views.hotel, name="hotel"),
path('mice',views.mice, name="mice"),
path('ticketing',views.ticketing, name="ticketing"),
path('travel',views.travel, name="travel"),
path('visa',views.visa, name="visa"),

path('testsignup',views.testsignup, name="testsignup"),

path('testemail',views.testemail, name="testemail"),

path('voucher',views.voucher, name="voucher"),

path('export',views.export_movies_to_xlsx, name="export"),

path('create_token',views.Create_Token, name="create_token"),
path('get_flights',views.get_flights, name="get_flights"),
path('get_pnr',views.get_pnr, name="get_pnr"),


path('script/add_taxi',Cotrav_InsertData_Scripts.add_taxi),

path('script/add_bus',Cotrav_InsertData_Scripts.add_bus),

path('script/add_train',Cotrav_InsertData_Scripts.add_train),

path('policy',views.policy, name="policy"),

path('script/add_flight',Cotrav_InsertData_Scripts.add_flight),

path('script/add_hotel',Cotrav_InsertData_Scripts.add_hotel),

path('agents/testpdf',views.pdf_render_test, name="testpdf"),


path('api-documentation-guide',views.api_documentation_guide, name="api-documentation-guide"),
path('api-test-guide',views.api_test_guide, name="api-teset-guide"),

path('screenshot',views.test_screenshot, name="test_screenshot"),


    ]