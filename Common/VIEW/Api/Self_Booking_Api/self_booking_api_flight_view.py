from Common.VIEW.Api.api_views import getUserinfoFromAccessToken, dictfetchall
from django.db import connection
from django.http import JsonResponse
from dateutil.parser import parse
import requests
import base64
import xmltodict


CREDENTIALS = 'Universal API/uAPI7648806979-241d6447:rT2xbTHrb4zy9sapAkmA43HHS'
CREDENTIALS_enc64 = base64.b64encode(bytes(CREDENTIALS, 'utf-8')).decode("ascii")
Provider = '1G'
RGETBRANCH = 'P7038885'


def travelport_api_search_flights(request):
    if 'AUTHORIZATION' in request.headers and 'USERTYPE' in request.headers:
        req_token = request.META['HTTP_AUTHORIZATION']
        user_type = request.META['HTTP_USERTYPE']
        try:
            trip_type = request.POST.get('trip_type', '')
            return_date = request.POST.get('return_date', '')
            fl_class = request.POST.get('fl_class', '')
            no_of_seats = request.POST.get('no_of_seats', '')
            from_city = request.POST.get('from_city', '')
            to_city = request.POST.get('to_city', '')
            departure_date = request.POST.get('departure_date', '')
            departure_date = parse(departure_date).strftime("%Y-%m-%d")
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
                        payload = """
                         <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <air:LowFareSearchReq TargetBranch="P7038885" TraceId="PP_1G_001322" SolutionResult="false" AuthorizedBy="SUSIL" xmlns:air="http://www.travelport.com/schema/air_v50_0" xmlns:com="http://www.travelport.com/schema/common_v50_0">
      <com:BillingPointOfSaleInfo OriginApplication="UAPI" />
      <air:SearchAirLeg>
        <air:SearchOrigin>
          <com:Airport Code="PNQ" />
        </air:SearchOrigin>
        <air:SearchDestination>
          <com:Airport Code="DEL" />
        </air:SearchDestination>
        <air:SearchDepTime PreferredTime="2020-07-28" />
      </air:SearchAirLeg>
      <air:AirSearchModifiers>
        <air:PreferredProviders>
          <com:Provider Code="1G" />
        </air:PreferredProviders>
      </air:AirSearchModifiers>
      <com:SearchPassenger Code="ADT" />
      <com:SearchPassenger Code="CNN" Age="3" />
    </air:LowFareSearchReq>
  </soap:Body>
</soap:Envelope>
                        """
                        header = {
                            "Content-Type": "text/xml:charset=utf-8",
                            "Accept": "gzip,deflate",
                            "Connection": "Keep-Alive",
                            "Authorization": "Basic %s" % CREDENTIALS_enc64,
                            "Content-Length": str(len(payload))
                        }

                        url = "https://apac.universal-api.pp.travelport.com/B2BGateway/connect/uAPI/AirService"
                        response = requests.post(url, data=payload, headers=header)
                        response = xmltodict.parse(response.content)
                        data = {'success': 1, 'Data': response}
                        return JsonResponse(data)
                    except Exception as e:
                        print(e)
                        data = {'success': 0, 'Data': e}
                        return JsonResponse(data)
                else:
                    data = {'success': 0, 'error': "User Information Not Found"}
                    return JsonResponse(data)
            else:
                data = {'success': 0, 'Corporates': "Token Not Found"}
                return JsonResponse(data)
        except Exception as e:
            print("EXCEPTION API")
            data = {'success': 0, 'Data': e}
            return JsonResponse(data)
    else:
        data = {'success': 0, 'error': "Missing Parameter Value Try Again..."}
        return JsonResponse(data)