#!/usr/bin/python
import xml.sax
from datetime import datetime

import dateutil.parser

class FlightHandler2( xml.sax.ContentHandler ):

    def __init__(self):
        self.CurrentData = ""
        self.FlightDetailsList = {}
        self.FlightDetails = {}
        self.ConnectedFlights = []
        self.AirSegment = {}
        self.segment_details = {}
        self.FlightDetailsRefKey = ""
        self.AirSegmentList = []
        self.AirPricingSolutionList = []
        self.BookingInfo = []
        self.segRef = []
        self.key = ""
        self.segkey = ""
        self.connection = 0
        self.AirPricingSolution = {}
        self.BookInfo = {}
        self.optar = []
        self.FlightOption = {}
        self.group1 = {}
        self.group2 = {}
        self.route = {}
        self.FlightOptionAr = []
        self.opt_count = 0
        self.LegRef = ""
        self.flag = ""
        self.flag_option = ""
        self.onwordAr = []
        self.returnAr = []
        self.onword_key = ""
        self.return_key = ""
        self.onword_flag = 0
        self.return_flag = 0
        self.BasePrice = ""
        self.carrier_code = ""

        self.finalDataSearch = {}

        self.Content = ""

        self.carrierAr = []

        self.error = 0

        self.error_content = ""

        self.error_data = {"error_flag": "1"}

    def startElement(self, tag, attributes):

        ############## error messaging ################
        if tag == "SOAP:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultcode":
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultstring":
            self.CurrentData = tag

        if tag == "SOAP-ENV:detail":
            self.CurrentData = tag

        if tag == "faultcode":
            self.CurrentData = tag

        if tag == "faultstring":
            self.CurrentData = tag

        if tag == "common_v50_0:Description":
            self.CurrentData = tag

        if tag == "air:ErrorMessage":
            self.CurrentData = tag

        ############## end ############################

        if tag == "air:FlightDetails":
            self.key = str(attributes['Key'])
            details = {
                "Key" : str(attributes['Key']),
                "Origin": attributes['Origin'],
                "Destination": attributes['Destination'],
                "DepartureTime": attributes['DepartureTime'],
                "ArrivalTime": attributes['ArrivalTime'],
                "FlightTime": attributes['FlightTime'],
                "TravelTime": attributes['TravelTime'],
                "Equipment": attributes['Equipment'] if "Equipment" in attributes else ""

            }

            self.FlightDetailsList[self.key] = details

        if tag == "air:Connection":
            self.connection = 1

        if tag == "air:Leg":
            grp = attributes['Group']
            key = str(attributes['Key'])
            if grp == "0":
                self.onword_flag = 1
                self.onword_key = key
                self.route["Onword"] = {
                    "Group": attributes['Group'],
                    "Origin": attributes['Origin'],
                    "Destination": attributes['Destination']
                }

            if grp == "1":
                self.return_flag = 1
                self.return_key = key
                self.route["Return"] = {
                    "Group": attributes['Group'],
                    "Origin": attributes['Origin'],
                    "Destination": attributes['Destination']
                }


        if tag == "air:AirSegment":
            self.segkey = str(attributes['Key'])
            #Departure = datetime.fromisoformat(str(attributes['DepartureTime']))
            #Arrival = datetime.fromisoformat(str(attributes['ArrivalTime']))
            Departure = dateutil.parser.isoparse(str(attributes['DepartureTime']))
            Arrival = dateutil.parser.isoparse(str(attributes['ArrivalTime']))
            self.segment_details = {
                'Key': str(attributes['Key']),
                'Group': attributes['Group'],
                'Carrier': attributes['Carrier'],
                'FlightNumber': attributes['FlightNumber'],
                'Origin': attributes['Origin'],
                'Destination': attributes['Destination'],
                'DepartureTime': Departure.strftime("%d/%m/%y %H:%M:%S"),
                'ArrivalTime': Arrival.strftime("%d/%m/%y %H:%M:%S"),
                'FlightTime': attributes['FlightTime'],
                'Distance': attributes['Distance'],
                'NumberOfStops' : attributes['NumberOfStops'] if 'NumberOfStops' in attributes else '0'

            }

            if "Carrier" in attributes:
                self.carrierAr.append(attributes['Carrier'])
                self.carrier_code = attributes['Carrier']


        if tag == "air:CodeshareInfo":
            self.CurrentData = tag
            self.segment_details['OperatingCarrier'] = attributes['OperatingCarrier']

        if tag == "air:FlightDetailsRef":
             self.FlightDetailsRefKey = str(attributes['Key'])

        if tag == "air:AirSegmentRef":
            self.AirSegmentRef = str(attributes['Key'])


        if tag == "air:AirPricingSolution":

            self.AirPricingSolution = {
                "Key": str(attributes['Key']),
                "TotalPrice": attributes['TotalPrice'],
                "BasePrice": attributes['BasePrice'],
                "ApproximateTotalPrice": attributes['ApproximateTotalPrice'],
                "ApproximateBasePrice": attributes['ApproximateBasePrice'],
                "EquivalentBasePrice": attributes['EquivalentBasePrice'],
                "Taxes": attributes['Taxes'],
                "ApproximateTaxes": attributes['ApproximateTaxes']
            }

        if tag == "air:AirPricePoint":
            self.BasePrice = attributes["BasePrice"].replace("INR", "")

        if tag == "air:FlightOptionsList":
            pass


        if tag == "air:FlightOption":
            self.LegRef = str(attributes["LegRef"])
            if self.LegRef == self.onword_key :
                self.flag = "Onword"
                self.flag_option = "Onword_Options"

            if self.LegRef == self.return_key :
                self.flag = "Return"
                self.flag_option = "Return_Options"

        if tag == "air:Option":
            self.option = {
                "Key" : attributes["Key"],
                "TravelTime" : attributes["TravelTime"]
            }

            #self.optionkey = attributes["Key"]
            #self.TravelTime = attributes["TravelTime"]

        if tag == "air:BookingInfo":
            segkey = str(attributes["SegmentRef"])
            self.BookInfo = {
                "BookingCode" : attributes["BookingCode"],
                "BookingCount" : attributes["BookingCount"],
                "CabinClass" : attributes["CabinClass"],
                "FareInfoRef" : attributes["FareInfoRef"],
                "SegmentRef" : self.AirSegment[segkey]
            }
            #self.BookInfo["BookingCode"] = attributes["BookingCode"]
            #self.BookInfo["BookingCount"] = attributes["BookingCount"]
            #self.BookInfo["CabinClass"] = attributes["CabinClass"]
            #self.BookInfo["FareInfoRef"] = str(attributes["FareInfoRef"])
            #self.BookInfo["SegmentRef"] = str(attributes["SegmentRef"])

            self.BookingInfo.append(self.BookInfo)


        if tag == "air:Journey":
            pass

        if tag == "air:AirSegmentRef":
            segRef = str(attributes['Key'])
            self.segRef.append(segRef)




    def endElement(self, tag):

        ############ eorror messaging ####################

        if tag == "SOAP-ENV:faultcode":
            pass

        if tag == "SOAP-ENV:faultstring":
            self.error_data['faultstring'] = self.Content

        if tag == "SOAP-ENV:detail":
            self.error_data['Description'] = self.Content


        if tag == "SOAP:Fault":
            pass

        if tag == "faultcode":
            self.error_data['faultcode'] = self.Content

        if tag == "faultstring":
            self.error_data['faultstring'] = self.Content


        if tag == "air:ErrorMessage":
            self.error_data['ErrorMessage'] = self.Content

        if tag == "common_v50_0:Description":
            self.error_data['Description'] = self.Content

        ############### end ################################


        if tag == "air:AirSegment":
            # self.AirSegment[self.segkey].append(self.segment_details)
            self.segment_details['FlightDetailsRef'] = self.FlightDetailsList[self.FlightDetailsRefKey]
            self.AirSegment[self.segkey] = self.segment_details

            #print(self.AirSegment)

            self.segment_details = {}

        if tag == "air:AirPricingSolution":
            self.AirPricingSolution['BookingInfo'] = self.BookingInfo
            self.AirPricingSolution['Connection'] =  self.connection
            airSol = self.AirPricingSolution
            self.AirPricingSolutionList.append(airSol)
            self.AirPricingSolution = {}
            self.connection = 0
            self.segAr = []
            self.BookingInfo = []


        if tag == "air:FlightOptionsList":
            self.optar = []


        if tag == "air:FlightOption":
            if self.flag == "Onword":
                for val in self.optar:
                    self.onwordAr.append(val)

            if self.flag == "Return":
                for val in self.optar:
                    self.returnAr.append(val)

            #self.route[self.flag].update(dictt)
            #self.route[self.LegRef]["options"].append(dictt)
            #self.opt_count = self.opt_count +1
            self.optar = []


        if tag == "air:Option":
            self.option["BookingInfo"] = self.BookingInfo
            self.option["connection"] = self.connection
            self.option["BasePrice"] = self.BasePrice
            self.option["Carrier_Code"] = self.carrier_code
            self.optar.append(self.option)
            self.option = {}
            self.optionkey = ""
            self.TravelTime = ""
            self.BookingInfo = []

            self.connection = 0


        if tag == "air: BookingInfo":
            pass


        if tag == "air:AirSegmentList":
            self.AirSegmentList.append(self.AirSegment)

        if tag == "air:CodeshareInfo":
            self.CurrentData = ""

        if tag == "air:Journey":
            self.segAr = []
            for ky in self.segRef:
                dt = self.AirSegment[ky]
                self.segAr.append(dt)

            self.AirPricingSolution['ConnectedSegRef'] = self.segAr
            self.segRef = []


        if tag == "air:AirPricePointList":

            if self.onword_flag == 1 :
                dictt = {

                    "Onword_Options": self.onwordAr

                }
                self.route["Onword"].update(dictt)

            if self.return_flag == 1 :
                dictt = {

                    "Return_Options": self.returnAr

                }
                self.route["Return"].update(dictt)



    def getFinalData(self):

        unique_carrier_list = []

        for x in self.carrierAr:
            # check if exists in unique_list or not
            if x not in unique_carrier_list:
                unique_carrier_list.append(x)


        self.finalData =  {
            "AirPricingSolutionList" : self.route,
            "FlightCarriers" : unique_carrier_list
        }

        print('Printing final dataaaaaa')
        print(self.finalData)

        print(self.error)

        print(self.error_data)

        if self.error == 0 :
            self.finalDataSearch =  self.finalData
        else:
            self.finalDataSearch = self.error_data

        return self.finalDataSearch


    def characters(self, content):

        if self.CurrentData == "faultcode":
            self.Content = content

        if self.CurrentData == "faultstring":
            self.Content = content

        if self.CurrentData == "common_v50_0:Description":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:faultstring":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:detail":
            self.Content = content

        if self.CurrentData == "air:ErrorMessage":
            self.Content = content


        if self.CurrentData == "air:CodeshareInfo":
            self.segment_details['FlightCarrier'] = content







class FlightDetailsHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.CurrentData = ""
        self.AirSegmentOnword = {}
        self.AirSegmentReturn = {}
        self.CodeshareInfo = {}
        self.AirSegmentAr = []
        self.finalData = {}
        self.BasePrice = ""
        self.Refundable = ""
        self.FlightType = ""
        self.Fare = {}
        self.FareInfo = []
        self.OnwordSegmentKey = ""
        self.ReturnSegmentKey = ""
        self.BookingInfo = {}
        self.BookingInfoAr = []

        self.error = 0

        self.error_content = ""

        self.error_data = {"error_flag": "1"}

        self.detail_seg = {}



    def startElement(self, tag, attributes):
        if tag == "air:AirItinerary":
            pass


        if tag == "SOAP:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:Fault":
            self.error = 1
            self.CurrentData = tag


        if tag == "SOAP-ENV:faultcode":
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultstring":
            self.CurrentData = tag

        if tag == "SOAP-ENV:detail":
            self.CurrentData = tag

        if tag == "faultcode":
            self.CurrentData = tag

        if tag == "faultstring":
            self.CurrentData = tag

        if tag == "common_v50_0:Description":
            self.CurrentData = tag

        if tag == "air:ErrorMessage":
            self.CurrentData = tag






        if tag == "air:AirSegment":
            Departure = dateutil.parser.isoparse(str(attributes["DepartureTime"]))
            Arrival = dateutil.parser.isoparse(str(attributes["ArrivalTime"]))

            group = attributes["Group"]

            #FlightTime = datetime.fromisoformat(str(attributes["FlightTime"]))
            #TravelTime = datetime.fromisoformat(str(attributes["TravelTime"]))
            if group == "0":
                self.FlightType = "0"
                self.OnwordSegmentKey = str(attributes["Key"])
                self.AirSegmentOnword = {

                "Key" : attributes["Key"],
                "Group" : attributes["Group"],
                "Carrier" : attributes["Carrier"],
                "FlightNumber" : attributes["FlightNumber"],
                "ProviderCode" : attributes["ProviderCode"],
                "Origin" : attributes["Origin"],
                "Destination" : attributes["Destination"],
                "DepartureTime" : Departure.strftime("%d-%m-%y %H:%M:%S"),
                "ArrivalTime" : Arrival.strftime("%d-%m-%y %H:%M:%S"),
                "FlightTime" : attributes["FlightTime"],
                "TravelTime" : attributes["TravelTime"],
                "Distance" : attributes["Distance"] if "Distance" in attributes else "",
                "ClassOfService" : attributes["ClassOfService"] if "ClassOfService" in  attributes else "",
                "Equipment" : attributes["Equipment"] if "Equipment" in attributes else "",
                "ChangeOfPlane" : attributes["ChangeOfPlane"] if "ChangeOfPlane" in attributes else "",
                "OptionalServicesIndicator" : attributes["OptionalServicesIndicator"] if "OptionalServicesIndicator" in attributes else "",
                "AvailabilitySource" : attributes["AvailabilitySource"] if "AvailabilitySource" in attributes else "",

                }

            if group == "1":
                self.FlightType = "1"
                self.ReturnSegmentKey = str(attributes["Key"])
                self.AirSegmentReturn = {
                    "Key": attributes["Key"],
                    "Group": attributes["Group"],
                    "Carrier": attributes["Carrier"],
                    "FlightNumber": attributes["FlightNumber"],
                    "ProviderCode": attributes["ProviderCode"],
                    "Origin": attributes["Origin"],
                    "Destination": attributes["Destination"],
                    "DepartureTime": Departure.strftime("%d-%m-%y %H:%M:%S"),
                    "ArrivalTime": Arrival.strftime("%d-%m-%y %H:%M:%S"),
                    "FlightTime": attributes["FlightTime"],
                    "TravelTime": attributes["TravelTime"],
                    "Distance": attributes["Distance"],
                    "ClassOfService": attributes["ClassOfService"],
                    "Equipment": attributes["Equipment"] if "Equipment" in attributes else "",
                    "ChangeOfPlane": attributes["ChangeOfPlane"],
                    "OptionalServicesIndicator": attributes["OptionalServicesIndicator"],
                    "AvailabilitySource": attributes["AvailabilitySource"],
                    "PolledAvailabilityOption": attributes["PolledAvailabilityOption"],
                    "AvailabilityDisplayType": attributes["AvailabilityDisplayType"],

                }

        if tag == "air:FareInfo":
            FareInfoKey = str(attributes["Key"])
            FareInfo = {
            "Key" : attributes["Key"],
            "FareBasis" : attributes["FareBasis"],
            "PassengerTypeCode" : attributes["PassengerTypeCode"],
            "Origin" : attributes["Origin"],
            "Destination" : attributes["Destination"],
            "EffectiveDate" : attributes["EffectiveDate"],
            "DepartureDate" : attributes["DepartureDate"],
            "Amount" : attributes["Amount"],
            "NegotiatedFare" : attributes["NegotiatedFare"],
            "NotValidBefore" : "",
            "NotValidAfter" : "",
            "TaxAmount" : attributes["TaxAmount"]
            }

            self.Fare[FareInfoKey] = FareInfo


        if tag == "air:BookingInfo":
            FareSeg = {}
            FareFlag = 0
            FareInfoRef = str(attributes["FareInfoRef"])

            SegmentRef = str(attributes["SegmentRef"])

            if self.OnwordSegmentKey == SegmentRef:
                FareSeg = self.AirSegmentOnword
                FareFlag = 0

            if self.ReturnSegmentKey == SegmentRef:
                FareSeg = self.AirSegmentReturn
                FareFlag = 1

            self.BookingInfo = {

                "BookingCode": attributes["BookingCode"],
                "CabinClass": attributes["CabinClass"],
                "FareInfo": self.Fare[FareInfoRef],
                "Segment": FareSeg,
                "HostTokenRef": attributes["HostTokenRef"],
                "FareFlag": FareFlag

            }



        if tag == "air:CodeshareInfo":
            self.CurrentData = tag
            self.CodeshareInfo['FlightCarrierCode'] = attributes["OperatingCarrier"]

        if tag == "air:FlightDetails":
            Departure = dateutil.parser.isoparse(str(attributes["DepartureTime"]))
            Arrival = dateutil.parser.isoparse(str(attributes["ArrivalTime"]))

            #FlightTime = datetime.fromisoformat(str(attributes["FlightTime"]))
            #TravelTime = datetime.fromisoformat(str(attributes["TravelTime"]))

            self.FlightDetails = {

            "Key" : attributes["Key"],
            "Origin" : attributes["Origin"],
            "Destination" : attributes["Destination"],
            "DepartureTime" : Departure.strftime("%d-%m-%y %H:%M:%S"),
            "ArrivalTime" : Arrival.strftime("%d-%m-%y %H:%M:%S"),
            "FlightTime" : attributes["FlightTime"],
            "TravelTime" : attributes["TravelTime"],
            "Distance" : attributes["Distance"],

            }

        if tag == "air:AirPricingInfo":
            self.BasePrice = attributes["BasePrice"] if "BasePrice" in attributes else "0"
            self.Refundable = attributes["Refundable"] if "Refundable" in attributes else ""
            #self.Refundable = ""


    def endElement(self, tag):

        if tag == "SOAP-ENV:faultcode":
            pass

        if tag == "SOAP-ENV:faultstring":
            self.error_data['faultstring'] = self.Content

        if tag == "SOAP-ENV:detail":
            self.error_data['Description'] = self.Content

        if tag == "SOAP:Fault":
            pass

        if tag == "faultcode":
            self.error_data['faultcode'] = self.Content

        if tag == "faultstring":
            self.error_data['faultstring'] = self.Content


        if tag == "air:ErrorMessage":
            self.error_data['ErrorMessage'] = self.Content

        if tag == "common_v50_0:Description":
            self.error_data['Description'] = self.Content



        if tag == "air:AirItinerary":
            pass

        if tag == "air:AirSegment":
            pass

        if tag == "air:CodeshareInfo":
            pass

        if tag == "air:FlightDetails":
            pass

        if tag == "air:AirPriceRsp":
            dicto = {
                "Onword": self.AirSegmentOnword,
                "Return": self.AirSegmentReturn,
                "CodeshareInfo": self.CodeshareInfo,
                "FlightDetails": self.FlightDetails,
                "BasePrice" : self.BasePrice,
                "Refundable" : self.Refundable,
                "FlightType" : self.FlightType,
                "BookingInf" : self.BookingInfoAr
            }

            self.AirSegmentAr.append(dicto)

        if tag == "air:FareInfo":
            self.FareInfo.append(self.Fare)

        if tag == "air:BookingInfo":
            self.BookingInfoAr.append(self.BookingInfo)
            self.BookingInfo = {}


    def characters(self, content):
        if self.CurrentData == "air:CodeshareInfo":
            if self.FlightType == "0":
                self.CodeshareInfo['FlightCarrierOnword'] = str(content)

            if self.FlightType == "1":
                self.CodeshareInfo['FlightCarrierReturn'] = str(content)


        if self.CurrentData == "faultcode":
            self.Content = content

        if self.CurrentData == "faultstring":
            self.Content = content

        if self.CurrentData == "common_v50_0:Description":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:faultstring":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:detail":
            self.Content = content

        if self.CurrentData == "air:ErrorMessage":
            self.Content = content




    def getFinalData(self):
        self.detail_seg = {
            "Details": self.AirSegmentAr

        }
        print('Printing final details............ dataaaaaa')
        print(self.detail_seg)

        if self.error == 0 :
            self.finalData =  self.detail_seg
        else:
            self.finalData = self.error_data

        return self.finalData






