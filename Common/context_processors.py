from django.conf import settings

from Common.VIEW.Agent.agent_views import getDataFromAPI


def global_settings(request):
    # return any necessary values
    return {
        'API_BASE_URL': settings.API_BASE_URL
    }

def global_hostname(request):
    # return any necessary values
    return {
        'HOST_BASE_PATH': settings.HOST_BASE_PATH
    }


def get_access_details_by_corporate_name(request):
    if 'login_type' in request.session:
        user_type = ''
        get_user_from_type = request.path
        ac_user = get_user_from_type.split("/")[1:]
        if get_user_from_type == '/login' or get_user_from_type == '/' or get_user_from_type == '/index' or get_user_from_type == '/about' or \
                get_user_from_type == '/signup' or get_user_from_type == '/contact' or get_user_from_type == '/support' or get_user_from_type =='/ourservices'\
                or ac_user[0] == "agents" or get_user_from_type =='/hotel' or get_user_from_type =='/cab' or get_user_from_type =='/mice' or get_user_from_type =='/ticketing' \
                or get_user_from_type == '/travel' or get_user_from_type == '/visa'        \
                or ac_user[0] == "operator" or ac_user[0]=='create_token' or ac_user[0]=='send_otp_to_user'  or ac_user[0]== 'get_flights' or ac_user[0]== 'forgot_password_conformation' or ac_user[0]== 'forgot_password' :
            return {}
        else:
            if ac_user[1] == "Admin":
                access_token = request.session['admin_access_token']
                user_type = request.session['admin_login_type']
            elif ac_user[1] == "Approver_1":
                access_token = request.session['approves_1_access_token']
                user_type = request.session['approves_1_login_type']
            elif ac_user[1] == "Approver_2":
                access_token = request.session['approves_2_access_token']
                user_type = request.session['approves_2_login_type']
            elif ac_user[1] == "Spoc":
                access_token = request.session['spoc_access_token']
                user_type = request.session['spoc_login_type']
            elif ac_user[1] == "Employee":
                access_token = request.session['employee_access_token']
                user_type = request.session['employee_login_type']
            elif ac_user[0] == "agents":
                return None
            elif ac_user[0] == "operator":
                return None
            else:
                return None

            if access_token:
                payload = {'corporate_id': request.user.corporate_id,'ac':access_token}
                url_access = settings.API_BASE_URL + "view_company"
                data = getDataFromAPI(str(user_type), access_token, url_access, payload)
                corp_access = data['Corporates']
                return {'corp_access': corp_access}
            else:
                return {}

    else:
        return {}