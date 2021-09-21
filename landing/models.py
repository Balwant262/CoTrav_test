from django.db import models
from landing.utils import get_choice
from django.contrib.contenttypes.fields import GenericRelation

from Common.models import Corporate_Agent
abc = get_choice()

sts = (
    ('','Select Lead Status'),
    ('Lead Created','Lead Created'),
    ('Assigned','Assigned'),
    ('In-Process','In-Process'),
    ('Closed-Win','Closed-Win'),
    ('Closed-Lost','Closed-Lost'),
)

source = (
    ('','Select Lead Communication'),
    ('Call','Call'),
    ('Email','Email'),
    ('Existing Customer','Existing Customer'),
    ('Campaign','Campaign'),
    ('Sign Up','Sign Up'),
    ('Contact Us','Contact Us'),
    ('Facebook','Facebook'),
    ('Twitter','Twitter'),
    ('LinkedIn','LinkedIn'),
    ('Other','Other'),

)

communication = (
    ('', 'Select Lead Communication'),
    ('SMS','SMS'),
    ('Email','Email'),
    ('Call', 'Call'),
    ('In-Person', 'In-Person'),
)

class ManagementFee(models.Model):
    corporate_id = models.IntegerField()
    service_fees_type_id = models.IntegerField()
    service_fees_type_value = models.IntegerField()
    service_fees_type = models.IntegerField()
    is_deleted = models.IntegerField()
    class Meta:
        db_table = "corporate_management_fees"


# Create your models here.
class Leadgeneration(models.Model):
    Contact_Name = models.CharField(max_length=255)
    Company_Name = models.CharField(max_length=255)
    Contact_Number = models.CharField(max_length=30)
    Contact_Email = models.EmailField(max_length=255)
    Company_Location = models.CharField(max_length=255)
    Contact_Address = models.CharField(max_length=255)
    Contact_Address_Line2 = models.CharField(max_length=255)
    Contact_Address_Line3 = models.CharField(max_length=255)
    Company_Website = models.CharField(max_length=255)
    Message = models.CharField(max_length=255)
    Assigned_Sales_Person = models.IntegerField()
    Status = models.CharField(max_length=255,choices=sts,)
    Lead_Source = models.CharField(max_length=255,choices=source,)
    Attachments = models.ImageField(upload_to='photos')
    Lead_Communication = models.CharField(max_length=255,choices=communication,)
    Comments = models.TextField(max_length=255)
    Hear_About_Us = models.TextField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "cotrav_lead_generation_module"



class LeadComments(models.Model):
     lead = models.ForeignKey(Leadgeneration, on_delete=models.CASCADE , related_name='lead_id')
     comment = models.CharField(max_length=255)
     created_by = models.ForeignKey(Corporate_Agent, on_delete=models.CASCADE , related_name='created_by')
     created_at = models.CharField(max_length=255)
     class Meta:
         db_table = "lead_comments"


class LeadLog(models.Model):
    lead_id = models.IntegerField()
    status_action = models.CharField(max_length=255)
    action_initiated_by = models.IntegerField()
    comment = models.CharField(max_length=255)
    class Meta:
        db_table = "lead_action_log"



class Document(models.Model):
    #upload_by = models.ForeignKey('auth.User', related_name='uploaded_documents')
    upload_by = models.ForeignKey('Leadgeneration', on_delete=models.CASCADE )
    datestamp = models.DateTimeField(auto_now_add=True)
    document = models.FileField(upload_to='uploads/')
    doc_name = models.CharField(max_length=255)
    class Meta:
        db_table = "document"

        

    

         