class FlightBookingHandler ( xml.sax.ContentHandler ):

    def __init__(self):
        self.CurrentData = ""
        self.ResponseMessage = {}
        self.ResponseMessageAr = []
        self.BookingTraveler = {}
        self.BookingTravelerAr = []
        self.ProviderReservationInfoRef = ""
        self.Address = {}
        self.HotelReservation = {}
        self.HotelProperty = {}
        self.ReservationName = {}
        self.PropertyAddress = ""
        self.HotelPhoneNumber = []
        self.RoomRateDescriptionText = ""
        self.HotelRateByDateAr = []
        self.GuaranteeType = ""
        self.HotelStay = {}
        self.HotelStayAr = []
        self.Guarantee = {}
        self.SellMessage = {}
        self.AgencyInfo = {}
        self.AgentActionAr = []
        self.BookingData = { "error_flag" : "0" }

        self.DeliveryInfo = {}
        self.AirSegment = {}
        self.AirSegmentAr = []
        self.flightdetails = {}
        self.flightdetailsAr = []

        self.LocatorCode = ""

        self.AirPricingInfo = {}

        self.error = 0

        self.error_content = ""

        self.error_data = { "error_flag" : "1" }

    def startElement(self, tag, attributes):

        if tag == "SOAP:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:Fault":
            self.error = 1
            self.CurrentData = tag


        if tag == "SOAP-ENV:faultcode":
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultstring":
            self.CurrentData = tag

        if tag == "SOAP-ENV:detail":
            self.CurrentData = tag

        if tag == "faultcode":
            self.CurrentData = tag

        if tag == "faultstring":
            self.CurrentData = tag

        if tag == "common_v50_0:Description":
            self.CurrentData = tag

        if tag == "air:ErrorMessage":
            self.CurrentData = tag




        if tag == "common_v50_0:ResponseMessage":
            self.ResponseMessage = {
            "Code" : attributes["Code"],
            "ProviderCode" : attributes["ProviderCode"],
            "Type" : attributes["Type"],
            }
            self.CurrentData = tag


        if tag == "universal:UniversalRecord":
            if "LocatorCode" in attributes:
                self.LocatorCode = attributes["LocatorCode"]
            else:
                pass

        if tag == "common_v50_0:BookingTraveler":
            self.BookingTraveler = {
            "ElStat" : attributes["ElStat"],
            "Gender" : "M",
            "Key" : attributes["Key"],
            "TravelerType" : attributes["TravelerType"],
             "Age" : "50"
            }

        if tag == "common_v50_0:BookingTravelerName":
            BookingTravelerName = {
            "First" : attributes["First"],
            "Last" : attributes["Last"],
            "Prefix" : attributes["Prefix"]
            }

            self.BookingTraveler["BookingTravelerName"] = BookingTravelerName
            #self.BookingTraveler.update(BookingTravelerName)

        if tag == "common_v50_0:DeliveryInfo":
            pass

        if tag == "common_v50_0:PhoneNumber":
            PhoneNumber = {
            "AreaCode" : "08",
            "CountryCode" : "61",
            "ElStat" : "A",
            "Key" : "4Vc037UXRzClNfG5ViYIXg==",
            "Location" : "PER",
            "Number" : "40003000",
            "Type" : "Home"
            }

            self.BookingTraveler.update({ "PhoneNumber" : PhoneNumber })

        if tag == "common_v50_0:ProviderReservationInfoRef":
            self.ProviderReservationInfoRef = attributes["Key"]

        if tag == "common_v50_0:Email":
            Email = {
            "ElStat" : attributes["ElStat"],
            "EmailID" : attributes["EmailID"],
            "Key" : attributes["Key"],
            "Type" : attributes["Type"]
            }

            self.BookingTraveler.update({"Email": Email})

        if tag == "common_v50_0:Address":
            self.Address = {
            "ElStat" : "A",
            "Key" : "n91VIL8gSm22rNKwLSHKpQ=="
            }

        if tag == "common_v50_0:AddressName":
            self.CurrentData = tag

        if tag == "common_v50_0:Street":
            self.CurrentData = tag

        if tag == "common_v50_0:City":
            self.CurrentData = tag

        if tag == "common_v50_0:State":
            self.CurrentData = tag

        if tag == "common_v50_0:PostalCode":
            self.CurrentData = tag

        if tag == "common_v50_0:Country":
            self.CurrentData = tag


        if tag == "air:AirReservation":
            self.AirReservation = {
            "CreateDate" : attributes["CreateDate"],
            "LocatorCode" : attributes["LocatorCode"],
            "ModifiedDate" : attributes["ModifiedDate"]
            }

        if tag == "common_v50_0:SupplierLocator":
            SupplierLocator = {
                "CreateDateTime" : attributes["CreateDateTime"],
                "ProviderReservationInfoRef" : attributes["ProviderReservationInfoRef"],
                "SupplierCode" : attributes["SupplierCode"],
                "SupplierLocatorCode" : attributes["SupplierLocatorCode"]
            }
            self.AirReservation.update({"SupplierLocator" : SupplierLocator })

        if tag == "air:AirSegment" and self.error == 0:
            self.AirSegment = {
            "ArrivalTime" : attributes["ArrivalTime"],
            "CabinClass" : "CabinClass",
            "Carrier" : attributes["Carrier"],
            "ChangeOfPlane" : "ChangeOfPlane",
            "ClassOfService" : attributes["ClassOfService"],
            "DepartureTime" : attributes["DepartureTime"],
            "Destination" : attributes["Destination"],
            "Distance" : "Distance",
            "ETicketability" : "ETicketability",
            "ElStat" : "ElStat",
            "Equipment" : attributes["Equipment"] if "Equipment" in attributes else "",
            "FlightNumber" : attributes["FlightNumber"],
            "Group" : attributes["Group"],
            "GuaranteedPaymentCarrier" : "GuaranteedPaymentCarrier",
            "Key" : attributes["Key"],
            "OptionalServicesIndicator" : attributes["OptionalServicesIndicator"],
            "Origin" : attributes["Origin"],
            "ProviderCode" : attributes["ProviderCode"],
            "ProviderReservationInfoRef" : "ProviderReservationInfoRef",
            "Status" : attributes["Status"],
            "TravelOrder" : "TravelOrder",
            "TravelTime" : attributes["TravelTime"]
            }


        if tag == "air:FlightDetails":

            self.flightdetails = {
            "ArrivalTime" : attributes["ArrivalTime"] if "ArrivalTime" in attributes else "",
            "DepartureTime" : attributes["DepartureTime"] if "DepartureTime" in attributes else "" ,
            "Destination" : attributes["Destination"] if "Destination" in attributes else "" ,
            "DestinationTerminal" : attributes["DestinationTerminal"] if "DestinationTerminal" in attributes else "" ,
            "ElStat" : attributes["ElStat"] if "ElStat" in attributes else "" ,
            "Equipment" : attributes["Equipment"] if "Equipment" in attributes else "" ,
            "FlightTime" : attributes["FlightTime"] if "FlightTime" in attributes else "" ,
            "Key" : attributes["Key"] if "Key" in attributes else "" ,
            "Origin" : attributes["Origin"] if "Origin" in attributes else "" ,
            "OriginTerminal" : attributes["OriginTerminal"] if "OriginTerminal" in attributes else "" ,
            "TravelTime" : attributes["TravelTime"] if "TravelTime" in attributes else ""
            }


        if tag == "air:AirPricingInfo":

            self.AirPricingInfo = {
            "AirPricingInfoGroup" : attributes["AirPricingInfoGroup"],
            "ApproximateBasePrice" : attributes["ApproximateBasePrice"],
            "ApproximateTotalPrice" : attributes["ApproximateTotalPrice"],
            "BasePrice" : attributes["BasePrice"],
            "ETicketability" : attributes["ETicketability"],
            "ElStat" : "ElStat",
            "EquivalentBasePrice" : "EquivalentBasePrice",
            "Exchangeable" : "Exchangeable",
            "IncludesVAT" : attributes["IncludesVAT"],
            "Key" : attributes["Key"],
            "LatestTicketingTime" : attributes["LatestTicketingTime"],
            "PlatingCarrier" : attributes["PlatingCarrier"],
            "PricingMethod" : attributes["PricingMethod"],
            "PricingType" : attributes["PricingType"],
            "ProviderCode" : attributes["ProviderCode"],
            "ProviderReservationInfoRef" : "ProviderReservationInfoRef",
            "Taxes" : attributes["Taxes"],
            "TotalPrice" : attributes["TotalPrice"],
            "TrueLastDateToTicket" : "TrueLastDateToTicket"
            }


            if tag == "SellMessage":
                self.CurrentData = tag


        if tag == "common_v50_0:FormOfPayment":
            pass

        if tag == "common_v50_0:CreditCard":
            self.CreditCard = {
            "ExpDate" : attributes["ExpDate"],
            "Name" : attributes["Name"],
            "Number" : attributes["Number"],
            "Type" : attributes["Type"]
            }

        if tag == "common_v50_0:BillingAddress":
            self.BillingAddress = {
            "ElStat" : "A",
            "Key" : "heqATi9qSYm/y1GLGs/QVw=="
            }


        if tag == "common_v50_0:ReservationName":
            self.ReservationName = {}

        if tag == "common_v50_0:NameOverride":
            self.ReservationName["First"] = attributes["First"]
            self.ReservationName["Last"] = attributes["Last"]

        if tag == "hotel:HotelProperty":
            self.HotelProperty = {
            "HotelChain" : attributes["HotelChain"],
            "HotelCode" : attributes["HotelCode"],
            "HotelLocation" : attributes["HotelLocation"],
            "Name" : attributes["Name"],
            "ParticipationLevel" : attributes["ParticipationLevel"]
            }

        if tag == "hotel:Address":
            self.PropertyAddress = tag

        if tag == "common_v50_0:PhoneNumber":
            PhoneNumber = {
            "Number" : "1-303-371-0888",
            "Type" : "Hotel"
            }
            self.HotelPhoneNumber.append(PhoneNumber)

        if tag == "hotel:HotelRateDetail":
            self.HotelRateDetail = {
            "Base" : attributes["Base"],
            "RateGuaranteed" : attributes["RateGuaranteed"],
            "RatePlanType" : attributes["RatePlanType"],
            "Total" : attributes["Total"]
            }

        if tag == "hotel:RoomRateDescription":
            self.Name = attributes["Name"]


        if tag == "hotel:Text":
            self.CurrentData = tag

        if tag == "hotel:HotelRateByDate":
            HotelRateByDate = {
            "Base" : "USD99.00",
            "EffectiveDate" : "2014-12-05",
            "ExpireDate" : "2014-12-08"
            }

            self.HotelRateByDateAr.append(HotelRateByDate)

        if tag == "hotel: GuaranteeInfo":
            self.GuaranteeType = attributes["GuaranteeType"]


        if tag == "hotel:HotelStay":
            self.HotelStay = {}

        if tag == "hotel:CheckinDate":
            self.CurrentData = tag

        if tag == "hotel:CheckoutDate":
            self.CurrentData = tag


        if tag == "common_v50_0:Guarantee":
            self.Guarantee = {
            "ElStat" : "A",
            "Key" : "39uAKjkbQveitaPPPeVeOg==",
            "Reusable" : "true",
            "Type" : "Guarantee"
            }

        if tag == "common_v50_0:CreditCard":
            CreditCard = {
            "ExpDate" : attributes["ExpDate"],
            "Number" : attributes["Number"],
            "Type" : attributes["Type"]
            }

            self.Guarantee["CreditCard"] = CreditCard

        if tag == "common_v50_0:BookingSource":
            self.BookingSource = {
            "Code" : "99999992",
            "Type" : "IataNumber"
            }

        if tag == "hotel:GuestInformation":
            self.GuestInformation = {
                "NumberOfRooms" : attributes["NumberOfRooms"]
            }

        if tag == "hotel:NumberOfAdults":
            self.CurrentData = tag

        if tag == "common_v50_0:SellMessage":
            self.CurrentData = tag


        if tag == "common_v50_0:AgencyInfo":
            self.AgencyInfo = {}

        if tag == "common_v50_0:AgentAction":
            AgentAction = {
            "ActionType" : attributes["ActionType"],
            "AgencyCode" : attributes["AgencyCode"],
            "AgentCode" : attributes["AgentCode"],
            "BranchCode" : attributes["BranchCode"],
            "EventTime" : attributes["EventTime"]
            }

            self.AgentActionAr.append(AgentAction)


    def endElement(self, tag):

        if tag == "SOAP-ENV:faultcode":
            pass

        if tag == "SOAP-ENV:faultstring":
            self.error_data['faultstring'] = self.Content

        if tag == "SOAP-ENV:detail":
            self.error_data['Description'] = self.Content


        if tag == "SOAP:Fault":
            pass

        if tag == "faultcode":
            self.error_data['faultcode'] = self.Content

        if tag == "faultstring":
            self.error_data['faultstring'] = self.Content


        if tag == "air:ErrorMessage":
            self.error_data['ErrorMessage'] = self.Content



        if tag == "common_v50_0:Description":
            self.error_data['Description'] = self.Content

        if tag == "common_v50_0:ResponseMessage":
            self.ResponseMessageAr.append(self.ResponseMessage)
            self.CurrentData = ""
            self.ResponseMessage = {}

        if tag == "universal:UniversalRecord":
            pass

        if tag == "common_v50_0:BookingTraveler":
            pass

        if tag == "common_v50_0:AddressName":
            self.Address["AddressName"] = self.Content

        if tag == "common_v50_0:Street":
            self.Address["Street"] = self.Content

        if tag == "common_v50_0:City":
            self.Address["City"] = self.Content

        if tag == "common_v50_0:State":
            self.Address["State"] = self.Content

        if tag == "common_v50_0:PostalCode":
            self.Address["PostalCode"] = self.Content

        if tag == "common_v50_0:Country":
            self.Address["Country"] = self.Content

        if tag == "common_v50_0:Address":
            self.BookingTraveler.update({"Address" : self.Address })

        if tag == "common_v50_0:DeliveryInfo":
            self.DeliveryInfo.update({"Address" : self.Address })

        if tag == "air:FlightDetails":
            self.flightdetailsAr.append(self.flightdetails)
            self.flightdetails = {}


        if tag == "air:AirSegment":
            self.AirSegment.update({ "FlightDetails" : self.flightdetailsAr , "SellMessage" :  self.SellMessage })

            self.AirSegmentAr.append(self.AirSegment)
            self.AirSegment = {}
            self.SellMessage = {}

        if tag == "air:AirReservation":
            self.AirReservation.update({ "AirSegments" : self.AirSegmentAr })

        if tag == "air:AirPricingInfo":
            pass

        if tag == "air:FareInfo":
            pass

        if tag == "common_v50_0:FormOfPayment":
            pass

        if tag == "air:TicketingModifiers":
            pass

        if tag == "common_v50_0:AgencyInfo":
            pass

        if tag == "common_v50_0:AgentAction":
            pass

        if tag == "SellMessage":
            pass
            #self.SellMessage.append({"SellMsg" : self.Content })

        if tag == "common_v50_0:CreditCard":
            self.CreditCard.update({ "BillingAddress" : self.BillingAddress })

        if tag == "common_v50_0:BillingAddress":
            self.BillingAddress.update({"Address" : self.Address })
            self.Address = {}

        if tag == "common_v50_0:BookingTraveler":
            self.BookingTraveler.update({ "DeliveryInfo" : self.DeliveryInfo })
            self.BookingTravelerAr.append(self.BookingTraveler)

        if tag == "common_v50_0:ReservationName":
            self.HotelReservation.update({"ReservationName" : self.ReservationName})

        if tag == "hotel:Address":
            self.PropertyAddress = self.Content + " "

        if tag == "hotel:PropertyAddress":
            self.HotelProperty["Address"] = self.PropertyAddress

        if tag == "hotel:HotelProperty":
            self.HotelProperty["Number"] = self.HotelPhoneNumber

        if tag == "hotel:Text":
            self.RoomRateDescriptionText = self.Content + " "

        if tag == "hotel:RoomRateDescription":
            self.HotelRateDetail[self.Name] = self.RoomRateDescriptionText


        if tag == "hotel:HotelRateDetail":
            self.HotelRateDetail["HotelRateByDate"] = self.HotelRateByDateAr
            self.HotelRateDetail["GuaranteeType"] = self.GuaranteeType


        if tag == "hotel:CheckinDate":
            CheckinDate = self.Content
            self.HotelStay["CheckinDate"] = CheckinDate

        if tag == "hotel:CheckoutDate":
            CheckoutDate = self.Content
            self.HotelStay["CheckoutDate"] = CheckoutDate

        if tag == "hotel:HotelStay":
            self.HotelStayAr.append(self.HotelStay)

        if tag == "common_v50_0:SellMessage":
            pass
            #self.SellMessage = self.SellMessage + " " + self.Content
            #self.SellMessage.append({"SellMsg": self.Content})


        if tag == "hotel:HotelReservation":
            self.HotelReservation.update({"HotelProperty": self.HotelProperty})
            self.HotelReservation.update({"HotelRateDetail": self.HotelRateDetail})
            self.HotelReservation.update({"HotelStay": self.HotelStayAr})
            self.HotelReservation.update({"Guarantee": self.Guarantee})
            self.HotelReservation.update({"BookingSource": self.BookingSource})
            self.HotelReservation.update({"GuestInformation": self.GuestInformation})
            self.HotelReservation.update({"SellMessage": self.SellMessage})


        if tag == "common_v50_0:AgencyInfo":
            self.AgencyInfo = { "AgentAction" : self.AgentActionAr }

        if tag == "universal:UniversalRecord":
            self.BookingData = {
                "ResponseMessage": self.ResponseMessageAr,
                "BookingTraveler": self.BookingTravelerAr,
                "HotelReservation": self.HotelReservation,
                "AgencyInfo": self.AgencyInfo
            }



    def characters(self, content):
        if self.CurrentData == "common_v50_0:ResponseMessage":
            self.ResponseMessage["message"] = content

        if self.CurrentData == "common_v50_0:AddressName":
            self.Content = content

        if self.CurrentData == "common_v50_0:Street":
            self.Content = content

        if self.CurrentData == "common_v50_0:City":
            self.Content = content

        if self.CurrentData == "common_v50_0:State":
            self.Content = content

        if self.CurrentData == "common_v50_0:PostalCode":
            self.Content = content

        if self.CurrentData == "common_v50_0:Country":
            self.Content = content

        if self.CurrentData == "hotel:Address":
            self.Content = content

        if self.CurrentData == "hotel:Text":
            self.Content = content

        if self.CurrentData == "hotel:CheckinDate":
            self.Content = content

        if self.CurrentData == "hotel:CheckoutDate":
            self.Content = content

        if self.CurrentData == "common_v50_0:SellMessage":
            self.Content = content

        if self.CurrentData == "hotel: NumberOfAdults":
            self.GuestInformation["NumberOfAdults"] = content

        if self.CurrentData == "SellMessage":
            self.Content = content


       # error handling

        if self.CurrentData == "faultcode":
            self.Content = content

        if self.CurrentData == "faultstring":
            self.Content = content

        if self.CurrentData == "common_v50_0:Description":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:faultstring":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:detail":
            self.Content = content

        if self.CurrentData == "air:ErrorMessage":
            self.Content = content






    def getFinalData(self):

        if self.LocatorCode == "":
            pass
        else:
            self.BookingData["LocatorCode"] = self.LocatorCode

        if self.error == 0 :
            self.finalData =  self.BookingData
        else:
            self.finalData = self.error_data

        return self.finalData





