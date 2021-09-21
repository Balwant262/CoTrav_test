import random
import string
from threading import Thread

import requests
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render , redirect , get_object_or_404
from django_global_request.middleware import get_request
from django.utils import timezone

from Common.VIEW.Agent.agent_views import getDataFromAPI
from landing.forms import LeadGenerationModelForm , LeadUpdateForm

from django.views import generic

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.db.models.signals import post_save
from django.dispatch import receiver

from landing.models import Leadgeneration , LeadComments , LeadLog , Document
from Common.models import Corporate_Agent, Corporate
from landing.cotrav_messeging import LeadGenerationEmail

from django.contrib.auth.decorators import login_required

from django.contrib.messages.views import SuccessMessageMixin

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.views.generic.edit import ModelFormMixin

from django.contrib import messages

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import os

from django.core.files.storage import default_storage


from landing.models import Document
from Common.email_settings import SignupEmail,Lead_Status_Change_Email,Lead_Email_To_Company_assign_agent

from landing.utils import get_choice


def lead_detail_view(request, pk):
    try:

        #lead = Leadgeneration.objects.raw('SELECT l.*,ca.user_name FROM cotrav_lead_generation_module l LEFT JOIN corporate_agents ca ON l.Assigned_Sales_Person = ca.id WHERE 1')
        lead = Leadgeneration.objects.get(id=pk)
        s_id = lead.Assigned_Sales_Person
        if s_id > 0:
            sales_person = Corporate_Agent.objects.get(id = s_id)
        else:
            sales_person = {'user_name':'not assigned'}


    except Leadgeneration.DoesNotExist:
        raise Http404('Book does not exist')

    return render(request, 'landing/lead_detail.html', context={'lead': lead , 'person':sales_person})


