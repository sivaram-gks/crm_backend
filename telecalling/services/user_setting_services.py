from rest_framework.exceptions import APIException
from ..models import *
from django.contrib.auth import get_user_model
from ..services.query_services import exec_raw_sql
from rest_framework.exceptions import APIException, NotFound
from .notification_services import *
from rest_framework.decorators import authentication_classes, permission_classes



# ─── GET all ─────────────────────────────────────────────────────


def get_all_settings_service(user,**data):
    try:

        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")
        
        try:
            notif =exec_raw_sql("D_FETCH_GET_USER_SETTINGS",{"id":user.id})
        except UserSettings.DoesNotExist:
            UserSettings.objects.create(user=user)
            notif =exec_raw_sql("D_FETCH_GET_USER_SETTINGS",{"id":user.id})
            
        print(notif)
            
        return  notif

    except Exception as e:
        raise APIException(detail=str(e))

# User = get_user_model()

# ─── Notification ─────────────────────────────────────────────────

def update_notification_service(user, **data):
    try:
        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")

        notifiy = UserSettings.objects.filter(user_id=user.id).first()

        if data.get("follow_up_reminders") is not None:
            notifiy.follow_up_reminders = data.get("follow_up_reminders")
        if data.get("sound_alerts") is not None:
            notifiy.sound_alerts = data.get("sound_alerts")
        if data.get("reminder_time") is not None:
            notifiy.reminder_time = data.get("reminder_time")
        if data.get("notify_new_lead_assigned") is not None:
            notifiy.notify_new_lead_assigned = data.get("notify_new_lead_assigned")
        if data.get("notify_missed_followups") is not None:
            notifiy.notify_missed_followups = data.get("notify_missed_followups")
        if data.get("notify_reassigned_leads") is not None:
            notifiy.notify_reassigned_leads = data.get("notify_reassigned_leads")
        notifiy.save()

        # ✅ .values() — dict ஆ return பண்ணும், JSON ஆகும்
        return UserSettings.objects.filter(user_id=user.id).values(
            "follow_up_reminders",
            "sound_alerts", 
            "reminder_time",
            "notify_new_lead",
            "notify_missed_followups",
            "notify_reassigned_leads",
        ).first()

    except Exception as e:
        raise APIException(detail=str(e))
        



# ─── Follow-up ────────────────────────────────────────────────────
def update_followup_service(user,**data):
    try:
        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")
        print(user.id)
        
        notifiy = UserSettings.objects.filter(user_id=user.id).first()

        if data.get("auto_suggestion_followup_date") is not None:
            notifiy.auto_suggest_followup_date = data.get("auto_suggestion_followup_date")
        if data.get("auto_manual_followup_edit") is not None:
            notifiy.auto_manual_followup_edit = data.get("auto_manual_followup_edit")
        if data.get("followup_mandatory_before_close") is not None:
            notifiy.mandatory_followup_before_close = data.get("followup_mandatory_before_close")
        if data.get("mark_followup_as_completed") is not None:
            notifiy.mark_followup_completed = data.get("mark_followup_as_completed")
        notifiy.save()
        
        
        return "follow up setting update successfully"
    except Exception as e:
        raise APIException(detail=str(e))


# ─── Calling ──────────────────────────────────────────────────────
def update_caller_service(user,**data):
    try:
        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")
        
        notifiy = UserSettings.objects.filter(user_id=user.id).first()

        if data.get("enable_click_to_call") is not None:
            notifiy.enable_click_to_call = data.get("enable_click_to_call")
        if data.get("make_call_notes_mandatory") is not None:
            notifiy.make_call_notes_mandatory = data.get("make_call_notes_mandatory")
        if data.get("default_call_outcome") is not None:
            notifiy.default_call_outcome = data.get("default_call_outcome")

        notifiy.save()
        
        
        return "call setting update successfully"
    except Exception as e:
        raise APIException(detail=str(e))


# ─── Messaging ────────────────────────────────────────────────────
def update_messaging_service(user, **data):
    try:
        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")
        
        notifiy = UserSettings.objects.filter(user_id=user.id).first()

        if data.get("enable_message_templates") is not None:
            notifiy.enable_message_templates = data.get("enable_message_templates")
        if data.get("allow_custom_templates") is not None:
            notifiy.allow_custom_templates = data.get("allow_custom_templates")
        if data.get("auto_send_messages") is not None:
            notifiy.auto_send_messages = data.get("auto_send_messages")

        notifiy.save()
        
        
        return "message setting update successfully"

    except Exception as e:
        raise APIException(detail=str(e))


# ─── Notes ────────────────────────────────────────────────────────
def update_notes_service(user, **data):
    try:
        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")
        
        notifiy = UserSettings.objects.filter(user_id=user.id).first()

        if data.get("make_notes_mandatory") is not None:
            notifiy.make_notes_mandatory = data.get("make_notes_mandatory")
        if data.get("enable_quick_note_templates") is not None:
            notifiy.enable_quick_note_templates = data.get("enable_quick_note_templates")

        notifiy.save()
        
        
        return "notes setting update successfully"

    except Exception as e:
        raise APIException(detail=str(e))


# ─── Lead Preference ──────────────────────────────────────────────
def update_lead_preference_service(user, **data):
    try:
        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")
        
        notifiy = UserSettings.objects.filter(user_id=user.id).first()

        if data.get("default_view") is not None:
            notifiy.default_lead_view = data.get("default_view")
        if data.get("sort_leads_by") is not None:
            notifiy.sort_leads_by = data.get("sort_leads_by")


        notifiy.save()
        
        
        return "lead view setting update successfully"

    except Exception as e:
        raise APIException(detail=str(e))


# ─── Security ─────────────────────────────────────────────────────
def update_security_service(user, **data):
    try:
        if not user or not user.is_authenticated:
            raise APIException(detail="Authentication required.")
        
        notifiy = UserSettings.objects.filter(user_id=user.id).first()

        if data.get("two_factor_authentication") is not None:
            notifiy.two_factor_auth_enabled = data.get("two_factor_authentication")


        notifiy.save()
        
        
        return "message setting update successfully"

    except Exception as e:
        raise APIException(detail=str(e))