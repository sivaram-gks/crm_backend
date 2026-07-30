from django.apps import apps
from huey.contrib.djhuey import task, periodic_task
from huey import crontab

# ✅ FIX: import these directly instead of relying on the wildcard
# "from .notification_task import *" below to transitively re-export them.
# It happened to work because notification_task.py imports these at module
# level (so `import *` pulls them along), but that's fragile - if
# notification_task.py ever adds an __all__ list or reorders its imports,
# this file breaks with NameError at runtime with no warning until then.
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
from .notification_task import *






def send_reminder_to_user(user_id, notification_type, title, message,
                           follow_up_id=None, payment_id=None, scheduled_remainder=None, data=None,
                           force_create=False):
    try:
        notification = Notification.objects.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            follow_up_id=follow_up_id,
            payment_id=payment_id,
            scheduled_remainder=scheduled_remainder,
            is_read=False,
            retry_count=data.get('attempt', 0) if data else 0
        )
        notification_id = notification.id
        print(f"✅ New notification created {notification_id}")

        # ✅ group name matches ReminderNotificationConsumer's
        # self.group_name = f"reminder_user_{self.user_id}"
        channel_layer = get_channel_layer()
        group_name = f"reminder_user_{user_id}"

        notification_data = {
            'id': notification.id,
            'created_at': str(notification.created_at),
            'follow_up_id': follow_up_id,
            'payment_id': payment_id,
            'scheduled_remainder': str(scheduled_remainder) if scheduled_remainder else None,
            'is_retry': not force_create and notification_type == 'missed_followup',
            'attempt': data.get('attempt', 1) if data else 1,
            **(data or {})
        }

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'reminder_notification',
                'notification_type': notification_type,
                'title': title,
                'message': message,
                'data': notification_data
            }
        )

        print(f"✅ Notification sent to user {user_id}: {title} (Attempt: {notification_data.get('attempt', 1)})")
        return notification_id

    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return None

@periodic_task(crontab(minute='*/1'))  # Every 1 minute
def send_followup_reminders():
    """
    Send reminders for follow-ups scheduled at the current minute
    """
    ist = zoneinfo.ZoneInfo('Asia/Kolkata')
    now = timezone.now().astimezone(ist)
    current_minute = now.replace(second=0, microsecond=0)
    next_minute = now.replace(second=59, microsecond=59)

    # ✅ Current minute la irukka follow-ups mattum
    followups = FollowUp.objects.filter(
        scheduled_at__gte=current_minute,
        scheduled_at__lt=next_minute,
        is_attended=False
    ).exclude(
        id__in=Notification.objects.filter(
            notification_type='followup_reminder',
            is_read=False
        ).values_list('follow_up_id', flat=True)
    ).select_related('lead', 'lead__assigned_to')

    count = 0
    for followup in followups:
        send_followup_reminder(followup.id, followup.lead.assigned_to_id)
        count += 1

    print(f"✅ Sent {count} follow-up reminders for {current_minute.strftime('%H:%M')}")
    return count


# ==========================================
# 2. TASK - Send Follow-up Reminder
# ==========================================
@task(retries=3, retry_delay=60)
def send_followup_reminder(follow_up_id, user_id):
    """
    Send follow-up reminder notification - Only once per follow-up
    """
    try:
        follow_up = FollowUp.objects.select_related('lead', 'lead__assigned_to').get(id=follow_up_id)
        lead = follow_up.lead

        # Check if notification already exists
        existing_notification = Notification.objects.filter(
            follow_up_id=follow_up.id,
            notification_type='followup_reminder',
            is_read=False
        ).exists()

        if existing_notification:
            print(f"⏭️ Notification already sent for follow-up {follow_up_id} - Skipping")
            return None
        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        scheduled_at_ist = follow_up.scheduled_at.astimezone(ist)
        title = "Follow-up Reminder"
        message = f"Follow-up reminder for {lead.full_name} at {scheduled_at_ist.strftime('%I:%M %p')}"

        data = {
            'lead_id': lead.id,
            'lead_name': lead.full_name,
            'lead_mobile': lead.mobile_no,
            'follow_up_id': follow_up.id,
            'scheduled_at': str(scheduled_at_ist),
            'notes': follow_up.notes
        }

        notification_id = send_reminder_to_user(
            user_id or lead.assigned_to_id,
            'followup_reminder',
            title,
            message,
            follow_up_id=follow_up.id,
            scheduled_remainder=scheduled_at_ist,
            data=data
        )

        if notification_id:
            print(f"✅ Follow-up reminder sent for {lead.full_name}")
            print(f"⏰ Missed follow-up check scheduled for {lead.full_name} in 5 minutes")

        return notification_id

    except FollowUp.DoesNotExist:
        print(f"❌ FollowUp {follow_up_id} not found")
        return None
    except Exception as e:
        print(f"❌ Error in followup reminder: {e}")
        raise


