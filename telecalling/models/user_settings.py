# models.py
from django.db import models
from django.conf import settings
from .delete_base_model import SafeDeleteModel
# from django.contrib.auth import get_user_model

# User = get_user_model()

class UserSettings(SafeDeleteModel):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')

    # ── Notifications (முன்னாடியே இருக்கு) ──────────────────
    follow_up_reminders        = models.BooleanField(default=True)
    reminder_time              = models.CharField(max_length=50, default=10)
    sound_alerts               = models.BooleanField(default=False)
    notify_new_lead            = models.BooleanField(default=True)
    notify_missed_followups    = models.BooleanField(default=True)
    notify_reassigned_leads    = models.BooleanField(default=True)

    # ── Follow-ups (முன்னாடியே இருக்கு) ─────────────────────
    auto_suggest_followup_date      = models.BooleanField(default=True)
    auto_manual_followup_edit       = models.BooleanField(default=False)
    mandatory_followup_before_close = models.BooleanField(default=False)
    mark_followup_completed         = models.BooleanField(default=False)

    # ── Calling (புதுசு) ──────────────────────────────────────
    enable_click_to_call   = models.BooleanField(default=False)
    make_call_notes_mandatory = models.BooleanField(default=False)
    default_call_outcome   = models.CharField(max_length=50 )

    # ── Notes & Templates (முன்னாடியே இருக்கு) ───────────────
    make_notes_mandatory        = models.BooleanField(default=False)
    enable_quick_note_templates = models.BooleanField(default=True)

    # ── Messaging (புதுசு) ────────────────────────────────────
    enable_message_templates = models.BooleanField(default=False)
    allow_custom_templates   = models.BooleanField(default=False)
    auto_send_messages       = models.BooleanField(default=False)
    default_template         = models.ForeignKey(
        'MessageTemplate',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='default_for_users'
    )


    default_lead_view = models.CharField(max_length=20)
    sort_leads_by     = models.CharField(max_length=20)

    # ── Security (புதுசு) ─────────────────────────────────────
    two_factor_auth_enabled = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)


    def __str__(self):
        return f"{self.user.email} — Settings"

    class Meta:
        db_table="telecalling_user_settings"

# Messaging templates-க்கு தனி model
class MessageTemplate(SafeDeleteModel):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_templates')
    name    = models.CharField(max_length=100)
    content = models.TextField()
    is_custom = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
    class Meta:
        db_table="telecalling_message_tmp"
        
        
        
class UserSecurity(SafeDeleteModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    two_factor_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)  # secret key store
    is_verified = models.BooleanField(default=False)  # setup complete ஆச்சா

    def __str__(self):
        return f"{self.user.username} - 2FA: {self.two_factor_enabled}"