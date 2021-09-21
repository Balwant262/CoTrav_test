"""CoTrav URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Common.VIEW import basic_web_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),


######################### Comman urls ################
    path('login', basic_web_views.login_action),
    path('logout', basic_web_views.logout_action),
    path('change_password', basic_web_views.change_password),
    path('forgot_password', basic_web_views.forgot_password),
    path('forgot_password_conformation', basic_web_views.forgot_password_conformation),
    path('send_sms', basic_web_views.send_sms),
    path('send_email', basic_web_views.send_email),
######################### END Commann urls ###############


#path('login2', basic_web_views.login2),

######################### CORPORATE ADMIN URLS ############################
    path('', include('Common.URL.Admin.urls')),
    path('', include('Common.URL.Spoc.urls')),
    path('', include('Common.URL.Employee.urls')),
    path('', include('Common.URL.Approver_1.urls')),
    path('', include('Common.URL.Approver_2.urls')),
######################### END CORPORATE URLS ####################


######################### AGENTS URLS ############################
    path('', include('Common.URL.Agent.urls')),
######################### END AGENTS URLS ################

######################### OPERATOR URLS ############################
    path('', include('Common.URL.Operator.urls')),
######################### END AGENTS URLS ################

######################### API URLS ############################
    path('', include('Common.URL.Api.urls')),
######################### END API URLS ####################

######################### PUBLIC API URLS ############################
    path('', include('Common.URL.Api.Public_Api.public_url_taxi')),
    path('', include('Common.URL.Api.Public_Api.public_url_bus')),
    path('', include('Common.URL.Api.Public_Api.public_url_train')),
    path('', include('Common.URL.Api.Public_Api.public_url_hotel')),
    path('', include('Common.URL.Api.Public_Api.public_url_flight')),
######################### END API URLS ####################


######################### SELF BOOKING API URLS ############################
    path('', include('Common.URL.Api.Self_Booking_Api.self_flight_booking_urls')),
######################### END API URLS ####################

######################### COTRAV LANDING #########################
 path('',include('landing.urls')),
######################### END LANDING #############################








]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'landing.views.error_404_view'
handler500 = 'landing.views.error_500_view'
