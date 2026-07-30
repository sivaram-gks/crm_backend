from django.db import models
from .leads import *
from .user import User
from django.conf import settings
from .delete_base_model import SafeDeleteModel




class DailyReport(SafeDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField(null=True)
    
    # Today Activity
    total_leads = models.IntegerField(default=0)
    new_leads = models.IntegerField(default=0)
    call_spoked = models.IntegerField(default=0)
    not_respond = models.IntegerField(default=0)
    follow_up = models.IntegerField(default=0)
    pending_follow_up = models.IntegerField(default=0)
    partial_payment = models.IntegerField(default=0)
    full_payment = models.IntegerField(default=0)
    
    # Manual Entry
    total_expected_conversion = models.IntegerField(default=0)
    actual_expected_conversion = models.IntegerField(default=0)
    notes_for_manager = models.TextField(blank=True, null=True)
    
    # Status
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
        db_table = "telecalling_daily_report"
    
    def __str__(self):
        return f"{self.user.username} - {self.report_date}"
        
        