class FlightTicketRespHandler ( xml.sax.ContentHandler ):

    def __init__(self):
        self.CurrentData = ""
        self.ResponseMessage = {}
        self.ResponseMessageAr = []
        self.etr = {}
        self.AirReservationLocatorCode = ""
        self.AgencyInfo = []
        self.AgentAction = {}
        self.BookingTraveler = {}
        self.DeliveryInfo = {}
        self.BookingData = {}
        self.ShippingAddress = []
        self.ssr = []
        self.BillingAddress = {}

        self.BaggageAllowanceInfo = {}

        self.url = []
        self.Text = []

        self.BagDetails = {}

        self.BaggageRestriction = []


    def startElement(self, tag, attributes):
        if tag == "common_v29_0:ResponseMessage":
            self.ResponseMessage = {
                "Code": attributes["Code"],
                "ProviderCode": attributes["ProviderCode"],
                "Type": attributes["Type"],
            }

            self.CurrentData = tag


        if tag == "air:ETR":
            self.etr = {
            "BasePrice" : attributes["BasePrice"],
            "ElStat" : attributes["ElStat"],
            "EquivalentBasePrice" : attributes["EquivalentBasePrice"],
            "Exchangeable" : attributes["Exchangeable"],
            "IATANumber" : attributes["IATANumber"],
            "IssuedDate" : attributes["IssuedDate"],
            "Key" : attributes["Key"],
            "PlatingCarrier" : attributes["PlatingCarrier"],
            "ProviderCode" : attributes["ProviderCode"],
            "ProviderLocatorCode" : attributes["ProviderLocatorCode"],
            "PseudoCityCode" : attributes["PseudoCityCode"],
            "Refundable" : attributes["Refundable"],
            "Taxes" : attributes["Taxes"]
            }


        if tag == "air:AirReservationLocatorCode":
            self.CurrentData = tag


        if tag == "common_v29_0:AgencyInfo":
            pass


        if tag == "common_v29_0:AgentAction":
            self.AgentAction = {
            "ActionType" : attributes["ActionType"],
            "AgencyCode" : attributes["AgencyCode"],
            "AgentCode" : attributes["AgentCode"],
            "BranchCode" : attributes["BranchCode"],
            "EventTime" : attributes["EventTime"]
            }
            self.AgencyInfo.append(self.AgentAction)
            self.AgentAction = {}


        if tag == "common_v29_0:BookingTraveler":
            self.BookingTraveler = {
            "DOB" : "1969-09-17",
            "Gender" : "M",
            "Key" : "gr8AVWGCR064r57Jt0+8bA==",
            "TravelerType" : "ADT"
            }


        if tag == "common_v29_0:BookingTravelerName":
            self.BookingTravelerName = {
                "First" : attributes["First"],
                "Last" : attributes["Last"],
                "Prefix" : attributes["Prefix"]
            }


        if tag == "common_v29_0:DeliveryInfo":
            pass

        if tag == "common_v29_0:ShippingAddress":
            self.ShippingAddressKey = attributes["Key"]

        if tag == "common_v29_0:AddressName":
            self.CurrentData = tag

        if tag == "common_v29_0:Street":
            self.CurrentData = tag

        if tag == "common_v29_0:City":
            self.CurrentData = tag

        if tag == "common_v29_0:State":
            self.CurrentData = tag

        if tag == "common_v29_0:PostalCode":
            self.CurrentData = tag

        if tag == "common_v29_0:Country":
            self.CurrentData = tag


        if tag == "common_v29_0:ProviderReservationInfoRef":
            pass

        if tag == "common_v29_0:PhoneNumber":
            PhoneNumber = {
                "AreaCode": "08",
                "CountryCode": "61",
                "ElStat": "A",
                "Key": "4Vc037UXRzClNfG5ViYIXg==",
                "Location": "PER",
                "Number": "40003000",
                "Type": "Home"
            }

            self.BookingTraveler.update({"PhoneNumber": PhoneNumber})

        if tag == "common_v29_0:ProviderReservationInfoRef":
            self.ProviderReservationInfoRef = attributes["Key"]

        if tag == "common_v29_0:Email":

            Email = {
                "EmailID": attributes["EmailID"],
                "Key": attributes["Key"],
                "Type": attributes["Type"]
            }

            self.BookingTraveler.update({"Email": Email})

        if tag == "common_v29_0:Address":
            self.Address = {
                "ElStat": "A",
                "Key": "n91VIL8gSm22rNKwLSHKpQ=="
            }


        if tag == "common_v29_0:SSR":
            ssr = {
            "Carrier" : attributes["Carrier"],
            "FreeText" : attributes["FreeText"],
            "Key" : attributes["Key"],
            "ProviderReservationInfoRef" : attributes["ProviderReservationInfoRef"],
            "Status" : attributes["Status"],
            "Type" : attributes["Type"]
            }
            self.ssr.append(ssr)


        if tag == "common_v29_0:FormOfPayment":
            self.FormOfPayment = {
            "Key" : "jwt2mcK1Qp27I2xfpcCtAw==",
            "ProfileKey" : "c3KaNgKlQSiX96c+ZAzHSA==",
            "Reusable" : "true",
            "Type" : "Credit"
            }


        if tag == "common_v29_0:CreditCard":
            self.CreditCard = {
            "ExpDate" : "2017-05",
            "Name" : "Jack Smith",
            "Number" : "4123456789001111",
            "Type" : "VI"
            }

        if tag == "common_v29_0:BillingAddress":
            self.BillingAddressKey = attributes["Key"]


        if tag == "common_v29_0:Payment":
            payment = {
            "Amount" : "GBP186.20",
            "FormOfPaymentRef" : "jwt2mcK1Qp27I2xfpcCtAw==",
            "Key" : "yf9y94e1Sia/3oKU/DOddw==",
            "Type" : "Itinerary"
            }


        if tag == "common_v29_0:SupplierLocator":
            SupplierLocator = {
            "SupplierCode" : "QF",
            "SupplierLocatorCode" : "3GA7XM"
            }


        if tag == "air:FareCalc":
            self.CurrentData = tag


        if tag == "air:Ticket":
            self.Ticket = {
            "ElStat" : "A",
            "Key" : "RGLlwNEtT0aG+IeDcMWzNg==",
            "TicketNumber" : "0819902192239",
            "TicketStatus" : "N"
            }


        if tag == "air:Coupon":
            self.coupon = {
            "BookingClass" : "L",
            "CouponNumber" : "1",
            "DepartureTime" : "2014-11-30T06:00:00.000+11:00",
            "Destination" : "MEL",
            "ElStat" : "A",
            "FareBasis" : "LFLEX",
            "Key" : "pIfegR6jSpyurN7duo75fA==",
            "MarketingCarrier" : "QF",
            "MarketingFlightNumber" : "401",
            "MarriageGroup" : "0",
            "Origin" : "SYD",
            "SegmentGroup" : "0",
            "Status" : "O",
            "StopoverCode" : "true"
            }


        if tag == "air:TicketEndorsement":
            self.TicketEndorsement = attributes["Value"]


        if tag == "common_v29_0:Endorsement":
            self.Endorsement = attributes["Value"]


        if tag == "air:BaggageAllowance":
            pass


        if tag == "air:BookingInfo":

            self.BookingInfo = {
            "BookingCode" : "L",
            "CabinClass" : "Economy",
            "FareInfoRef" : "8C8wntyaQaqL3vkOSo5o1w=="
            }


        if tag == "air:TaxInfo":

            TaxInfo = {
            "Amount" : "GBP4.20",
            "Category" : "QR",
            "Key" : "fCsdYYt8Tk2x58TPRJm5NQ=="
            }

            self.TaxInfo.apppend(TaxInfo)


        if tag == "air:FareCalc":
            self.CurrentData = tag


        if tag == "air:PassengerType":
            PassengerType = {
            "BookingTravelerRef" : "gr8AVWGCR064r57Jt0+8bA==",
            "Code" : "ADT",
            }


        if tag == "air:FareGuaranteeInfo":
            self.GuaranteeType = attributes["GuaranteeType"]


        if tag == "common_v29_0:BookingTravelerRef":
            self.BookingTravelerRefKey = attributes["Key"]


        if tag == "air:ChangePenalty":
            pass


        if tag == "air:Amount":
            self.CurrentData = tag


        if tag == "air:AirPricingInfo":
            self.AirPricingInfo = {
            "AirPricingInfoGroup" : "1",
            "ApproximateBasePrice" : "GBP179.00",
            "ApproximateTotalPrice" : "GBP186.20",
            "BasePrice" : "AUD331.16",
            "ETicketability" : "Yes",
            "EquivalentBasePrice" : "GBP179.00",
            "Exchangeable" : "true",
            "Key" : "6jeI5IdBSo+cstIHWS36Bw==",
            "LatestTicketingTime" : "2014-11-30T23:59:00.000+00:00",
            "PlatingCarrier" : "QF",
            "PricingMethod" : "Guaranteed",
            "PricingType" : "StoredFare",
            "ProviderReservationInfoRef" : "M0RkM31eQ3+0m65rx3oM/Q==",
            "Taxes" : "GBP7.20",
            "Ticketed" : "true",
            "TotalPrice" : "GBP186.20",
            "TrueLastDateToTicket" : "2014-11-30T23:59:00.000+00:00"
            }


        if tag == "air:FareInfo":
            self.FareInfo = {
            "Amount" : "AUD331.16",
            "Destination" : "MEL",
            "EffectiveDate" : "2014-11-10T00:00:00.000+00:00",
            "FareBasis" : "LFLEX",
            "Key" : "8C8wntyaQaqL3vkOSo5o1w==",
            "Origin" : "SYD",
            "PassengerTypeCode" : "ADT"
            }


        if tag == "air:BaggageAllowances":
            pass

        if tag == "air:BaggageAllowanceInfo":
            self.BaggageAllowanceInfo = {
            "Carrier" : attributes["Carrier"],
            "Destination" : attributes["Destination"],
            "Origin" : attributes["Origin"],
            "TravelerType" : attributes["TravelerType"]
            }

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            self.CurrentData = tag

        if tag == "air:TextInfo":
            pass

        if tag == "air:Text":
            self.CurrentData = tag

        if tag == "air:BagDetails":
            self.BagDetails = {
            "ApplicableBags" : attributes["ApplicableBags"],
            "ApproximateBasePrice" : attributes["ApproximateBasePrice"],
            "ApproximateTotalPrice" : attributes["ApproximateTotalPrice"],
            "BasePrice" : attributes["BasePrice"],
            "TotalPrice" : attributes["TotalPrice"]
            }

        if tag == "air:BaggageRestriction":
            pass

        if tag == "air:CarryOnAllowanceInfo":
            pass

        if tag == "air:EmbargoInfo":
            pass

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            pass



    def endElement(self, tag):
        if tag == "common_v29_0:ResponseMessage":
            self.ResponseMessageAr.append(self.ResponseMessage)
            self.CurrentData = ""
            self.ResponseMessage = {}

        if tag == "air:ETR":
            pass

        if tag == "common_v29_0:AgencyInfo":
            pass

        if tag == "common_v29_0:AddressName":
            self.Address["AddressName"] = self.Content

        if tag == "common_v29_0:Street":
            self.Address["Street"] = self.Content

        if tag == "common_v29_0:City":
            self.Address["City"] = self.Content

        if tag == "common_v29_0:State":
            self.Address["State"] = self.Content

        if tag == "common_v29_0:PostalCode":
            self.Address["PostalCode"] = self.Content

        if tag == "common_v29_0:Country":
            self.Address["Country"] = self.Content

        if tag == "common_v29_0:ShippingAddress":
            self.ShippingAddress.append(self.Address)

        if tag == "common_v29_0:FormOfPayment":
           self.FormOfPayment["CreditCard"] = self.CreditCard

        if tag == "common_v29_0:CreditCard":
            self.CreditCard["BillingAddress"] = self.BillingAddress

        if tag == "common_v29_0:BillingAddress":
            self.BillingAddress["Address"] = self.Address

        if tag == "air:FareCalc":
            self.FareCalc = self.Content

        if tag == "air:Ticket":
            self.Ticket["Coupon"] = self.coupon
            self.Ticket["TicketEndorsement"] = self.TicketEndorsement


        if tag == "air:AirPricingInfo":

            pass


        if tag == "air:FareInfo":

            pass


        if tag == "air:FareCalc":
            self.FareCalc = self.Content


        if tag == "air:ChangePenalty":
            self.ChangePenalty = self.Amount


        if tag == "air:CancelPenalty":
            self.CancelPenalty = self.Amount


        if tag == "air:Amount":
            self.Amount = self.Content


        if tag == "air:AirPricingInfo":
            self.AirPricingInfo["FareInfo"] = self.FareInfo
            self.AirPricingInfo["BookingInfo"] = self.BookingInfo
            self.AirPricingInfo["TaxInfo"] = self.TaxInfo
            self.AirPricingInfo["FareCalc"] = self.FareCalc
            self.AirPricingInfo["ChangePenalty"] = self.ChangePenalty
            self.AirPricingInfo["CancelPenalty"] = self.CancelPenalty


        if tag == "air:BaggageAllowances":
            pass

        if tag == "air:BaggageAllowanceInfo":
            self.BaggageAllowanceInfo["url"] = self.url
            self.BaggageAllowanceInfo["TextInfo"] = self.TextInfo

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            url ={
               "url" : self.Content
            }
            self.url.append(url)

        if tag == "air:TextInfo":
            self.TextInfo = self.Text
            self.Text = []

        if tag == "air:Text":
            url = {
                "Text": self.Content
            }
            self.Text.append(url)

        if tag == "air:BagDetails":
            self.BagDetails["BaggageRestriction"] = self.BaggageRestriction

        if tag == "air:BaggageRestriction":
            self.BaggageRestriction = self.TextInfo
            self.TextInfo = []

        if tag == "air:CarryOnAllowanceInfo":
            pass

        if tag == "air:EmbargoInfo":
            pass

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            pass





    def characters(self, content):
        if self.CurrentData == "common_v29_0:ResponseMessage":
            self.ResponseMessage["message"] = content

        if self.CurrentData == "air:AirReservationLocatorCode":
            self.AirReservationLocatorCode = content

        if self.CurrentData == "common_v29_0:AddressName":
            self.Content = content

        if self.CurrentData == "common_v29_0:Street":
            self.Content = content

        if self.CurrentData == "common_v29_0:City":
            self.Content = content

        if self.CurrentData == "common_v29_0:State":
            self.Content = content

        if self.CurrentData == "common_v29_0:PostalCode":
            self.Content = content

        if self.CurrentData == "common_v29_0:Country":
            self.Content = content

        if self.CurrentData == "air:FareCalc":
            self.Content = content


        if self.CurrentData == "air:Amount":
            self.Content = content


        if self.CurrentData == "air:URL":
            self.Content = content


        if self.CurrentData == "air:Text":
            self.Content = content




    def getFinalData(self):
        self.finalData =  self.BookingData

        return self.finalData




