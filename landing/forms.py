from django import forms
from landing.models import Leadgeneration
from Common.models import Corporate_Agent
from landing.utils import get_choice
from django.core.validators import DecimalValidator

abc = get_choice()


sts = (
    ('','Select Status'),
    ('Lead Created','Lead Created'),
    ('Assigned','Assigned'),
    ('In-Process','In-Process'),
    ('Closed-Win','Closed-Win'),
    ('Closed-Lost','Closed-Lost'),
)

source = (
    ('','Select Source'),
    ('Call','Call'),
    ('Email','Email'),
    ('Existing Customer','Existing Customer'),
    ('Campaign','Campaign'),
    ('Sign Up','Sign Up'),
    ('Contact Us','Contact Us'),
    ('Facebook','Facebook'),
    ('Twitter','Twitter'),
    ('LinkedIn','LinkedIn'),
    ('Bulk Upload','Bulk Upload'),
    ('Other','Other'),
)

communication = (
    ('','Select Communication'),
    ('SMS', 'SMS'),
    ('Email', 'Email'),
    ('Call', 'Call'),
    ('In-Person', 'In-Person')
)

hear_about = (
    ('','Select Communication'),
    ('SMS', 'SMS'),
    ('Email', 'Email'),
    ('Call', 'Call'),
    ('In-Person', 'In-Person')
)


class Corporate_Agent_Form(forms.ModelForm):

    class Meta:
        model = Corporate_Agent
        fields = ['user_name']




