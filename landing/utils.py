from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from Common.models import Corporate_Agent


from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    #pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def get_choice():

    BLANK_CHOICE = (('', 'Select Agent'),)

    CHOICES = BLANK_CHOICE + tuple(Corporate_Agent.objects.values_list('id', 'user_name'))

    #CHOICES = Corporate_Agent.objects.values('id', 'user_name')

    #CHOICES = [(q) for q in CHOICESS]

    return CHOICES


