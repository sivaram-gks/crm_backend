from django.apps import apps
from huey.contrib.djhuey import task,periodic_task
from huey import crontab
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.conf import settings
from ..models import *
from ..services.query_services import *
from rest_framework.exceptions import APIException, NotFound
from datetime import datetime, timedelta
import zoneinfo
from django.utils import timezone
    # Get all active users (telecallers)
# from django.contrib.auth import get_user_model
# User = get_user_model()



# @task()
def send_notification_to_user(user_id, notification_type, title, message, 
                              follow_up_id=None, payment_id=None, lead_id=None, scheduled_remainder=None, data=None):
    """
    Send notification to a specific user via WebSocket and save to database
    """
    try:
        actual_lead_id = lead_id or (data.get('lead_id') if isinstance(data, dict) else None)
        
        # Save notification to database
        notification = Notification.objects.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            follow_up_id=follow_up_id,
            payment_id=payment_id,
            lead_id=actual_lead_id,
            scheduled_remainder=scheduled_remainder,
            is_read=False
        )
        
        # Send via WebSocket
        channel_layer = get_channel_layer()
        group_name = f"notif_user_{user_id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification',
                'notification_type': notification_type,
                'title': title,
                'message': message,
                'lead_id': actual_lead_id,
                'data': {
                    'id': notification.id,
                    'created_at': str(notification.created_at),
                    'follow_up_id': follow_up_id,
                    'payment_id': payment_id,
                    'lead_id': actual_lead_id,
                    'scheduled_remainder': str(scheduled_remainder) if scheduled_remainder else None,
                    **(data or {})
                }
            }
        )
        
        print(f"[OK] Notification sent to user {user_id}: {title}")
        return notification.id
        
    except Exception as e:
        print(f"[ERROR] Failed to send notification: {e}")
        return None
    
    
    
    
def send_lead_assigned_notification(lead_id, assigned_to_id, assigned_by_id=None):
    """
    Send notification when a lead is assigned
    """
    try:
        lead = Lead.objects.select_related('assigned_to', 'lead_source', 'course_name').get(id=lead_id)
        
        title = "New Lead Assigned"
        message = f"New lead assigned: {lead.full_name} (Mobile: {lead.mobile_no})"
        
        data = {
            'lead_id': lead.id,
            'lead_name': lead.full_name,
            'lead_mobile': lead.mobile_no,
            'lead_source': lead.lead_source.name if lead.lead_source else None,
            'created_at': str(lead.created_at)
        }
        
        if assigned_by_id:
            assigned_by = User.objects.get(id=assigned_by_id)
            message = f"Lead {lead.full_name} assigned to you by {assigned_by.get_full_name() or assigned_by.username}"
            data['assigned_by'] = assigned_by.get_full_name() or assigned_by.username
        
        return send_notification_to_user(
            assigned_to_id,
            'lead_notification',
            title,
            message,
            lead_id=lead.id,
            data=data
        )
        
    except Lead.DoesNotExist:
        print(f"[ERROR] Lead {lead_id} not found")
        return None
    except Exception as e:
        print(f"[ERROR] Error in lead assignment notification: {e}")
        return None





@task()
def send_lead_reassigned_notification(lead_id, new_assignee_id, old_assignee_id=None):
    """
    Send notification when a lead is reassigned
    """
    try:
        lead = Lead.objects.select_related('assigned_to').get(id=lead_id)
        
        data = {
            'lead_id': lead.id,
            'lead_name': lead.full_name,
            'lead_mobile': lead.mobile_no,
            'reassigned_at': str(lead.updated_at)
        }
        
        # Notify new assignee
        notification_id = send_notification_to_user(
            new_assignee_id,
            'lead_notification',
            'Lead Reassigned',
            f"Lead {lead.full_name} reassigned to you",
            data=data
        )
        
        # Optional: Notify old assignee
        if old_assignee_id and old_assignee_id != new_assignee_id:
            send_notification_to_user(
                old_assignee_id,
                'lead_notification',
                'Lead Reassigned',
                f"Lead {lead.full_name} has been reassigned to someone else",
                data={**data, 'status': 'removed'}
            )
        
        return notification_id
        
    except Lead.DoesNotExist:
        print(f"❌ Lead {lead_id} not found")
        return None
    except Exception as e:
        print(f"❌ Error in lead reassignment notification: {e}")
        return None
    
    