class LeadGenerationModelForm(forms.ModelForm):
    Contact_Name = forms.CharField(label='Contact_Name', max_length=255 , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Contact Name"}))
    Company_Name = forms.CharField(label='Company_Name', max_length=255 , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Company Name"}))
    Contact_Number = forms.CharField(label='Contact_Number', max_length=255 , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Contact Number"}))
    Contact_Email = forms.EmailField(label='Contact_Email', max_length=255 , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Contact Email"}))
    Company_Location = forms.CharField(label='Company_Location', max_length=255 , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'id':"company_location",'placeholder':"Company Location"}))
    Contact_Address = forms.CharField(label='Contact_Address', max_length=255 , required=False , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Address Line 1"}))
    Contact_Address_Line2 = forms.CharField(label='Contact_Address_Line2', max_length=255 , required=False , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Address Line 2"}))
    Contact_Address_Line3 = forms.CharField(label='Contact_Address_Line2', max_length=255 , required=False , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Address Line 3"}))
    Company_Website = forms.CharField(label='Company_Website', max_length=255 , required=False , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Company Website"}))
    Message = forms.CharField(label='Message', max_length=255 , widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Message"}))
    Assigned_Sales_Person = forms.CharField(max_length=255 ,widget = forms.Select( choices=abc,attrs={'class': "form-control col-sm-8 myselect",'id':"sales_person"}),)
    Status = forms.CharField(label='Status' , max_length=255 , widget = forms.Select(choices=sts,attrs={'class': "form-control col-sm-8 myselect",'id':"status"}),)
    Lead_Source = forms.CharField(label='Lead_Source', max_length=255 , widget = forms.Select(choices=source,attrs={'class': "form-control col-sm-8 myselect",'id':"lead_source"}),)
    Attachments = forms.FileField(required=False)
    Lead_Communication = forms.CharField(label='Lead_Communication', max_length=255 , required=False , widget = forms.Select(choices=communication,attrs={'class': "form-control col-sm-8 myselect",'id':"lead_communication"}),)
    Hear_About_Us = forms.CharField(label='Hear_About_Us', max_length=255 , required=False , widget = forms.TextInput(attrs={'class': "form-control col-sm-8",'id':"Hear_About_Us"}),)
    Comments = forms.CharField(label='Comments', max_length=255 , widget=forms.Textarea(attrs={'class': "form-control col-sm-8"}))

    def __init__(self,*args, **kwargs):
        super(LeadGenerationModelForm, self).__init__(*args, **kwargs)
        pqr = get_choice()
        self.fields['Assigned_Sales_Person'] = forms.CharField(max_length=255, widget=forms.Select(choices=pqr, attrs={
            'class': "form-control col-sm-8 myselect", 'id': "sales_person"}), )

    def clean(self):
        cleaned_data = super().clean()
        Assigned_Sales_Person = cleaned_data.get("Assigned_Sales_Person")

    class Meta:
        model = Leadgeneration
        fields = "__all__"




class LeadUpdateForm(forms.ModelForm):
    Contact_Name = forms.CharField(label='Contact_Name', max_length=255,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Contact Name"}))
    Company_Name = forms.CharField(label='Company_Name', max_length=255,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Company Name"}))
    Contact_Number = forms.CharField(label='Contact_Number', max_length=255,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Contact Number"}))
    Contact_Email = forms.EmailField(label='Contact_Email', max_length=255,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Contact Email"}))
    Company_Location = forms.CharField(label='Company_Location', max_length=255,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'id':"company_location"}))
    Contact_Address = forms.CharField(label='Contact_Address', max_length=255, required=False,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Address Line 1"}))
    Contact_Address_Line2 = forms.CharField(label='Contact_Address_Line2', max_length=255, required=False,widget=forms.TextInput(attrs={'class': "form-control col-sm-8", 'placeholder': "Address Line 2"}))
    Contact_Address_Line3 = forms.CharField(label='Contact_Address_Line2', max_length=255, required=False, widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder': "Address Line 3"}))
    Company_Website = forms.CharField(label='Company_Website', max_length=255, required=False,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Company Website"}))
    Message = forms.CharField(label='Message', max_length=255,widget=forms.TextInput(attrs={'class': "form-control col-sm-8",'placeholder':"Message"}))
    #Assigned_Sales_Person = forms.ModelChoiceField()
    #Assigned_Sales_Person = forms.ModelChoiceField(required=False, widget=forms.Select, queryset= get_choice() )
    #Assigned_Sales_Person = forms.CharField(max_length=255, widget=forms.Select(choices=abc, attrs={'class': "form-control col-sm-8 myselect", 'id': "sales_person"}), )
    Assigned_Sales_Person = forms.CharField(max_length=255 ,widget = forms.Select( choices=abc,attrs={'class': "form-control col-sm-8 myselect",'id':"sales_person"}),)

    #Assigned_Sales_Person = forms.ChoiceField(choices=[(agent.id, agent.user_name) for agent in Corporate_Agent.objects.all()])

    Status = forms.CharField(label='Status', max_length=255,widget=forms.Select(choices=sts, attrs={'class': "form-control col-sm-8 myselect",'id':"status"}), )
    Lead_Source = forms.CharField(label='Lead_Source', max_length=255,widget = forms.Select(choices=source,attrs={'class': "form-control col-sm-8 myselect",'id':"lead_source"}),)
    Attachments = forms.FileField(required=False)
    Lead_Communication = forms.CharField(label='Lead_Communication', max_length=255, required=False,widget = forms.Select(choices=communication,attrs={'class': "form-control col-sm-8 myselect",'id':"lead_communication"}),)
    Hear_About_Us = forms.CharField(label='Hear_About_Us', max_length=255, required=False,widget = forms.TextInput(attrs={'class': "form-control col-sm-8",'id':"Hear_About_Us"}),)
    Comments = forms.CharField(label='Comments', max_length=255,widget=forms.Textarea(attrs={'class': "form-control col-sm-8"}))

    def __init__(self,*args, **kwargs):
        super(LeadUpdateForm, self).__init__(*args, **kwargs)
        pqr = get_choice()
        self.fields['Assigned_Sales_Person'] = forms.CharField(max_length=255, widget=forms.Select(choices=pqr, attrs={
            'class': "form-control col-sm-8 myselect", 'id': "sales_person"}), )

    def clean(self):
        cleaned_data = super().clean()
        Assigned_Sales_Person = cleaned_data.get("Assigned_Sales_Person")


    class Meta:
        model = Leadgeneration
        fields = "__all__"



        