@receiver(post_save, sender=Leadgeneration)
def my_handler(sender, instance , created , **kwargs):
    corporate_name = instance.Company_Name
    corporate_location = instance.Company_Location
    contact_person_name = instance.Contact_Name
    contact_person_no = instance.Contact_Number
    contact_person_email = instance.Contact_Email
    message = instance.Message

    if(created) :
        print ("create call")
        #message = ""
        signup = SignupEmail(corporate_name, corporate_location, contact_person_name, contact_person_no, contact_person_email, message)
        #resp1 = signup.send_email()
        thread = Thread(target=signup.send_email, args=())
        thread.start()

    else:
        print("update call")
        print(instance.id)
        ag_id = instance.Assigned_Sales_Person
        ag_email = Corporate_Agent.objects.get(id=ag_id).email
        ag_name = Corporate_Agent.objects.get(id=ag_id).user_name
        ag_no = Corporate_Agent.objects.get(id=ag_id).contact_no
        message = ""
        if instance.Status == "Closed-Win":
            try:
                corporate_name = instance.Company_Name
                ref = Corporate.objects.get(corporate_name=corporate_name)
                print("company with same name allready exist")

            except ObjectDoesNotExist:
                corporate_name = instance.Company_Name
                corporate_city = instance.Company_Location
                corporate_code = instance.Company_Name
                contact_person_name = instance.Contact_Name
                contact_person_no = instance.Contact_Number
                contact_person_email = instance.Contact_Email
                contact_address_line1 = instance.Contact_Address
                contact_address_line2 = instance.Contact_Address_Line2
                contact_address_line3 = instance.Contact_Address_Line3

                company = Corporate()

                company.corporate_name = corporate_name
                company.corporate_city = corporate_city
                company.corporate_code = corporate_code
                company.contact_person_name = contact_person_name
                company.contact_person_no = contact_person_no
                company.contact_person_email = contact_person_email
                company.contact_address_line1 = contact_address_line1
                company.contact_address_line2 = contact_address_line2
                company.contact_address_line3 = contact_address_line3
                company.has_auth_level = 0
                company.no_of_auth_level = 0
                company.has_assessment_codes = 0
                company.is_radio = 0
                company.is_local = 1
                company.is_outstation = 1
                company.is_bus = 1
                company.is_train = 1
                company.is_hotel = 1
                company.is_meal = 0
                company.is_flight = 1
                company.is_water_bottles = 1
                company.is_reverse_logistics = 1
                company.is_deleted = 0
                company.is_send_email = 0
                company.is_send_sms = 0

                company.save()
                request = get_request()
                login_type = request.session['agent_login_type']
                access_token = request.session['agent_access_token']
                access_token_auth = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(60))
                password = "taxi123"
                payload = {'corporate_id': company.pk, 'user_id': request.user.id, 'login_type': login_type,
                           'access_token': access_token, 'name': contact_person_name, 'email': contact_person_email, 'cid': '',
                           'contact_no': contact_person_no,
                           'is_radio': 0, 'is_local': 1, 'is_outstation': 1, 'is_bus': 1,
                           'is_train': 1, 'is_hotel': 1, 'is_meal': 0, 'is_flight': 1,
                           'is_water_bottles': 1, 'is_reverse_logistics': 1,
                           'access_token_auth': access_token_auth,'password': password}
                url = settings.API_BASE_URL + "add_admin"
                company111 = getDataFromAPI(login_type, access_token, url, payload)

                payload1 = {'corporate_id':company.pk, 'rm_level_1_id':ag_id, 'is_active':1}
                url2 = settings.API_BASE_URL + "add_relationship_managements"
                company1111 = getDataFromAPI(login_type, access_token, url2, payload1)

                message = "Congratulation on converting your lead to Closed-Win. Your diligence, self-motivation as well as dedication to always go the extra mile in order to achieve the best possible results is really admirable. Thank you for your hard work and effort."
                print("Lead is converted to new company after closed-win status")

                signup1 = Lead_Status_Change_Email(message, "", ag_email, ag_name, instance.Company_Name, instance.Contact_Name, instance.Contact_Email,
                 instance.Contact_Number, instance.Company_Location)
                resp1 = signup1.send_email()
                print("in mail send fun")
                print(resp1)

        elif instance.Status == "Closed-Lost":
            message = "Sorry to loose you, We will miss you, let me know if we could be of any help in future. CoTrav Team"
            signup1 = Lead_Status_Change_Email(message, "", ag_email, ag_name, instance.Company_Name,
                                               instance.Contact_Name, instance.Contact_Email,
                                               instance.Contact_Number, instance.Company_Location)
            resp1 = signup1.send_email_lost()

        elif instance.Status == "Assigned":
            message = "New Lead has been assigned to your queue"
            # message = "Lead with id " + str(instance.id) + " is updated and assigned to agent " + ag_email
            status = instance.Status
            signup = Lead_Status_Change_Email(message, status, ag_email, ag_name, instance.Company_Name,
                                              instance.Contact_Name, instance.Contact_Email, instance.Contact_Number,
                                              instance.Company_Location)
            resp1 = signup.send_email()
            message1 = "A Relationship Manager from Cotrav Team has been assigned to you to solve all your queries. Please find the details below."
            signup1 = Lead_Email_To_Company_assign_agent(message1, ag_email, ag_name, ag_no, instance.Contact_Name, instance.Contact_Email, instance.Contact_Number)
            resp1 = signup1.send_email()

            print("in mail send fun")
            print(resp1)
        else:
            message = "Lead Status Changed "
            status = instance.Status
            signup = Lead_Status_Change_Email(message,status,ag_email,ag_name,instance.Company_Name,instance.Contact_Name,instance.Contact_Email,instance.Contact_Number,instance.Company_Location)
            resp1 = signup.send_email()
            print("in mail send fun")
            print(resp1)




@login_required(login_url='/agents/login')
def leads(request):
    user_id = request.user.id
    print("is admin")
    print(request.user.is_super_admin)
    if request.user.is_super_admin == 1:
        print("in if")
        leads = Leadgeneration.objects.raw('SELECT l.*,ca.user_name FROM cotrav_lead_generation_module l LEFT JOIN corporate_agents ca ON l.Assigned_Sales_Person = ca.id WHERE 1 ORDER BY l.`created` DESC')
    else:
        print("in else")
        leads = Leadgeneration.objects.raw('SELECT l.*,ca.user_name FROM cotrav_lead_generation_module l LEFT JOIN corporate_agents ca ON l.Assigned_Sales_Person = ca.id WHERE l.Assigned_Sales_Person = '+str(user_id)+' ORDER BY l.`created` DESC')
    agents = Corporate_Agent.objects.all()
    return render(request,'landing/leadgeneration_list.html',{'leads':leads,'agents':agents})



