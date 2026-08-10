from django.db import models
from telecalling.models import Lead, SelectTag, User


class AdminLossActionLog(models.Model):
    lead = models.ForeignKey(
        Lead, 
        on_delete=models.CASCADE, 
        related_name='admin_loss_action_logs'
    )
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='loss_action_logs'
    )
    action_type = models.CharField(max_length=50)
    previous_assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='prev_loss_reassignments'
    )
    new_assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='new_loss_reassignments'
    )
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'adm_loss_action_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.lead.full_name} - {str(self.action_type).upper()} by {self.admin_user}"


class AdminApprovedLossLead(models.Model):
    
    lead = models.OneToOneField(
        Lead, 
        on_delete=models.CASCADE, 
        related_name='approved_loss_record'
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='approved_loss_leads'
    )
    main_reason = models.ForeignKey(
        SelectTag, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    final_remarks = models.TextField(null=True, blank=True)
    can_retarget = models.BooleanField(default=True)
    approved_at = models.DateTimeField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'adm_approved_loss_lead'
        ordering = ['-approved_at']

    def __str__(self):
        return f"Permanent Loss: {self.lead.full_name} | Reason: {self.main_reason}"
