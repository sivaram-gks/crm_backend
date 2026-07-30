from django.db import models
from .follow_up import FollowUp
from .leads import Lead
from .paymentinfo import PaymentInfo
from .delete_base_model import SafeDeleteModel
from django.conf import settings

class Notification(SafeDeleteModel):

    title = models.CharField(max_length=100)

    message = models.CharField(max_length=255)

    follow_up = models.ForeignKey(
        FollowUp,
        on_delete=models.CASCADE,
        null=True
    )
    scheduled_remainder=models.DateTimeField(null=True)
    
    
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    payment=models.ForeignKey(
        PaymentInfo,
        on_delete=models.CASCADE,
        null=True
    )
    
    # is_missed = models.BooleanField(default=False,null=True)
    retry_count = models.IntegerField(default=0,null=True)


    notification_type=models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.CharField(max_length=50)

    updated_at = models.DateTimeField(auto_now=True)

    updated_by = models.CharField(max_length=50)

    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table='telecalling_notifications'
    
    
    
    
           
class MissedFollowUpHistory(SafeDeleteModel):

    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='missed_logs'
    )

    follow_up = models.ForeignKey(
        FollowUp,
        on_delete=models.CASCADE
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    retry_count = models.IntegerField(default=1)

    sent_at = models.DateTimeField(auto_now_add=True)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "telecalling_missed_followup_history"

    def __str__(self):
        return f"{self.lead.full_name} - Retry {self.retry_count}"