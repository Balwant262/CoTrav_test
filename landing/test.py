from django.shortcuts import render , redirect , get_object_or_404
from landing.forms import LeadGenerationModelForm , LeadUpdateForm

from django.views import generic

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.db.models.signals import post_save
from django.dispatch import receiver

from landing.models import Leadgeneration , LeadComments , LeadLog
from Common.models import Corporate_Agent
from landing.cotrav_messeging import LeadGenerationEmail

from django.contrib.auth.decorators import login_required

from django.contrib.messages.views import SuccessMessageMixin

from django.http import HttpResponse , HttpResponseRedirect

from django.views.generic.edit import ModelFormMixin

from django.contrib import messages

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import os

from django.core.files.storage import default_storage


from landing.models import Document



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

    if(created) :
        print ("create call")
        message = "New Lead Generated with id " + str(instance.id) + " and status Lead Created "
        status = "Lead Created"
        lead_create = LeadGenerationEmail(corporate_name,corporate_location,contact_person_name,contact_person_no,contact_person_email,message,status)

        resp1 = lead_create.lead_create_send_email()
        print(resp1)
    else:
        print("update call")
        print(instance.id)
        ag_id = instance.Assigned_Sales_Person
        ag_email = Corporate_Agent.objects.get(id=ag_id).get_email_id()

        message = "Lead with id " + str(instance.id) + " is updated and assigned to agent " + ag_email
        status = "Assigned"
        lead_updated = LeadGenerationEmail(corporate_name,corporate_location,contact_person_name,contact_person_no,contact_person_email,message,status)
        agent = ag_email
        resp1 = lead_updated.lead_updated_send_email(agent)
        print(resp1)


@login_required(login_url='/agents/login')
def leads(request):

    leads = Leadgeneration.objects.raw('SELECT l.*,ca.user_name FROM cotrav_lead_generation_module l LEFT JOIN corporate_agents ca ON l.Assigned_Sales_Person = ca.id WHERE 1')

    return render(request,'landing/leadgeneration_list.html',{'leads':leads})



@require_POST
def file_upload(request,lead_id):
    file_up = request.FILES['Attachments']
    save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', str(file_up))
    path = default_storage.save(save_path, request.FILES['Attachments'])

    lead = Leadgeneration.objects.get(id=lead_id)
    document = Document.objects.create(document=path, upload_by=lead)
    return JsonResponse({'document': document.id})




@login_required(login_url='/agents/login')
def lead_update(request, pk, template_name='landing/leadgeneration_form.html'):
    lead = get_object_or_404(Leadgeneration, pk=pk)
    comments = LeadComments.objects.filter(lead_id=pk)
    if request.method == 'POST':

        form = LeadUpdateForm(request.POST or None,request.FILES, instance=lead , initial={'Comments': ''})


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
            cmt.created_by = request.user.id
            cmt.save()
            log = LeadLog()
            log.lead_id = edit_lead.pk
            log.comment = new_comment
            log.status_action = status_action
            log.action_initiated_by = request.user.id
            log.save()
            return redirect('lead-list')
    else:

        form = LeadUpdateForm(request.POST or None, instance=lead , initial={'Comments': ''})

    return render(request, template_name, {'form':form,'comments':comments , 'form_title': 'Update Lead'})



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
            cmt.created_by = request.user.id
            cmt.save()
            log = LeadLog()
            log.lead_id = new_lead.pk
            log.comment = new_comment
            log.status_action = status_action
            log.action_initiated_by = request.user.id
            log.save()

            return redirect('lead-list')
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
    success_url = '/Agents/lead/'

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
        return redirect('/Agents/lead/')


class LeadUpdate(SuccessMessageMixin , UpdateView):
    model = Leadgeneration
    form_class = LeadUpdateForm
    success_message = "Lead Updated Successfully"
    #fields = ['Contact_Name', 'Company_Name', 'Contact_Number', 'Contact_Email','Company_Location','Assigned_Sales_Person','Status','Comments']
    initial = {'Status': 'Assigned'}
    success_url = '/Agents/lead/'

class LeadDelete(SuccessMessageMixin , DeleteView):
    model = Leadgeneration
    #messages.add_message(self.request, messages.INFO, 'Hello world.')
    success_message = "Lead Deleated Successfully"
    success_url = reverse_lazy('leads')
    #success_url = '/Agents/lead/'