# # ==========================================
# # 1. PERIODIC TASK - detects missed follow-ups every minute.
# # Does NOT require any pre-existing Notification - send_missed_followup_
# # notification() below creates/updates the Notification itself.
# # ==========================================
# @periodic_task(crontab(minute='*/1'))
# def check_missed_followups_scheduled():
#     """
#     Check for missed follow-ups every 1 minute
#     """
#     print("check missed run")
#     ist = zoneinfo.ZoneInfo('Asia/Kolkata')
#     now = timezone.now().astimezone(ist)

#     five_min_ago = now - timedelta(minutes=5)
#     six_min_ago = now - timedelta(minutes=6)

#     print(five_min_ago)
#     print(six_min_ago)

#     missed_followups = FollowUp.objects.filter(
#         scheduled_at__gte=six_min_ago,
#         scheduled_at__lt=five_min_ago,
#         is_attended=False
#     ).select_related('lead', 'lead__assigned_to')
#     print(missed_followups)
#     count = 0
#     for followup in missed_followups:
#         existing_history = MissedFollowUpHistory.objects.filter(
#             follow_up=followup
#         ).exists()

#         if not existing_history:
#             # ✅ FIX: don't require a pre-existing 'followup_reminder'
#             # notification. Call directly with the lead's assigned user -
#             # this can never silently no-op just because a prior
#             # notification wasn't found/was already read.
#             send_missed_followup_notification(
#                 followup.id,
#                 retry_count=1,
#                 is_first=True
#             )
#             count += 1

#     if count > 0:
#         print(f"📢 Processed {count} missed follow-ups")
#     print(f"✅ Sent {count} missed follow-up reminders for {now.strftime('%H:%M')}")
#     return count


# # ==========================================
# # 2. SINGLE TASK - Send Missed Follow-up Notification
# # ==========================================
# @task(retries=3, retry_delay=60)
# def send_missed_followup_notification(follow_up_id, retry_count, is_first=False):
#     """
#     Send missed follow-up notification - Single function for all attempts.
#     DB: a new MissedFollowUpHistory row per retry (audit trail).
#     Notification: single row per follow_up, created on first call and
#     updated with the latest message on every retry (handled inside
#     send_reminder_to_user - no pre-existing notification required).
#     WebSocket: sent on every retry.
#     """
#     try:
#         follow_up = FollowUp.objects.select_related('lead', 'lead__assigned_to').get(id=follow_up_id)
#         lead = follow_up.lead

#         if follow_up.is_attended:
#             print(f"✅ Follow-up for {lead.full_name} has been attended - No action needed")
#             return True

#         existing_history = MissedFollowUpHistory.objects.filter(
#             follow_up=follow_up,
#             retry_count=retry_count,
            
#         ).exists()

#         if existing_history:
#             print(f"⏭️ Missed follow-up retry {retry_count} already logged for {lead.full_name} - Skipping")
#             return None

#         ist = zoneinfo.ZoneInfo('Asia/Kolkata')
#         scheduled_at_ist = follow_up.scheduled_at.astimezone(ist)

#         if retry_count > 3:
#             final_message = f"🚫 {lead.full_name} missed follow-up {retry_count - 1} times. Please take action."

#             send_reminder_to_user(
#                 lead.assigned_to_id,
#                 'missed_followup',
#                 'Max Retry Reached',
#                 final_message,
#                 follow_up_id=follow_up.id,
#                 scheduled_remainder=follow_up.scheduled_at,
#                 data={
#                     'lead_id': lead.id,
#                     'lead_name': lead.full_name,
#                     'total_attempts': retry_count - 1,
#                     'is_final': True
#                 },
#                 force_create=True
#             )
#             print(f"🚫 Max retries reached for {lead.full_name} - Final notification sent")
#             return True

