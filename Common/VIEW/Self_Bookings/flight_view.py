import xml.etree.ElementTree as ET
import requests
import base64
import xmltodict

CREDENTIALS = 'Universal API/uAPI7648806979-241d6447:rT2xbTHrb4zy9sapAkmA43HHS'
CREDENTIALS_enc64 = base64.b64encode(bytes(CREDENTIALS, 'utf-8')).decode("ascii")
Provider = '1G'
RGETBRANCH = 'P7038885'

class Flight():
    def travelport_api_search_flights(self, data):
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
        root = ET.parse(response.content)
        return root