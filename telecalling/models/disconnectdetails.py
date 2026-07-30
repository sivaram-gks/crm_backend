from django.db import models
from .call_details import CallDetails
from .delete_base_model import SafeDeleteModel

class DisconnectedDetails(SafeDeleteModel):
    # --- FK to Main Call ---
    # Oru call attempt disconnect aana, athoda context-a inga store pannuvom
    call = models.OneToOneField(CallDetails, on_delete=models.CASCADE, related_name='disconnection_info')
    
    # --- Disconnection Reasons ---
    select_tag = models.ForeignKey('DisconnectStage',on_delete=models.SET_NULL, null=True, related_name='disconnect')
    other_reason=models.TextField(null=True,blank=True,default=None)
    # --- Retry Strategy ---
    retry_notes = models.TextField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return f"Disconnected: {self.call.lead.full_name} ({self.select_tag})"
    
    class Meta:
        db_table = 'telecalling_disconnect_details'
        
        
        



class DisconnectStage(SafeDeleteModel):
    name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return str(self.name)
    class Meta:
        db_table = 'telecalling_disconnect_stage'