@require_POST
def file_upload(request,lead_id):
    file_up = request.FILES['Attachments']
    save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', str(file_up))
    path = default_storage.save(save_path, request.FILES['Attachments'])
    doc_name = request.POST.get('doc_name', '')
    lead = Leadgeneration.objects.get(id=lead_id)
   # document = Document.objects.create(document=path, upload_by=lead, doc_name=doc_name)
    document = Document.objects.create(document=str(file_up), upload_by=lead, doc_name=doc_name)
    return JsonResponse({'document': document.id})




@login_required(login_url='/agents/login')
def lead_update(request, pk, template_name='landing/leadgeneration_form.html'):

    lead = get_object_or_404(Leadgeneration, pk=pk)

    comments = LeadComments.objects.filter(lead_id=pk)
    attachment = Document.objects.filter(upload_by=pk)

    if request.method == 'POST':

        form = LeadUpdateForm(request.POST or None, instance=lead , initial={'Comments': ''})

        if form.is_valid():
            edit_lead = form.save()
            if request.FILES:
                resp = file_upload(request, edit_lead.pk)
            new_comment = form.cleaned_data['Comments']
            status_action = form.cleaned_data['Status']
            # print(new_lead.pk)
            # print(form.cleaned_data['Comments'])
            cmt = LeadComments()
            cmt.lead_id = edit_lead.pk
            cmt.comment = new_comment
            cmt.created_by = request.user
            cmt.created_at = timezone.now()
            cmt.save()
            log = LeadLog()
            log.lead_id = edit_lead.pk
            log.comment = new_comment
            log.status_action = status_action
            log.action_initiated_by = request.user.id
            log.save()

            messages.success(request, "Lead Status Updated Successfully..!")
            return redirect('lead-list')
        else:

            print("eoorr listing")
            print(form.errors)
            messages.error(request, "Lead Status Not Updated ..!")
            form = LeadUpdateForm(request.POST or None, instance=lead , initial={'Comments': ''})

            return render(request, template_name, {'form': form, 'comments': comments, 'attachments': attachment, 'form_title': 'Update Lead' })
    else:
        lead_created = lead.created
        lead_modified = lead.modified
        diff_date = lead_modified - lead_created
        diff_date = diff_date.days
        if lead.Status == 'Closed-Win':
            status_msg = "Lead is Closed-Win in "
        else:
            status_msg = "Lead is still active from last "

        form = LeadUpdateForm(request.POST or None, instance=lead , initial={'Comments': ''})

    return render(request, template_name, {'form':form,'status_msg': status_msg ,'diff_date':diff_date,'comments':comments,'attachments':attachment, 'form_title': 'Update Lead' })



@login_required(login_url='/agents/login')
def lead_create(request, template_name='landing/leadgeneration_form.html'):
    if request.method == 'POST':
        form = LeadGenerationModelForm(request.POST or None , request.FILES)
        if form.is_valid():

            new_lead = form.save()
            if request.FILES:
                resp = file_upload(request, new_lead.pk)

            new_comment = form.cleaned_data['Comments']
            status_action = form.cleaned_data['Status']
            #print(new_lead.pk)
            #print(form.cleaned_data['Comments'])
            cmt = LeadComments()
            cmt.lead_id = new_lead.pk
            cmt.comment = new_comment
            cmt.created_by = request.user
            cmt.created_at = timezone.now()
            cmt.save()
            log = LeadLog()
            log.lead_id = new_lead.pk
            log.comment = new_comment
            log.status_action = status_action
            log.action_initiated_by = request.user.id
            log.save()
            is_email = request.POST.get('is_email')
            is_sms = request.POST.get('is_sms')

            if is_email:
                print("in email")
                Contact_Name = request.POST.get('Contact_Name', '')
                Company_Name = request.POST.get('Company_Name', '')
                Contact_Number = request.POST.get('Contact_Number', '')
                Contact_Email = request.POST.get('Contact_Email', '')
                corporate_location = request.POST.get('Company_Location', '')
                message = "Thank you for contacting us, our sales person will get in touch with you as earliest as possible.<br><br>Regards,<br>CoTrav"
                signup = SignupEmail(Company_Name, corporate_location, Contact_Name, Contact_Number,
                                     Contact_Email, message)
                resp1 = signup.send_email()
                print(resp1)
            if is_sms:
                print("in smsm")
                sender_id = 'COTRAV'
                exotel_sid = "novuslogic1"
                exotel_key = "6ae4c99860c31346203da94dc98a4de7fd002addc5848182"
                exotel_token = "a2c78520d23942ad9ad457b81de2ee3f3be743a8188f8c39"
                Contact_no = request.POST.get('Contact_Number')
                sms_body = "Thank you for contacting us, our sales person will get in touch with you as earliest as possible.<br><br>Regards,<br>CoTrav";

                requests.post(
                    'https://twilix.exotel.in/v1/Accounts/{exotel_sid}/Sms/send.json'.format(exotel_sid=exotel_sid),
                    auth=(exotel_key, exotel_token),
                    data={
                        'From': sender_id,
                        'To': Contact_no,
                        'Body': sms_body
                    })

            messages.success(request, "Lead Created Successfully..!")
            return redirect('lead-list')
        else:
            messages.error(request, "Lead Status Not Created ..!")
            form = LeadUpdateForm(request.POST or None)
            return render(request, template_name, {'form': form, 'form_title': 'Update Lead'})
    else:
        form = LeadGenerationModelForm()

    return render(request, template_name, {'form':form , 'form_title': 'Create New Lead'})




