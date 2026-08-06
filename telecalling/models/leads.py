from django.conf import settings
from .delete_base_model import SafeDeleteModel
from django.db import models
from django.contrib.auth.models import *
from .courses import *

        

class Lead(SafeDeleteModel):
    # --- Basic Info (Initial stage-le kidaikkum) ---
    full_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    alternative_mobile = models.CharField(max_length=15, null=True, blank=True)

    # --- Education & Experience (Telecaller fill panna vendiyavai) ---
    # Ippo ithu ellame optional, initial save-la error varathu.
    location = models.CharField(max_length=100, null=True, blank=True)
    education = models.ForeignKey('Education',on_delete=models.SET_NULL, null=True, related_name='course')
    passed_out_year = models.IntegerField(null=True, blank=True)
    experience = models.CharField(max_length=50, null=True, blank=True)

    # --- Source Info ---
    lead_source =models.ForeignKey('LeadSource',on_delete=models.SET_NULL, null=True, related_name='lead_source')
    campaign= models.ForeignKey('CampaignName',on_delete=models.SET_NULL, null=True, related_name='campaign')
    enquiry_date = models.DateTimeField(auto_now_add=True)
    
    # --- Course Details (Initial stage-la null-a irukalam) ---
    course_plan = models.ForeignKey(CoursePlan,on_delete=models.SET_NULL, null=True, related_name='course_plan')
    course_name =models.ForeignKey(CourseName,on_delete=models.SET_NULL, null=True, related_name='course_name')
    course_timing= models.ForeignKey(CourseTiming,on_delete=models.SET_NULL, null=True, related_name='course_timing')
    preferred_timing = models.ForeignKey('PreferredTime',on_delete=models.SET_NULL, null=True, related_name='preferred_timing')

    # --- Status & Pipeline ---
    current_status = models.CharField(max_length=50, default="working")
    pipeline_stage = models.ForeignKey('PipelineStage',on_delete=models.SET_NULL, null=True, related_name='pipeline_stage')
    
    priority = models.ForeignKey('Priority',on_delete=models.SET_NULL, null=True, related_name='priority')

    # --- Assignment & Dates ---
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='leads')
    course=models.ForeignKey(Course,on_delete=models.SET_NULL, null=True, related_name='course')
    # next_followup_date = models.DateTimeField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return f"{self.full_name} ({self.mobile_no})"
    class Meta:
        db_table = 'telecalling_lead'
        
   
        
class ReferalDetails(SafeDeleteModel):
    referal_name=models.CharField(max_length=100)
    referal_number=models.CharField(max_length=15)
    referal_lead=models.ForeignKey(Lead,on_delete=models.SET_NULL,null=True,related_name='leads')
    admin_check=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.referal_name)
    class Meta:
        db_table = 'telecalling_referal_details'
        
        
        
class LeadSource(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_lead_source'
        
        
        
class CampaignName(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_campaign_name'
        
        
class Priority(SafeDeleteModel):
    name=models.CharField(max_length=100)
    display_value=models.CharField(max_length=100, null=True, blank=True)
    pipeline_stage=models.ForeignKey('PipelineStage', on_delete=models.SET_NULL, null=True, blank=True)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_priority'
        
        
class PipelineStage(SafeDeleteModel):
    name=models.CharField(max_length=100)
    display_value=models.CharField(max_length=100, null=True, blank=True)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_pipeline_stage'
        
        
        
class PreferredTime(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_preferred_time'
        


class Education(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_education'
        
        
class Stages(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_stages'
        
        
        
class SelectTag(SafeDeleteModel):
    stages=models.ForeignKey(Stages,on_delete=models.SET_NULL,null=True,related_name="stages")
    name=models.CharField(max_length=100)
    display_value=models.CharField(max_length=100, null=True, blank=True)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_select_tag'
        
        
class FilterLeads(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_filter_leads'
        
        
class PaymentStatus(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_payment_status'
        
        
        
        
class FilterPayment(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_filter_payment'
        
        
class PaymentStage(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_payment_stage'
        
        
class AmountStage(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_amount_stage'
        
        
        

        
class FilterPipeline(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_filter_pipeline'