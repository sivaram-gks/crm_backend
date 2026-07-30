from django.db import models
from .leads import Lead
from .call_details import CallDetails
from django.conf import settings
from .delete_base_model import SafeDeleteModel

class FollowUp(SafeDeleteModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='followups')
    telecaller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    scheduled_at = models.DateTimeField()       # எப்ப பண்ணணும்
    attended_at = models.DateTimeField(null=True, blank=True)  # எப்ப பண்ணோம்
    
    is_attended = models.BooleanField(default=False)  # பண்ணோமா இல்லையா
    
    # எந்த call-ல இருந்து follow up create ஆச்சு
    created_from_call = models.ForeignKey(
        CallDetails, null=True, blank=True,
        on_delete=models.SET_NULL, 
        related_name='scheduled_followups'
    )
    
    # Follow up attend பண்ணும்போது எந்த call பண்ணோம்
    attended_via_call = models.ForeignKey(
        CallDetails, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='attended_followups'
    )
    
    notes = models.TextField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)
    
    class Meta:
        db_table="telecalling_follow_up"
        
        
 