# ==========================================
# 1. SEND DAILY FOLLOW-UP COUNT NOTIFICATION
# ==========================================
@periodic_task(crontab(minute='00', hour='10'))  # Every day at 9 AM
def send_daily_followup_count():
    """
    Send daily follow-up count notification to all telecallers at 9 AM
    """
    ist = zoneinfo.ZoneInfo('Asia/Kolkata')
    today = timezone.now().astimezone(ist).date()
    tomorrow = today + timedelta(days=1)
    

    
    users = User.objects.filter(is_active=True, is_staff=False)
    
    count = 0
    for user in users:
        # ✅ Get today's follow-ups for this user
        today_followups = FollowUp.objects.filter(
            lead__assigned_to_id=user.id,
            scheduled_at__date=today,
            is_attended=False
        ).select_related('lead')
        
        followup_count = today_followups.count()
        
        # ✅ Prepare data with lead details
        lead_names = [f.lead.full_name for f in today_followups[:5]]
        lead_details = [
            {
                'id': f.lead.id,
                'name': f.lead.full_name,
                'mobile': f.lead.mobile_no,
                'time': f.scheduled_at.strftime('%I:%M %p') if f.scheduled_at else None
            }
            for f in today_followups[:10]
        ]
        
        more_count = followup_count - 5 if followup_count > 5 else 0
        
        if followup_count > 0:
            title = "Today's Follow-ups"
            
            if followup_count == 1:
                message = f"You have 1 follow-up today: {lead_names[0]}"
            elif followup_count <= 5:
                message = f"You have {followup_count} follow-ups today: {', '.join(lead_names)}"
            else:
                message = f"You have {followup_count} follow-ups today: {', '.join(lead_names)} and {more_count} more"
            
            # ✅ Send notification via WebSocket
            send_daily_followup_notification(
                user.id,
                title,
                message,
                followup_count,
                lead_details,
                followup_count > 5
            )
            count += 1
        else:
            # ✅ Optional: Send "No follow-ups today" notification
            send_daily_followup_notification(
                user.id,
                "No Follow-ups Today",
                "You have no follow-ups scheduled for today. Enjoy your day!",
                0,
                [],
                False
            )
            count += 1
    
    print(f"✅ Daily follow-up count sent to {count} users at {today}")
    return count


# ==========================================
# 2. TASK - Send Daily Follow-up Notification
# ==========================================
@task(retries=3, retry_delay=60)
def send_daily_followup_notification(user_id, title, message, followup_count, lead_details, has_more):
    """
    Send daily follow-up count notification to a specific user
    """
    try:
        
        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        today = timezone.now().astimezone(ist).date()
        
        # ✅ Save notification to database
        notification = Notification.objects.create(
            user_id=user_id,
            notification_type='daily_followup_count',
            title=title,
            message=message,
            is_read=False,
            retry_count=0
        )
        
        # ✅ Send via WebSocket
        channel_layer = get_channel_layer()
        group_name = f"notif_user_{user_id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification',
                'notification_type': 'daily_followup_count',
                'title': title,
                'message': message,
                'data': {
                    'id': notification.id,
                    'created_at': str(notification.created_at),
                    'followup_count': followup_count,
                    'lead_details': lead_details,
                    'has_more': has_more,
                    'total_count': followup_count,
                }
            }
        )
        
        print(f"✅ Daily follow-up count sent to user {user_id}: {followup_count} follow-ups")
        return notification.id
        
    except Exception as e:
        print(f"❌ Failed to send daily follow-up notification to user {user_id}: {e}")
        return None
