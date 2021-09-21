def pdftest(request):
    try:
        print('i m here')
        login_type = request.session['login_type']
        access_token = request.session['access_token']
        booking_id = 13

        url = settings.API_BASE_URL + "view_bus_booking"
        payload = {'booking_id': booking_id}
        booking = getDataFromAPI(login_type, access_token, url, payload)
        booking = booking['Bookings']

        print(booking)

        value = {}

        for book in booking:

            for bk in book:

                if bk == 'Passangers':
                    print("Passanger Found")
                    if len(book[bk]) == 0:
                        value[bk] = {'employee_name': 'none','employee_email': 'none'}
                else:
                    v = book[bk]
                    value[bk] = v

        value['ticket_price'] = "1200"

        bus_pdf = Pdf(value)
        abc = bus_pdf.get(request)

        return HttpResponse(abc,content_type="application/pdf")
    except Exception as e:
        print('exception---')
        print(e)
