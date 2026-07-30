from django.db import models
from .leads import *
from .user import User
from django.conf import settings
from .delete_base_model import SafeDeleteModel




class CallDetails(SafeDeleteModel):
    # --- Identifiers ---
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='calls')
    telecaller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='made_calls')

    # --- Call Status & Outcomes ---
    # connection_status: Answered, No Answer, Busy, Switched Off
    connection_status = models.CharField(max_length=50) 
    
    # conversation_outcome: Interested, Not Interested, Busy - Call Back, Wrong Number
    stage = models.ForeignKey(Stages,  blank=True,on_delete=models.SET_NULL, null=True, related_name='select_tag')
    
    # key_objective: Degree inquiry, Course Fee details, Location inquiry
    select_tag = models.ForeignKey(SelectTag, blank=True,on_delete=models.SET_NULL, null=True, related_name='stage')

    # --- Content & Recording ---
    conversation_summary = models.TextField(null=True, blank=True) # Ithu dhaan 'Call Notes'
    upload_recording = models.FileField(upload_to='call_recordings/', null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    called_at = models.DateTimeField(auto_now_add=True)

    # --- Future Action ---
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return f"Call with {self.lead.full_name} by {self.telecaller.first_name}"
    
    class Meta:
        db_table = 'telecalling_call_details'
        
        