@login_required(login_url='/agents/login')
def lead_delete(request, pk, template_name='landing/leadgeneration_confirm_delete.html'):
    lead = get_object_or_404(Leadgeneration, pk=pk)
    if request.method=='POST':
        lead.delete()
        return redirect('lead-list')
    return render(request, template_name, {'object':lead})


@login_required(login_url='/agents/login')
def lead_assigned(request, template_name='landing/leadgeneration_list.html'):
    if request.method=='POST':
        lead_id = request.POST.get('lead_id', '')
        agent_id = request.POST.get('agent_id', '')
        ag_name = request.POST.get('ag_name', '')
        agent_email = request.POST.get('agent_email', '')
        contact_no = request.POST.get('contact_no', '')
        Contact_Name = request.POST.get('Contact_Name', '')
        Company_Name = request.POST.get('Company_Name', '')
        Contact_Number = request.POST.get('Contact_Number', '')
        Contact_Email = request.POST.get('Contact_Email', '')
        Company_Location = request.POST.get('Company_Location', '')
        message = "New Lead has been assigned to your queue"
        Leadgeneration.objects.filter(pk=lead_id).update(Assigned_Sales_Person=agent_id,Status='Assigned')
        signup = Lead_Status_Change_Email(message, 'Assigned', agent_email, "User",Company_Name,Contact_Name,Contact_Email,Contact_Number,Company_Location)
        resp1 = signup.send_email()

        message1 = "A Relationship Manager from Cotrav Team has been assigned to you to solve all your queries. Please find the details below."
        signup1 = Lead_Email_To_Company_assign_agent(message1, agent_email, ag_name, contact_no, Contact_Name, Contact_Email, Contact_Number)
        resp2 = signup1.send_email()


        return redirect('lead-list')
    return render(request, template_name, {})


@login_required(login_url='/agents/login')
def lead_doc_delete(request, pk ):
    lead = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        lead.delete()

    return HttpResponse('deleted')





##########################


@login_required(login_url='/agents/login')
class LeadListView(generic.ListView):
    model = Leadgeneration
    queryset = Leadgeneration.objects.all()


class LeadCreate(SuccessMessageMixin , CreateView):
    model = Leadgeneration
    form_class = LeadGenerationModelForm
    #fields = '__all__'
    initial = {'Status': 'Lead Created'}
    success_message = "Lead Created Successfully"
    success_url = '/agents/lead/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        print(self.object)
        cmt = LeadComments()
        self.object = self.object.save()
        id = self.object.latest('id')
        cmt.lead_id = id
        cmt.comment = "testing comment"
        cmt.save()
        #LeadComments.objects.create(cotrav_lead_generation_module_id = self.object)
        #LeadComments.save()
        return redirect('/agents/lead/')


class LeadUpdate(SuccessMessageMixin , UpdateView):
    model = Leadgeneration
    form_class = LeadUpdateForm
    success_message = "Lead Updated Successfully"
    #fields = ['Contact_Name', 'Company_Name', 'Contact_Number', 'Contact_Email','Company_Location','Assigned_Sales_Person','Status','Comments']
    initial = {'Status': 'Assigned'}
    success_url = '/agents/lead/'

class LeadDelete(SuccessMessageMixin , DeleteView):
    model = Leadgeneration
    #messages.add_message(self.request, messages.INFO, 'Hello world.')
    success_message = "Lead Deleated Successfully"
    success_url = reverse_lazy('leads')
    #success_url = '/agents/lead/'