class FlightTicketCancleRespHandler ( xml.sax.ContentHandler ):

    def __init__(self):
        self.CurrentData = ""
        self.ResponseMessage = {}
        self.ResponseMessageAr = []
        self.etr = {}
        self.AirReservationLocatorCode = ""
        self.AgencyInfo = []
        self.AgentAction = {}
        self.BookingTraveler = {}
        self.DeliveryInfo = {}
        self.BookingData = {}
        self.ShippingAddress = []
        self.ssr = []
        self.BillingAddress = {}

        self.BaggageAllowanceInfo = {}

        self.url = []
        self.Text = []

        self.TaxInfo = []

        self.BagDetails = {}

        self.BaggageRestriction = []


    def startElement(self, tag, attributes):
        if tag == "common_v29_0:ResponseMessage":
            self.ResponseMessage = {
                "Code": attributes["Code"],
                "ProviderCode": attributes["ProviderCode"],
                "Type": attributes["Type"],
            }

            self.CurrentData = tag


        if tag == "air:ETR":
            self.etr = {
            "BasePrice" : attributes["BasePrice"],
            "ElStat" : attributes["ElStat"],
            "EquivalentBasePrice" : attributes["EquivalentBasePrice"],
            "Exchangeable" : attributes["Exchangeable"],
            "IATANumber" : attributes["IATANumber"],
            "IssuedDate" : attributes["IssuedDate"],
            "Key" : attributes["Key"],
            "PlatingCarrier" : attributes["PlatingCarrier"],
            "ProviderCode" : attributes["ProviderCode"],
            "ProviderLocatorCode" : attributes["ProviderLocatorCode"],
            "PseudoCityCode" : attributes["PseudoCityCode"],
            "Refundable" : attributes["Refundable"],
            "Taxes" : attributes["Taxes"]
            }


        if tag == "air:AirReservationLocatorCode":
            self.CurrentData = tag


        if tag == "common_v29_0:AgencyInfo":
            pass


        if tag == "common_v29_0:AgentAction":
            self.AgentAction = {
            "ActionType" : attributes["ActionType"],
            "AgencyCode" : attributes["AgencyCode"],
            "AgentCode" : attributes["AgentCode"],
            "BranchCode" : attributes["BranchCode"],
            "EventTime" : attributes["EventTime"]
            }
            self.AgencyInfo.append(self.AgentAction)
            self.AgentAction = {}


        if tag == "common_v29_0:BookingTraveler":
            self.BookingTraveler = {
            "DOB" : "1969-09-17",
            "Gender" : "M",
            "Key" : "gr8AVWGCR064r57Jt0+8bA==",
            "TravelerType" : "ADT"
            }


        if tag == "common_v29_0:BookingTravelerName":
            self.BookingTravelerName = {
                "First" : attributes["First"],
                "Last" : attributes["Last"],
                "Prefix" : attributes["Prefix"]
            }


        if tag == "common_v29_0:DeliveryInfo":
            pass

        if tag == "common_v29_0:ShippingAddress":
            self.ShippingAddressKey = attributes["Key"]

        if tag == "common_v29_0:AddressName":
            self.CurrentData = tag

        if tag == "common_v29_0:Street":
            self.CurrentData = tag

        if tag == "common_v29_0:City":
            self.CurrentData = tag

        if tag == "common_v29_0:State":
            self.CurrentData = tag

        if tag == "common_v29_0:PostalCode":
            self.CurrentData = tag

        if tag == "common_v29_0:Country":
            self.CurrentData = tag


        if tag == "common_v29_0:ProviderReservationInfoRef":
            pass

        if tag == "common_v29_0:PhoneNumber":
            PhoneNumber = {
                "AreaCode": "08",
                "CountryCode": "61",
                "ElStat": "A",
                "Key": "4Vc037UXRzClNfG5ViYIXg==",
                "Location": "PER",
                "Number": "40003000",
                "Type": "Home"
            }

            self.BookingTraveler.update({"PhoneNumber": PhoneNumber})

        if tag == "common_v29_0:ProviderReservationInfoRef":
            self.ProviderReservationInfoRef = attributes["Key"]

        if tag == "common_v29_0:Email":

            Email = {
                "EmailID": attributes["EmailID"],
                "Key": attributes["Key"],
                "Type": attributes["Type"]
            }

            self.BookingTraveler.update({"Email": Email})

        if tag == "common_v29_0:Address":
            self.Address = {
                "ElStat": "A",
                "Key": "n91VIL8gSm22rNKwLSHKpQ=="
            }


        if tag == "common_v29_0:SSR":
            ssr = {
            "Carrier" : attributes["Carrier"],
            "FreeText" : attributes["FreeText"],
            "Key" : attributes["Key"],
            "ProviderReservationInfoRef" : attributes["ProviderReservationInfoRef"],
            "Status" : attributes["Status"],
            "Type" : attributes["Type"]
            }
            self.ssr.append(ssr)


        if tag == "common_v29_0:FormOfPayment":
            self.FormOfPayment = {
            "Key" : "jwt2mcK1Qp27I2xfpcCtAw==",
            "ProfileKey" : "c3KaNgKlQSiX96c+ZAzHSA==",
            "Reusable" : "true",
            "Type" : "Credit"
            }


        if tag == "common_v29_0:CreditCard":
            self.CreditCard = {
            "ExpDate" : "2017-05",
            "Name" : "Jack Smith",
            "Number" : "4123456789001111",
            "Type" : "VI"
            }

        if tag == "common_v29_0:BillingAddress":
            self.BillingAddressKey = attributes["Key"]


        if tag == "common_v29_0:Payment":
            payment = {
            "Amount" : "GBP186.20",
            "FormOfPaymentRef" : "jwt2mcK1Qp27I2xfpcCtAw==",
            "Key" : "yf9y94e1Sia/3oKU/DOddw==",
            "Type" : "Itinerary"
            }


        if tag == "common_v29_0:SupplierLocator":
            SupplierLocator = {
            "SupplierCode" : "QF",
            "SupplierLocatorCode" : "3GA7XM"
            }


        if tag == "air:FareCalc":
            self.CurrentData = tag


        if tag == "air:Ticket":
            self.Ticket = {
            "ElStat" : "A",
            "Key" : "RGLlwNEtT0aG+IeDcMWzNg==",
            "TicketNumber" : "0819902192239",
            "TicketStatus" : "N"
            }


        if tag == "air:Coupon":
            self.coupon = {
            "BookingClass" : "L",
            "CouponNumber" : "1",
            "DepartureTime" : "2014-11-30T06:00:00.000+11:00",
            "Destination" : "MEL",
            "ElStat" : "A",
            "FareBasis" : "LFLEX",
            "Key" : "pIfegR6jSpyurN7duo75fA==",
            "MarketingCarrier" : "QF",
            "MarketingFlightNumber" : "401",
            "MarriageGroup" : "0",
            "Origin" : "SYD",
            "SegmentGroup" : "0",
            "Status" : "O",
            "StopoverCode" : "true"
            }


        if tag == "air:TicketEndorsement":
            self.TicketEndorsement = attributes["Value"]


        if tag == "common_v29_0:Endorsement":
            self.Endorsement = attributes["Value"]


        if tag == "air:BaggageAllowance":
            pass


        if tag == "air:BookingInfo":

            self.BookingInfo = {
            "BookingCode" : "L",
            "CabinClass" : "Economy",
            "FareInfoRef" : "8C8wntyaQaqL3vkOSo5o1w=="
            }


        if tag == "air:TaxInfo":

            TaxInfo = {
            "Amount" : "GBP4.20",
            "Category" : "QR",
            "Key" : "fCsdYYt8Tk2x58TPRJm5NQ=="
            }

            self.TaxInfo.append(TaxInfo)


        if tag == "air:FareCalc":
            self.CurrentData = tag


        if tag == "air:PassengerType":
            PassengerType = {
            "BookingTravelerRef" : "gr8AVWGCR064r57Jt0+8bA==",
            "Code" : "ADT",
            }


        if tag == "air:FareGuaranteeInfo":
            self.GuaranteeType = attributes["GuaranteeType"]


        if tag == "common_v29_0:BookingTravelerRef":
            self.BookingTravelerRefKey = attributes["Key"]


        if tag == "air:ChangePenalty":
            pass


        if tag == "air:Amount":
            self.CurrentData = tag


        if tag == "air:AirPricingInfo":
            self.AirPricingInfo = {
            "AirPricingInfoGroup" : "1",
            "ApproximateBasePrice" : "GBP179.00",
            "ApproximateTotalPrice" : "GBP186.20",
            "BasePrice" : "AUD331.16",
            "ETicketability" : "Yes",
            "EquivalentBasePrice" : "GBP179.00",
            "Exchangeable" : "true",
            "Key" : "6jeI5IdBSo+cstIHWS36Bw==",
            "LatestTicketingTime" : "2014-11-30T23:59:00.000+00:00",
            "PlatingCarrier" : "QF",
            "PricingMethod" : "Guaranteed",
            "PricingType" : "StoredFare",
            "ProviderReservationInfoRef" : "M0RkM31eQ3+0m65rx3oM/Q==",
            "Taxes" : "GBP7.20",
            "Ticketed" : "true",
            "TotalPrice" : "GBP186.20",
            "TrueLastDateToTicket" : "2014-11-30T23:59:00.000+00:00"
            }


        if tag == "air:FareInfo":
            self.FareInfo = {
            "Amount" : "AUD331.16",
            "Destination" : "MEL",
            "EffectiveDate" : "2014-11-10T00:00:00.000+00:00",
            "FareBasis" : "LFLEX",
            "Key" : "8C8wntyaQaqL3vkOSo5o1w==",
            "Origin" : "SYD",
            "PassengerTypeCode" : "ADT"
            }


        if tag == "air:BaggageAllowances":
            pass

        if tag == "air:BaggageAllowanceInfo":
            self.BaggageAllowanceInfo = {
            "Carrier" : attributes["Carrier"],
            "Destination" : attributes["Destination"],
            "Origin" : attributes["Origin"],
            "TravelerType" : attributes["TravelerType"]
            }

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            self.CurrentData = tag

        if tag == "air:TextInfo":
            pass

        if tag == "air:Text":
            self.CurrentData = tag

        if tag == "air:BagDetails":
            self.BagDetails = {
            "ApplicableBags" : attributes["ApplicableBags"],
            "ApproximateBasePrice" : attributes["ApproximateBasePrice"],
            "ApproximateTotalPrice" : attributes["ApproximateTotalPrice"],
            "BasePrice" : attributes["BasePrice"],
            "TotalPrice" : attributes["TotalPrice"]
            }

        if tag == "air:BaggageRestriction":
            pass

        if tag == "air:CarryOnAllowanceInfo":
            pass

        if tag == "air:EmbargoInfo":
            pass

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            pass



    def endElement(self, tag):
        if tag == "common_v29_0:ResponseMessage":
            self.ResponseMessageAr.append(self.ResponseMessage)
            self.CurrentData = ""
            self.ResponseMessage = {}

        if tag == "air:ETR":
            pass

        if tag == "common_v29_0:AgencyInfo":
            pass

        if tag == "common_v29_0:AddressName":
            self.Address["AddressName"] = self.Content

        if tag == "common_v29_0:Street":
            self.Address["Street"] = self.Content

        if tag == "common_v29_0:City":
            self.Address["City"] = self.Content

        if tag == "common_v29_0:State":
            self.Address["State"] = self.Content

        if tag == "common_v29_0:PostalCode":
            self.Address["PostalCode"] = self.Content

        if tag == "common_v29_0:Country":
            self.Address["Country"] = self.Content

        if tag == "common_v29_0:ShippingAddress":
            self.ShippingAddress.append(self.Address)

        if tag == "common_v29_0:FormOfPayment":
           self.FormOfPayment["CreditCard"] = self.CreditCard

        if tag == "common_v29_0:CreditCard":
            self.CreditCard["BillingAddress"] = self.BillingAddress

        if tag == "common_v29_0:BillingAddress":
            self.BillingAddress["Address"] = self.Address

        if tag == "air:FareCalc":
            self.FareCalc = self.Content

        if tag == "air:Ticket":
            self.Ticket["Coupon"] = self.coupon
            self.Ticket["TicketEndorsement"] = self.TicketEndorsement


        if tag == "air:AirPricingInfo":

            pass


        if tag == "air:FareInfo":

            pass


        if tag == "air:FareCalc":
            self.FareCalc = self.Content


        if tag == "air:ChangePenalty":
            self.ChangePenalty = self.Amount


        if tag == "air:CancelPenalty":
            self.CancelPenalty = self.Amount


        if tag == "air:Amount":
            self.Amount = self.Content


        if tag == "air:AirPricingInfo":
            self.AirPricingInfo["FareInfo"] = self.FareInfo
            self.AirPricingInfo["BookingInfo"] = self.BookingInfo
            self.AirPricingInfo["TaxInfo"] = self.TaxInfo
            self.AirPricingInfo["FareCalc"] = self.FareCalc
            self.AirPricingInfo["ChangePenalty"] = self.ChangePenalty
            self.AirPricingInfo["CancelPenalty"] = self.CancelPenalty


        if tag == "air:BaggageAllowances":
            pass

        if tag == "air:BaggageAllowanceInfo":
            self.BaggageAllowanceInfo["url"] = self.url
            self.BaggageAllowanceInfo["TextInfo"] = self.TextInfo

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            url ={
               "url" : self.Content
            }
            self.url.append(url)

        if tag == "air:TextInfo":
            self.TextInfo = self.Text
            self.Text = []

        if tag == "air:Text":
            url = {
                "Text": self.Content
            }
            self.Text.append(url)

        if tag == "air:BagDetails":
            self.BagDetails["BaggageRestriction"] = self.BaggageRestriction

        if tag == "air:BaggageRestriction":
            self.BaggageRestriction = self.TextInfo
            self.TextInfo = []

        if tag == "air:CarryOnAllowanceInfo":
            pass

        if tag == "air:EmbargoInfo":
            pass

        if tag == "air:URLInfo":
            pass

        if tag == "air:URL":
            pass





    def characters(self, content):
        if self.CurrentData == "common_v29_0:ResponseMessage":
            self.ResponseMessage["message"] = content

        if self.CurrentData == "air:AirReservationLocatorCode":
            self.AirReservationLocatorCode = content

        if self.CurrentData == "common_v29_0:AddressName":
            self.Content = content

        if self.CurrentData == "common_v29_0:Street":
            self.Content = content

        if self.CurrentData == "common_v29_0:City":
            self.Content = content

        if self.CurrentData == "common_v29_0:State":
            self.Content = content

        if self.CurrentData == "common_v29_0:PostalCode":
            self.Content = content

        if self.CurrentData == "common_v29_0:Country":
            self.Content = content

        if self.CurrentData == "air:FareCalc":
            self.Content = content


        if self.CurrentData == "air:Amount":
            self.Content = content


        if self.CurrentData == "air:URL":
            self.Content = content


        if self.CurrentData == "air:Text":
            self.Content = content




    def getFinalData(self):
        self.finalData =  self.BookingData

        return self.finalData



