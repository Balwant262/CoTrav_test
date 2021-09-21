from django.http import JsonResponse
from Common.VIEW.Api.api_views import getUserinfoFromAccessToken, dictfetchall


def get_app_version_code(request):
    if 'USERTYPE' in request.headers:
        user_type = request.META['HTTP_USERTYPE']
        user = {}
        try:
            if user_type == '1':
                data = {'success': 1, 'message': 'Api Found Successfully', 'app_name': "AdminApp", 'versionName': '1.0', 'versionCode':'1'}
                return JsonResponse(data)
            elif user_type == '2':
                data = {'success': 1, 'message': 'Api Found Successfully', 'app_name': "SubgroupApproverApp", 'versionName': '1.0', 'versionCode':'1'}
                return JsonResponse(data)
            elif user_type == '3':
                data = {'success': 1, 'message': 'Api Found Successfully', 'app_name': "GroupApproverApp", 'versionName': '1.0', 'versionCode':'1'}
                return JsonResponse(data)
            elif user_type == '4':
                data = {'success': 1, 'message': 'Api Found Successfully', 'app_name': "SpocApp", 'versionName': '1.0', 'versionCode':'1'}
                return JsonResponse(data)
            elif user_type == '6':
                data = {'success': 1, 'message': 'Api Found Successfully', 'app_name': "EmployeeApp", 'versionName': '1.0', 'versionCode':'1'}
                return JsonResponse(data)
            elif user_type == '8':
                data = {'success': 1, 'message': 'Api Found Successfully', 'app_name': "DriverApp", 'versionName': '1.0', 'versionCode':'1'}
                return JsonResponse(data)
            elif user_type == '10':
                data = {'success': 1, 'message': 'Api Found Successfully', 'app_name': "AgentApp", 'versionName': '1.0', 'versionCode':'1'}
                return JsonResponse(data)
        except Exception as e:
            data = {'success': 0, 'error': getattr(e, 'message', str(e))}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)