#         if is_first:
#             missed_title = "Missed Follow-up"
#             missed_message = f"{lead.full_name} missed their follow-up at {scheduled_at_ist.strftime('%I:%M %p')} - Attempt {retry_count}"
#         else:
#             missed_title = "Missed Follow-up"
#             missed_message = f"{lead.full_name} missed their follow-up again at {scheduled_at_ist.strftime('%I:%M %p')} - Attempt {retry_count} "

#         missed_data = {
#             'lead_id': lead.id,
#             'lead_name': lead.full_name,
#             'follow_up_id': follow_up.id,
#             'attempt': retry_count,
#             'scheduled_at': str(scheduled_at_ist),
#             'is_missed': True
#         }

#         notification_id = send_reminder_to_user(
#             lead.assigned_to_id,
#             'missed_followup',
#             missed_title,
#             missed_message,
#             follow_up_id=follow_up.id,
#             scheduled_remainder=follow_up.scheduled_at,
#             data=missed_data,
#             force_create=False
#         )

#         missed_history = MissedFollowUpHistory.objects.create(
#             notification_id=notification_id,
#             follow_up=follow_up,
#             lead=lead,
#             user=lead.assigned_to,
#             retry_count=retry_count,
#             message=missed_message
#         )

#         print(f"📢 Missed follow-up notification sent for {lead.full_name} - Attempt {retry_count} "
#               f"(new history row {missed_history.id} created)")

#         if retry_count < 3:
#             send_missed_followup_notification.schedule(
#                 args=(follow_up.id, retry_count + 1, False),
#                 delay=300  # 5 minutes later
#             )
#             print(f"🔄 Next retry {retry_count + 1} scheduled for {lead.full_name} in 5 minutes")

#         return missed_history.id

#     except FollowUp.DoesNotExist:
#         print(f"❌ FollowUp {follow_up_id} not found")
#         return None
#     except Exception as e:
#         print(f"❌ Error in missed followup: {e}")
#         raise



# ==========================================
# 1. PERIODIC TASK - detects missed follow-ups every minute.
# Does NOT require any pre-existing Notification - send_missed_followup_
# notification() below creates/updates the Notification itself.
# ==========================================
@periodic_task(crontab(minute='*/1'))
def check_missed_followups_scheduled():
    """
    Check for missed follow-ups every 1 minute
    """
    print("check missed run")
    ist = zoneinfo.ZoneInfo('Asia/Kolkata')
    now = timezone.now().astimezone(ist)

    five_min_ago = now - timedelta(minutes=5)
    six_min_ago = now - timedelta(minutes=6)

    print(five_min_ago)
    print(six_min_ago)

    missed_followups = FollowUp.objects.filter(
        scheduled_at__gte=six_min_ago,
        scheduled_at__lt=five_min_ago,
        is_attended=False
    ).select_related('lead', 'lead__assigned_to')
    print(missed_followups)
    count = 0
    for followup in missed_followups:
        existing_history = MissedFollowUpHistory.objects.filter(
            follow_up=followup
        ).exists()

        if existing_history:
            continue

        # ✅ NEW CHECK — if the follow-up reminder OR any missed-followup
        # notification for this follow-up was already READ by the user,
        # don't even start the missed-followup chain. Reading it means
        # they've seen it, so we shouldn't nag them further.
        notification_already_read = Notification.objects.filter(
            follow_up_id=followup.id,
            notification_type__in=['followup_reminder', 'missed_followup'],
            is_read=True
        ).exists()

        if notification_already_read:
            print(f"👁️ Notification already read for {followup.lead.full_name} - skipping missed followup")
            continue

        # ✅ FIX: don't require a pre-existing 'followup_reminder'
        # notification. Call directly with the lead's assigned user -
        # this can never silently no-op just because a prior
        # notification wasn't found/was already read.
        send_missed_followup_notification(
            followup.id,
            retry_count=1,
            is_first=True
        )
        count += 1

    if count > 0:
        print(f"📢 Processed {count} missed follow-ups")
    print(f"✅ Sent {count} missed follow-up reminders for {now.strftime('%H:%M')}")
    return count