class UniversalRecordRetrieveRsp ( xml.sax.ContentHandler ):

    def __init__(self):
        self.CurrentData = ""
        self.ResponseMessage = {}
        self.ResponseMessageAr = []
        self.BookingTraveler = {}
        self.BookingTravelerAr = []
        self.ProviderReservationInfoRef = ""
        self.Address = {}
        self.HotelReservation = {}
        self.HotelProperty = {}
        self.ReservationName = {}
        self.PropertyAddress = ""
        self.HotelPhoneNumber = []
        self.RoomRateDescriptionText = ""
        self.HotelRateByDateAr = []
        self.GuaranteeType = ""
        self.HotelStay = {}
        self.HotelStayAr = []
        self.Guarantee = {}
        self.SellMessage = {}
        self.AgencyInfo = {}
        self.AgentActionAr = []
        self.BookingData = {"error_flag": "0"}

        self.DeliveryInfo = {}
        self.AirSegment = {}
        self.AirSegmentAr = []
        self.flightdetails = {}
        self.flightdetailsAr = []

        self.LocatorCode = ""
        self.AirReservationLocatorCode = ""
        self.ProviderLocatorCode = ""

        self.basePrice = "0"

        self.ProviderReservationInfo = {}

        self.AirPricingInfo = {}

        self.error = 0

        self.error_content = ""

        self.error_data = {"error_flag": "1"}



    def startElement(self, tag, attributes):

        if tag == "universal:UniversalRecord":
            pass

        if tag == "SOAP:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultcode":
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultstring":
            self.CurrentData = tag

        if tag == "SOAP-ENV:detail":
            self.CurrentData = tag

        if tag == "faultcode":
            self.CurrentData = tag

        if tag == "faultstring":
            self.CurrentData = tag

        if tag == "common_v50_0:Description":
            self.CurrentData = tag

        if tag == "air:ErrorMessage":
            self.CurrentData = tag


        if tag == "common_v50_0:ResponseMessage":
            self.ResponseMessage = {
            "Code" : attributes["Code"],
            "ProviderCode" : attributes["ProviderCode"],
            "Type" : attributes["Type"],
            }
            self.CurrentData = tag


        if tag == "universal:UniversalRecord":
            if "LocatorCode" in attributes:
                self.LocatorCode = attributes["LocatorCode"]
            else:
                pass

        if tag == "common_v50_0:BookingTraveler":
            self.BookingTraveler = {
            "Gender" : "M",
            "Key" : attributes["Key"],
            "TravelerType" : attributes["TravelerType"],
             "Age" : "50"
            }

        if tag == "common_v50_0:BookingTravelerName":
            BookingTravelerName = {
            "First" : attributes["First"],
            "Last" : attributes["Last"],
            "Prefix" : attributes["Prefix"]
            }

            self.BookingTraveler["BookingTravelerName"] = BookingTravelerName
            #self.BookingTraveler.update(BookingTravelerName)

        if tag == "common_v50_0:DeliveryInfo":
            pass

        if tag == "common_v50_0:PhoneNumber":
            PhoneNumber = {
            "AreaCode" : "08",
            "CountryCode" : "61",
            "ElStat" : "A",
            "Key" : "4Vc037UXRzClNfG5ViYIXg==",
            "Location" : "PER",
            "Number" : "40003000",
            "Type" : "Home"
            }

            self.BookingTraveler.update({ "PhoneNumber" : PhoneNumber })

        if tag == "common_v50_0:ProviderReservationInfoRef":
            self.ProviderReservationInfoRef = attributes["Key"]

        if tag == "common_v50_0:Email":
            Email = {
            "EmailID" : attributes["EmailID"],
            "Key" : attributes["Key"],
            "Type" : attributes["Type"]
            }

            self.BookingTraveler.update({"Email": Email})

        if tag == "common_v50_0:Address":
            self.Address = {
            "ElStat" : "A",
            "Key" : "n91VIL8gSm22rNKwLSHKpQ=="
            }

        if tag == "common_v50_0:AddressName":
            self.CurrentData = tag

        if tag == "common_v50_0:Street":
            self.CurrentData = tag

        if tag == "common_v50_0:City":
            self.CurrentData = tag

        if tag == "common_v50_0:State":
            self.CurrentData = tag

        if tag == "common_v50_0:PostalCode":
            self.CurrentData = tag

        if tag == "common_v50_0:Country":
            self.CurrentData = tag

        if tag == "universal:ProviderReservationInfo":
            self.ProviderReservationInfo = {
            "Key" : attributes["Key"] if "Key" in attributes else "",
            "ProviderCode" : attributes["ProviderCode"] if "ProviderCode" in attributes else "" ,
            "LocatorCode" : attributes["LocatorCode"] if "LocatorCode" in attributes else "" ,
            "CreateDate" : attributes["CreateDate"] if "CreateDate" in attributes else "" ,
            "ModifiedDate" : attributes["ModifiedDate"] if "ModifiedDate" in attributes else "" ,
            "HostCreateDate" : attributes["HostCreateDate"] if "HostCreateDate" in attributes else "" ,
            "OwningPCC" : attributes["OwningPCC"] if "OwningPCC" in attributes else ""
            }

            self.ProviderLocatorCode = attributes["LocatorCode"] if "LocatorCode" in attributes else ""



        if tag == "air:AirReservation":
            self.AirReservation = {
            "CreateDate" : attributes["CreateDate"],
            "LocatorCode" : attributes["LocatorCode"],
            "ModifiedDate" : attributes["ModifiedDate"]
            }
            self.AirReservationLocatorCode = attributes["LocatorCode"] if "LocatorCode" in attributes else ""

        if tag == "common_v50_0:SupplierLocator":
            SupplierLocator = {
                "CreateDateTime" : attributes["CreateDateTime"],
                "ProviderReservationInfoRef" : attributes["ProviderReservationInfoRef"],
                "SupplierCode" : attributes["SupplierCode"],
                "SupplierLocatorCode" : attributes["SupplierLocatorCode"]
            }
            self.AirReservation.update({"SupplierLocator" : SupplierLocator })

        if tag == "air:AirSegment" and self.error == 0:
            self.AirSegment = {
            "ArrivalTime" : attributes["ArrivalTime"],
            "CabinClass" : "CabinClass",
            "Carrier" : attributes["Carrier"],
            "ChangeOfPlane" : "ChangeOfPlane",
            "ClassOfService" : attributes["ClassOfService"],
            "DepartureTime" : attributes["DepartureTime"],
            "Destination" : attributes["Destination"],
            "Distance" : "Distance",
            "ETicketability" : "ETicketability",
            "ElStat" : "ElStat",
            "Equipment" : attributes["Equipment"] if "Equipment" in attributes else "",
            "FlightNumber" : attributes["FlightNumber"],
            "Group" : attributes["Group"],
            "GuaranteedPaymentCarrier" : "GuaranteedPaymentCarrier",
            "Key" : attributes["Key"],
            "OptionalServicesIndicator" : attributes["OptionalServicesIndicator"],
            "Origin" : attributes["Origin"],
            "ProviderCode" : attributes["ProviderCode"],
            "ProviderReservationInfoRef" : "ProviderReservationInfoRef",
            "Status" : attributes["Status"],
            "TravelOrder" : "TravelOrder",
            "TravelTime" : attributes["TravelTime"]
            }


        if tag == "air:FlightDetails":

            self.flightdetails = {
            "ArrivalTime" : "2014-11-30T07:35:00.000+11:00",
            "DepartureTime" : "2014-11-30T06:00:00.000+11:00",
            "Destination" : "MEL",
            "DestinationTerminal" : "1",
            "ElStat" : "A",
            "Equipment" : "73H",
            "FlightTime" : "95",
            "Key" : "zV1ojUKoRGiUQUFEMgDUQQ==",
            "Origin" : "SYD",
            "OriginTerminal" : "3",
            "TravelTime" : "95"
            }


        if tag == "air:AirPricingInfo":

            self.AirPricingInfo = {
            "AirPricingInfoGroup" : attributes["AirPricingInfoGroup"] if "AirPricingInfoGroup" in attributes else "",
            "ApproximateBasePrice" : attributes["ApproximateBasePrice"] if "ApproximateBasePrice" in attributes else "",
            "ApproximateTotalPrice" : attributes["ApproximateTotalPrice"] if "ApproximateTotalPrice" in attributes else "",
            "BasePrice" : attributes["BasePrice"] if "BasePrice" in attributes else "",
            "ETicketability" : attributes["ETicketability"] if "ETicketability" in attributes else "",
            "ElStat" : "ElStat" if "ElStat" in attributes else "",
            "EquivalentBasePrice" : attributes["EquivalentBasePrice"]  if "EquivalentBasePrice" in attributes else "",
            "Exchangeable" : attributes["Exchangeable"] if "Exchangeable" in attributes else "",
            "IncludesVAT" : attributes["IncludesVAT"] if "IncludesVAT" in attributes else "",
            "Key" : attributes["Key"] if "Key" in attributes else "",
            "LatestTicketingTime" : attributes["LatestTicketingTime"] if "LatestTicketingTime" in attributes else "",
            "PlatingCarrier" : attributes["PlatingCarrier"] if "PlatingCarrier" in attributes else "",
            "PricingMethod" : attributes["PricingMethod"] if "PricingMethod" in attributes else "",
            "PricingType" : attributes["PricingType"] if "PricingType" in attributes else "",
            "ProviderCode" : attributes["ProviderCode"] if "ProviderCode" in attributes else "",
            "ProviderReservationInfoRef" : attributes["ProviderReservationInfoRef"] if "ProviderReservationInfoRef" in attributes else "",
            "Taxes" : attributes["Taxes"] if "Taxes" in attributes else "",
            "TotalPrice" : attributes["TotalPrice"] if "TotalPrice" in attributes else "",
            "TrueLastDateToTicket" : attributes["TrueLastDateToTicket"] if "TrueLastDateToTicket" in attributes else ""
            }

            self.basePrice = attributes["BasePrice"] if "BasePrice" in attributes else "0"



            if tag == "SellMessage":
                self.CurrentData = tag


        if tag == "common_v50_0:FormOfPayment":
            pass

        if tag == "common_v50_0:CreditCard":
            self.CreditCard = {
            "ExpDate" : attributes["ExpDate"],
            "Name" : attributes["Name"],
            "Number" : attributes["Number"],
            "Type" : attributes["Type"]
            }

        if tag == "common_v50_0:BillingAddress":
            self.BillingAddress = {
            "ElStat" : "A",
            "Key" : "heqATi9qSYm/y1GLGs/QVw=="
            }


        if tag == "common_v50_0:ReservationName":
            self.ReservationName = {}

        if tag == "common_v50_0:NameOverride":
            self.ReservationName["First"] = attributes["First"]
            self.ReservationName["Last"] = attributes["Last"]

        if tag == "hotel:HotelProperty":
            self.HotelProperty = {
            "HotelChain" : attributes["HotelChain"],
            "HotelCode" : attributes["HotelCode"],
            "HotelLocation" : attributes["HotelLocation"],
            "Name" : attributes["Name"],
            "ParticipationLevel" : attributes["ParticipationLevel"]
            }

        if tag == "hotel:Address":
            self.PropertyAddress = tag

        if tag == "common_v50_0:PhoneNumber":
            PhoneNumber = {
            "Number" : "1-303-371-0888",
            "Type" : "Hotel"
            }
            self.HotelPhoneNumber.append(PhoneNumber)

        if tag == "hotel:HotelRateDetail":
            self.HotelRateDetail = {
            "Base" : attributes["Base"],
            "RateGuaranteed" : attributes["RateGuaranteed"],
            "RatePlanType" : attributes["RatePlanType"],
            "Total" : attributes["Total"]
            }

        if tag == "hotel:RoomRateDescription":
            self.Name = attributes["Name"]


        if tag == "hotel:Text":
            self.CurrentData = tag

        if tag == "hotel:HotelRateByDate":
            HotelRateByDate = {
            "Base" : "USD99.00",
            "EffectiveDate" : "2014-12-05",
            "ExpireDate" : "2014-12-08"
            }

            self.HotelRateByDateAr.append(HotelRateByDate)

        if tag == "hotel: GuaranteeInfo":
            self.GuaranteeType = attributes["GuaranteeType"]


        if tag == "hotel:HotelStay":
            self.HotelStay = {}

        if tag == "hotel:CheckinDate":
            self.CurrentData = tag

        if tag == "hotel:CheckoutDate":
            self.CurrentData = tag


        if tag == "common_v50_0:Guarantee":
            self.Guarantee = {
            "ElStat" : "A",
            "Key" : "39uAKjkbQveitaPPPeVeOg==",
            "Reusable" : "true",
            "Type" : "Guarantee"
            }

        if tag == "common_v50_0:CreditCard":
            CreditCard = {
            "ExpDate" : attributes["ExpDate"],
            "Number" : attributes["Number"],
            "Type" : attributes["Type"]
            }

            self.Guarantee["CreditCard"] = CreditCard

        if tag == "common_v50_0:BookingSource":
            self.BookingSource = {
            "Code" : "99999992",
            "Type" : "IataNumber"
            }

        if tag == "hotel:GuestInformation":
            self.GuestInformation = {
                "NumberOfRooms" : attributes["NumberOfRooms"]
            }

        if tag == "hotel:NumberOfAdults":
            self.CurrentData = tag

        if tag == "common_v50_0:SellMessage":
            self.CurrentData = tag


        if tag == "common_v50_0:AgencyInfo":
            self.AgencyInfo = {}

        if tag == "common_v50_0:AgentAction":
            AgentAction = {
            "ActionType" : attributes["ActionType"],
            "AgencyCode" : attributes["AgencyCode"],
            "AgentCode" : attributes["AgentCode"],
            "BranchCode" : attributes["BranchCode"],
            "EventTime" : attributes["EventTime"]
            }

            self.AgentActionAr.append(AgentAction)



    def endElement(self, tag):

        if tag == "universal:UniversalRecord":
            pass

        if tag == "SOAP-ENV:faultcode":
            pass

        if tag == "SOAP-ENV:faultstring":
            self.error_data['faultstring'] = self.Content

        if tag == "SOAP-ENV:detail":
            self.error_data['Description'] = self.Content


        if tag == "SOAP:Fault":
            pass

        if tag == "faultcode":
            self.error_data['faultcode'] = self.Content

        if tag == "faultstring":
            self.error_data['faultstring'] = self.Content


        if tag == "air:ErrorMessage":
            self.error_data['ErrorMessage'] = self.Content

        if tag == "common_v50_0:Description":
            self.error_data['Description'] = self.Content

        if tag == "common_v50_0:ResponseMessage":
            self.ResponseMessageAr.append(self.ResponseMessage)
            self.CurrentData = ""
            self.ResponseMessage = {}

        if tag == "universal:UniversalRecord":
            pass

        if tag == "common_v50_0:BookingTraveler":
            pass

        if tag == "common_v50_0:AddressName":
            self.Address["AddressName"] = self.Content

        if tag == "common_v50_0:Street":
            self.Address["Street"] = self.Content

        if tag == "common_v50_0:City":
            self.Address["City"] = self.Content

        if tag == "common_v50_0:State":
            self.Address["State"] = self.Content

        if tag == "common_v50_0:PostalCode":
            self.Address["PostalCode"] = self.Content

        if tag == "common_v50_0:Country":
            self.Address["Country"] = self.Content

        if tag == "common_v50_0:Address":
            self.BookingTraveler.update({"Address" : self.Address })

        if tag == "common_v50_0:DeliveryInfo":
            self.DeliveryInfo.update({"Address" : self.Address })

        if tag == "air:FlightDetails":
            self.flightdetailsAr.append(self.flightdetails)
            self.flightdetails = {}


        if tag == "air:AirSegment":
            self.AirSegment.update({ "FlightDetails" : self.flightdetailsAr , "SellMessage" :  self.SellMessage })

            self.AirSegmentAr.append(self.AirSegment)
            self.AirSegment = {}
            self.SellMessage = {}

        if tag == "air:AirReservation":
            self.AirReservation.update({ "AirSegments" : self.AirSegmentAr })

        if tag == "air:AirPricingInfo":
            pass

        if tag == "air:FareInfo":
            pass

        if tag == "common_v50_0:FormOfPayment":
            pass

        if tag == "air:TicketingModifiers":
            pass

        if tag == "common_v50_0:AgencyInfo":
            pass

        if tag == "common_v50_0:AgentAction":
            pass

        if tag == "SellMessage":
            pass
            #self.SellMessage.append({"SellMsg" : self.Content })

        if tag == "common_v50_0:CreditCard":
            self.CreditCard.update({ "BillingAddress" : self.BillingAddress })

        if tag == "common_v50_0:BillingAddress":
            self.BillingAddress.update({"Address" : self.Address })
            self.Address = {}

        if tag == "common_v50_0:BookingTraveler":
            self.BookingTraveler.update({ "DeliveryInfo" : self.DeliveryInfo })
            self.BookingTravelerAr.append(self.BookingTraveler)

        if tag == "common_v50_0:ReservationName":
            self.HotelReservation.update({"ReservationName" : self.ReservationName})

        if tag == "hotel:Address":
            self.PropertyAddress = self.Content + " "

        if tag == "hotel:PropertyAddress":
            self.HotelProperty["Address"] = self.PropertyAddress

        if tag == "hotel:HotelProperty":
            self.HotelProperty["Number"] = self.HotelPhoneNumber

        if tag == "hotel:Text":
            self.RoomRateDescriptionText = self.Content + " "

        if tag == "hotel:RoomRateDescription":
            self.HotelRateDetail[self.Name] = self.RoomRateDescriptionText


        if tag == "hotel:HotelRateDetail":
            self.HotelRateDetail["HotelRateByDate"] = self.HotelRateByDateAr
            self.HotelRateDetail["GuaranteeType"] = self.GuaranteeType


        if tag == "hotel:CheckinDate":
            CheckinDate = self.Content
            self.HotelStay["CheckinDate"] = CheckinDate

        if tag == "hotel:CheckoutDate":
            CheckoutDate = self.Content
            self.HotelStay["CheckoutDate"] = CheckoutDate

        if tag == "hotel:HotelStay":
            self.HotelStayAr.append(self.HotelStay)

        if tag == "common_v50_0:SellMessage":
            pass
            #self.SellMessage = self.SellMessage + " " + self.Content
            #self.SellMessage.append({"SellMsg": self.Content})


        if tag == "hotel:HotelReservation":
            self.HotelReservation.update({"HotelProperty": self.HotelProperty})
            self.HotelReservation.update({"HotelRateDetail": self.HotelRateDetail})
            self.HotelReservation.update({"HotelStay": self.HotelStayAr})
            self.HotelReservation.update({"Guarantee": self.Guarantee})
            self.HotelReservation.update({"BookingSource": self.BookingSource})
            self.HotelReservation.update({"GuestInformation": self.GuestInformation})
            self.HotelReservation.update({"SellMessage": self.SellMessage})


        if tag == "common_v50_0:AgencyInfo":
            self.AgencyInfo = { "AgentAction" : self.AgentActionAr }

        if tag == "universal:UniversalRecord":
            self.BookingData = {
                "ResponseMessage": self.ResponseMessageAr,
                "BookingTraveler": self.BookingTravelerAr,
                "HotelReservation": self.HotelReservation,
                "AgencyInfo": self.AgencyInfo,
                "AirReservation" : self.AirReservation,
                "AirPricingInfo" : self.AirPricingInfo
            }


    def characters(self, content):
        if self.CurrentData == "common_v50_0:ResponseMessage":
            self.ResponseMessage["message"] = content

        if self.CurrentData == "common_v50_0:AddressName":
            self.Content = content

        if self.CurrentData == "common_v50_0:Street":
            self.Content = content

        if self.CurrentData == "common_v50_0:City":
            self.Content = content

        if self.CurrentData == "common_v50_0:State":
            self.Content = content

        if self.CurrentData == "common_v50_0:PostalCode":
            self.Content = content

        if self.CurrentData == "common_v50_0:Country":
            self.Content = content

        if self.CurrentData == "hotel:Address":
            self.Content = content

        if self.CurrentData == "hotel:Text":
            self.Content = content

        if self.CurrentData == "hotel:CheckinDate":
            self.Content = content

        if self.CurrentData == "hotel:CheckoutDate":
            self.Content = content

        if self.CurrentData == "common_v50_0:SellMessage":
            self.Content = content

        if self.CurrentData == "hotel: NumberOfAdults":
            self.GuestInformation["NumberOfAdults"] = content

        if self.CurrentData == "SellMessage":
            self.Content = content

        # error handling

        if self.CurrentData == "faultcode":
            self.Content = content

        if self.CurrentData == "faultstring":
            self.Content = content

        if self.CurrentData == "common_v50_0:Description":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:faultstring":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:detail":
            self.Content = content

        if self.CurrentData == "air:ErrorMessage":
            self.Content = content



    def getFinalData(self):
        self.finalData =  self.BookingData

        if self.LocatorCode == "":
            pass
        else:
            self.BookingData["LocatorCode"] = self.LocatorCode
            self.BookingData["AirReservationLocatorCode"] = self.AirReservationLocatorCode
            self.BookingData["ProviderLocatorCode"] = self.ProviderLocatorCode

            self.BookingData["BasePrice"] = self.basePrice

        if self.error == 0 :
            self.finalData =  self.BookingData
        else:
            self.finalData = self.error_data

        return self.finalData





