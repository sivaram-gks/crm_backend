from django.db import models
from telecalling.models import Lead, User

class AdminLeadReassignHistory(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='reassign_history')
    previous_telecaller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reassigned_from_history')
    new_telecaller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reassigned_to_history')
    reassigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reassigned_by_history')
    
    attended_calls_count = models.IntegerField(default=0)
    previous_call_history = models.JSONField(default=list, blank=True, null=True)
    
    reassigned_reason = models.TextField(null=True, blank=True)
    reassigned_at = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=50, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=50, null=True)

    def __str__(self):
        lead_name = self.lead.full_name if self.lead else "Unknown"
        return f"Reassignment of Lead {lead_name} (ID: {self.lead_id})"

    class Meta:
        db_table = 'adm_lead_reassign_history'
        ordering = ['-reassigned_at']
