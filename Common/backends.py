import string
import random

from django.http import HttpResponse

from Common.models import Corporate_Login
from Common.models import Corporate_Spoc_Login
from Common.models import Corporate_Employee_Login
from Common.models import Corporate_Approves_1_Login
from Common.models import Corporate_Approves_2_Login
from Common.models import Operator_Login
from django.contrib.auth.hashers import check_password
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django_global_request.middleware import get_request

from Common.models import Corporate_Agent

from Common.models import Corporate_Login_Access_Token
from Common.models import Corporate_Spoc_Login_Access_Token
from Common.models import Corporate_Employee_Login_Access_Token
from Common.models import Corporate_Approves_1_Login_Access_Token
from Common.models import Corporate_Approves_2_Login_Access_Token
from Common.models import Corporate_Agent_Login_Access_Token
from Common.models import Operator_Login_Access_Token


class CustomCompanyUserAuth(object):

    @staticmethod
    def authenticate(request, username=None, post_password=None, login_type=None):

        try:

            request = get_request()
            request.session['login_type'] = login_type

            response = HttpResponse('blah')


            user_info = request.META['HTTP_USER_AGENT']
            print("Browser Info")
            print(user_info)
            print(login_type)

            if login_type == '1':
                try:
                    user = Corporate_Login.objects.get(email=username)

                except Corporate_Login.DoesNotExist:
                    user = None
            elif login_type == '2':
                try:
                    user = Corporate_Approves_1_Login.objects.get(email=username)

                except Corporate_Approves_1_Login.DoesNotExist:
                    user = None
            elif login_type == '3':
                try:
                    user = Corporate_Approves_2_Login.objects.get(email=username)

                except Corporate_Approves_2_Login.DoesNotExist:
                    user = None
            elif login_type == '4':
                try:
                    user = Corporate_Spoc_Login.objects.get(username=username)
                except Corporate_Spoc_Login.DoesNotExist:
                    user = None
            elif login_type == '6':
                try:
                    user = Corporate_Employee_Login.objects.get(username=username)

                except Corporate_Employee_Login.DoesNotExist:
                    user = None
            elif login_type == '10':
                try:
                    user = Corporate_Agent.objects.get(email=username)

                except Corporate_Agent.DoesNotExist:
                    user = None
            elif login_type == '7':
                try:
                    user = Operator_Login.objects.get(username=username)

                except Operator_Login.DoesNotExist:
                    user = None
            else:
                return None

            if user:
                if check_password(post_password, user.password):
                    gen_access_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(60))
                    today = datetime.now()
                    gen_expiry_date = today + relativedelta(months=1)
                    if login_type == '1':
                        print("is delete")
                        print(user.is_deleted)
                        if not user.is_deleted:
                            insert_data = Corporate_Login_Access_Token.objects.create(corporate_login_id=user.id,access_token=gen_access_token,user_agent=user_info, expiry_date=gen_expiry_date)
                            request.session['admin_access_token'] = insert_data.access_token
                            request.session['admin_login_type'] = login_type
                            response.set_cookie('admin_access_token', insert_data.access_token)
                            response.set_cookie('admin_login_type', login_type)
                        else:
                            return None
                    elif login_type == '2':
                        if not user.is_deleted:
                            insert_data = Corporate_Approves_1_Login_Access_Token.objects.create(subgroup_authenticater_id=user.id,access_token=gen_access_token,user_agent=user_info, expiry_date=gen_expiry_date)
                            request.session['approves_1_access_token'] = insert_data.access_token
                            request.session['approves_1_login_type'] = login_type
                            print("App 1 Save Session")
                        else:
                            return None
                    elif login_type == '3':
                        if not user.is_deleted:
                            insert_data = Corporate_Approves_2_Login_Access_Token.objects.create(group_authenticater_id=user.id, access_token=gen_access_token,user_agent=user_info, expiry_date=gen_expiry_date)
                            request.session['approves_2_access_token'] = insert_data.access_token
                            request.session['approves_2_login_type'] = login_type
                        else:
                            return None
                    elif login_type == '4':
                        if not user.is_deleted:
                            insert_data = Corporate_Spoc_Login_Access_Token.objects.create(spoc_id=user.id,access_token=gen_access_token, user_agent=user_info, expiry_date=gen_expiry_date)
                            request.session['spoc_access_token'] = insert_data.access_token
                            request.session['spoc_login_type'] = login_type
                            response.set_cookie('spoc_access_token', insert_data.access_token)
                            response.set_cookie('spoc_login_type', login_type)
                        else:
                            return None
                    elif login_type == '6':
                        if not user.is_deleted:
                            insert_data = Corporate_Employee_Login_Access_Token.objects.create(employee_id=user.id, access_token=gen_access_token, user_agent=user_info, expiry_date=gen_expiry_date)
                            request.session['employee_access_token'] = insert_data.access_token
                            request.session['employee_login_type'] = login_type
                    elif login_type == '10':
                        if not user.is_deleted:
                            insert_data = Corporate_Agent_Login_Access_Token.objects.create(agent_id=user.id, access_token=gen_access_token, user_agent=user_info, expiry_date=gen_expiry_date)
                            request.session['agent_access_token'] = insert_data.access_token
                            request.session['agent_login_type'] = login_type
                        else:
                            return None
                    elif login_type == '7':
                        if not user.is_deleted:
                            insert_data = Operator_Login_Access_Token.objects.create(operator_id=user.id,access_token=gen_access_token, user_agent=user_info, expiry_date=gen_expiry_date)
                            request.session['operator_access_token'] = insert_data.access_token
                            request.session['operator_login_type'] = login_type
                        else:
                            return None

                    return user
                else:
                    print("IN : else")
                    return None
        except Corporate_Login.DoesNotExist:
            print("exception")
            return None

    @staticmethod
    def get_user(user_id):
        try:
            request = get_request()

            get_user_from_type = request.path

            if get_user_from_type is not '/login':
                ac_user = get_user_from_type.split("/")[1:]

                if ac_user[1] == "Admin":
                    user = Corporate_Login.objects.get(pk=user_id)
                    print("get user info from get_user")
                    print(user.id)
                elif ac_user[1] == "Approver_1":
                    user = Corporate_Approves_1_Login.objects.get(pk=user_id)
                elif ac_user[1] == "Approver_2":
                    user = Corporate_Approves_2_Login.objects.get(pk=user_id)
                elif ac_user[1] == "Spoc":
                    user = Corporate_Spoc_Login.objects.get(pk=user_id)
                elif ac_user[1] == "Employee":
                    user = Corporate_Employee_Login.objects.get(pk=user_id)
                elif ac_user[0] == "agents":
                    user = Corporate_Agent.objects.get(pk=user_id)
                elif ac_user[0] == "operator":
                    user = Operator_Login.objects.get(pk=user_id)
                else:
                    return None
            else:
                return None

            if user.is_active:
                return user
            return None
        except Corporate_Login.DoesNotExist:
            return None