class UniversalRecordCancelRsp(xml.sax.ContentHandler):

    def __init__(self):
        self.CurrentData = ""
        self.ProviderReservationStatus = {}
        self.CancelInfo = {}
        self.Content = ""
        self.cancle_req_resp_data = {"error_flag": "1"}
        self.cancle_status = 0

        self.error = 0

        self.error_content = ""

        self.error_data = {"error_flag": "1"}

    def startElement(self, tag, attributes):

        if tag == "universal:UniversalRecord":
            pass

        if tag == "SOAP:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:Fault":
            self.error = 1
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultcode":
            self.CurrentData = tag

        if tag == "SOAP-ENV:faultstring":
            self.CurrentData = tag

        if tag == "SOAP-ENV:detail":
            self.CurrentData = tag

        if tag == "faultcode":
            self.CurrentData = tag

        if tag == "faultstring":
            self.CurrentData = tag

        if tag == "common_v50_0:Description":
            self.CurrentData = tag

        if tag == "air:ErrorMessage":
            self.CurrentData = tag


        if tag == "universal:UniversalRecordCancelRsp":
            pass

        if tag == "universal:ProviderReservationStatus":
            self.ProviderReservationStatus = {
            "CreateDate" : attributes["CreateDate"],
            "ModifiedDate" : attributes["ModifiedDate"],
            "ProviderCode" : attributes["ProviderCode"],
            "LocatorCode" : attributes["LocatorCode"],
            "Cancelled" : attributes["Cancelled"]
            }

            if attributes["Cancelled"]:
                self.cancle_status = 1

        if tag == "universal:CancelInfo":
            self.CancelInfo["Code"] = attributes["Code"]
            self.CancelInfo["Type"] = attributes["Type"]

            self.CurrentData = tag


    def endElement(self, tag):

        if tag == "universal:UniversalRecord":
            pass

        if tag == "SOAP-ENV:faultcode":
            pass

        if tag == "SOAP-ENV:faultstring":
            self.error_data['faultstring'] = self.Content

        if tag == "SOAP-ENV:detail":
            self.error_data['Description'] = self.Content


        if tag == "SOAP:Fault":
            pass

        if tag == "faultcode":
            self.error_data['faultcode'] = self.Content

        if tag == "faultstring":
            self.error_data['faultstring'] = self.Content


        if tag == "air:ErrorMessage":
            self.error_data['ErrorMessage'] = self.Content

        if tag == "common_v50_0:Description":
            self.error_data['Description'] = self.Content


        if tag == "universal:UniversalRecordCancelRsp":
            self.cancle_req_resp_data["ProviderReservationStatus"] = self.ProviderReservationStatus

            self.cancle_req_resp_data["CancelInfo"] = self.CancelInfo


        if tag == "universal:ProviderReservationStatus":
            pass

        if tag == "universal:CancelInfo":
            self.CancelInfo["cancl_msg"] = self.Content

    def characters(self, content):

        if self.CurrentData == "faultcode":
            self.Content = content

        if self.CurrentData == "faultstring":
            self.Content = content

        if self.CurrentData == "common_v50_0:Description":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:faultstring":
            self.Content = content

        if self.CurrentData == "SOAP-ENV:detail":
            self.Content = content

        if self.CurrentData == "air:ErrorMessage":
            self.Content = content


        if self.CurrentData == "universal:CancelInfo":
            self.Content = content


    def getFinalData(self):

        if self.error == 0 :
            self.finalData =  self.cancle_req_resp_data
        else:
            self.finalData = self.error_data

        return self.finalData