# ==========================================
# 2. SINGLE TASK - Send Missed Follow-up Notification
# ==========================================
@task(retries=3, retry_delay=60)
def send_missed_followup_notification(follow_up_id, retry_count, is_first=False):
    """
    Send missed follow-up notification - Single function for all attempts.
    DB: a new MissedFollowUpHistory row per retry (audit trail).
    Notification: single row per follow_up, created on first call and
    updated with the latest message on every retry (handled inside
    send_reminder_to_user - no pre-existing notification required).
    WebSocket: sent on every retry.
    """
    try:
        follow_up = FollowUp.objects.select_related('lead', 'lead__assigned_to').get(id=follow_up_id)
        lead = follow_up.lead

        if follow_up.is_attended:
            print(f"✅ Follow-up for {lead.full_name} has been attended - No action needed")
            return True

        # ✅ NEW CHECK — re-verify on every retry too. User might read the
        # notification in between retries (e.g. after attempt 1, before
        # attempt 2's scheduled 5-min delay fires). If so, stop retrying.
        notification_already_read = Notification.objects.filter(
            follow_up_id=follow_up.id,
            notification_type__in=['followup_reminder', 'missed_followup'],
            is_read=True
        ).exists()

        if notification_already_read:
            print(f"👁️ Notification already read for {lead.full_name} - stopping missed followup retries")
            return None

        existing_history = MissedFollowUpHistory.objects.filter(
            follow_up=follow_up,
            retry_count=retry_count,
        ).exists()

        if existing_history:
            print(f"⏭️ Missed follow-up retry {retry_count} already logged for {lead.full_name} - Skipping")
            return None

        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        scheduled_at_ist = follow_up.scheduled_at.astimezone(ist)

        if retry_count > 3:
            final_message = f"🚫 {lead.full_name} missed follow-up {retry_count - 1} times. Please take action."

            send_reminder_to_user(
                lead.assigned_to_id,
                'missed_followup',
                'Max Retry Reached',
                final_message,
                follow_up_id=follow_up.id,
                scheduled_remainder=follow_up.scheduled_at,
                data={
                    'lead_id': lead.id,
                    'lead_name': lead.full_name,
                    'total_attempts': retry_count - 1,
                    'is_final': True
                },
                force_create=True
            )
            print(f"🚫 Max retries reached for {lead.full_name} - Final notification sent")
            return True

        if is_first:
            missed_title = "Missed Follow-up"
            missed_message = f"{lead.full_name} missed their follow-up at {scheduled_at_ist.strftime('%I:%M %p')} - Attempt {retry_count}"
        else:
            missed_title = "Missed Follow-up"
            missed_message = f"{lead.full_name} missed their follow-up again at {scheduled_at_ist.strftime('%I:%M %p')} - Attempt {retry_count} "

        missed_data = {
            'lead_id': lead.id,
            'lead_name': lead.full_name,
            'follow_up_id': follow_up.id,
            'attempt': retry_count,
            'scheduled_at': str(scheduled_at_ist),
            'is_missed': True
        }

        notification_id = send_reminder_to_user(
            lead.assigned_to_id,
            'missed_followup',
            missed_title,
            missed_message,
            follow_up_id=follow_up.id,
            scheduled_remainder=follow_up.scheduled_at,
            data=missed_data,
            force_create=False
        )

        missed_history = MissedFollowUpHistory.objects.create(
            notification_id=notification_id,
            follow_up=follow_up,
            lead=lead,
            user=lead.assigned_to,
            retry_count=retry_count,
            message=missed_message
        )

        print(f"📢 Missed follow-up notification sent for {lead.full_name} - Attempt {retry_count} "
              f"(new history row {missed_history.id} created)")

        if retry_count < 3:
            send_missed_followup_notification.schedule(
                args=(follow_up.id, retry_count + 1, False),
                delay=300  # 5 minutes later
            )
            print(f"🔄 Next retry {retry_count + 1} scheduled for {lead.full_name} in 5 minutes")

        return missed_history.id

    except FollowUp.DoesNotExist:
        print(f"❌ FollowUp {follow_up_id} not found")
        return None
    except Exception as e:
        print(f"❌ Error in missed followup: {e}")
        raise




