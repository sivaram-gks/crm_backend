from django.apps import apps
from huey.contrib.djhuey import task,periodic_task
from huey import crontab
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.conf import settings
from .models import *
from .services.query_services import *
from rest_framework.exceptions import APIException, NotFound
from datetime import datetime, timedelta
import zoneinfo
from django.utils import timezone



# @task()
# @periodic_task(crontab(minute='*/1'))
def notification_task():
    try:
        channel_layer = get_channel_layer()
        print(f"Channel Layer: {channel_layer}")  
        users_with_reminders = UserSettings.objects.filter(
            follow_up_reminders=True
        ).select_related('user')
        print(f"👥 Total users with reminders: {users_with_reminders.count()}")
        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        now = timezone.now().astimezone(ist)
        print(f"🕐 Now IST: {now}")
        
        
        for setting in users_with_reminders:
            user = setting.user
            reminder_minutes = int(setting.reminder_time)

            remain_follow = FollowUp.objects.filter(
                telecaller_id=user,
                is_attended=False
            ).select_related('lead')
            print(f"📋 User {user.id} — Total followups: {remain_follow.count()}")  # ✅ Followups இருக்கா?

            for follow in remain_follow:
                task_eta = follow.scheduled_at - timedelta(minutes=reminder_minutes)
                task_eta_ist = task_eta.astimezone(ist)
                diff = abs((task_eta_ist - now).total_seconds())

                print(f"[User {user.id}] Follow {follow.id} | ETA IST: {task_eta_ist} | diff: {diff:.1f}s")

                if 0 <=diff <= 60:
                    already_sent = Notification.objects.filter(
                        user=user,
                        follow_up=follow,
                        notification_type="followup_reminder"
                    ).exists()
                    
                    if already_sent:
                        print(f"⚠️ Already sent → Follow {follow.id}, skipping")
                        continue 
                    lead = follow.lead
                    lead_name = lead.full_name
                    scheduled_ist = follow.scheduled_at.astimezone(ist).strftime('%I:%M %p')

                    message = f"{lead_name} - {reminder_minutes} minutes your reminder time"
                    Notification.objects.create(
                            user=user,
                            title="Follow-up Reminder",
                            message=message,
                            notification_type="followup_reminder",
                            follow_up=follow,
                            
                        )

                    # channel_layer = get_channel_layer()
                    print(f"📤 Sending to group: notif_user_{user.id}")
                    async_to_sync(channel_layer.group_send)(
                            f"notif_user_{user.id}",  # ✅ dynamic
                            {
                                "type": "send_notification",
                                "notification_type": "followup_reminder",
                                "title": "Follow-up Reminder",
                                "message":message,
                                "data": {
                                    "followup_id": follow.id,
                                    "lead_name": lead_name,
                                    "scheduled_at": scheduled_ist
                                }
                            }
                        )
                # db notification store enga pannanum
        # print(f"✅ Notification sent → User {user.id}, Follow {follow.id}")

    except Exception as e:
        print(f"❌ notification_task error: {e}")
        raise APIException(e)



# @periodic_task(crontab(minute='*'))
# def missed_followups_task():
    
#     try:
#         users_with_reminders = UserSettings.objects.filter(
#             follow_up_reminders=True
#         ).select_related('user')

#         ist = zoneinfo.ZoneInfo('Asia/Kolkata')
#         now = timezone.now().astimezone(ist)

#         for setting in users_with_reminders:
#             user = setting.user
#             reminder_minutes = int(setting.reminder_time)

#             # remain_follow = FollowUp.objects.filter(
#             #     telecaller_id=user,
#             #     is_attended=False
#             # ).select_related('lead')
            
#             missed_follow=Notification.objects.filter(
#                 user_id=user,
#                 is_read=False
#             ).select_related('follow_up')

#             for follow in missed_follow:
#                 task_eta = follow.follow_up.scheduled_at + timedelta(minutes=10)
#                 task_eta_ist = task_eta.astimezone(ist)
#                 diff = abs((task_eta_ist == now).total_seconds())

#                 print(f"[User {user.id}] Follow {follow.id} | ETA IST: {task_eta_ist} | diff: {diff:.1f}s")

#                 if 0 <=diff <= 60:
#                     lead = follow.lead
#                     lead_name = lead.full_name
#                     scheduled_ist = follow.scheduled_at.astimezone(ist).strftime('%I:%M %p')

#                     message = f"{lead_name} - {reminder_minutes} minutes your reminder time"
#                     Notification.objects.create(
#                             user=user,
#                             title="Follow-up Reminder",
#                             message=message,
#                             notification_type="followup_reminder",
#                             follow_up=follow,
                            
#                         )

#                     channel_layer = get_channel_layer()
#                     async_to_sync(channel_layer.group_send)(
#                             f"notif_user_{user.id}",  # ✅ dynamic
#                             {
#                                 "type": "send_notification",
#                                 "notification_type": "followup_reminder",
#                                 "title": "Follow-up Reminder",
#                                 "message":message,
#                                 "data": {
#                                     "followup_id": follow.id,
#                                     "lead_name": lead_name,
#                                     "scheduled_at": scheduled_ist
#                                 }
#                             }
#                         )
#                 # db notification store enga pannanum
#         print(f"✅ Notification sent → User {user.id}, Follow {follow.id}")

#     except Exception as e:
#         print(f"❌ notification_task error: {e}")
#         raise APIException(e)




# @periodic_task(crontab(minute='*/1'))  # every 1 min
def missed_followups_task():
    try:
        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        now = timezone.now().astimezone(ist)

        # 🔥 only unread reminders
        reminders = Notification.objects.filter(
            notification_type="followup_reminder",
            is_read=False
        ).select_related('follow_up', 'user')
        print(f"📋 Total unread reminders: {reminders.count()}")        
        for notif in reminders:
            follow = notif.follow_up
            user = notif.user

            if not follow:
                print(f"⚠️ Notif {notif.id} — follow_up None, skip")
                continue

            # ⏱ scheduled + 10 min
            missed_time = follow.scheduled_at + timedelta(minutes=10)
            missed_time = missed_time.astimezone(ist)

            # ⏱ diff
            diff = (now - missed_time).total_seconds()
            print(f"  ↳ Notif {notif.id} | follow {follow.id} | diff: {diff:.1f}s | condition: {diff >= 0}")  # ✅ diff என்ன வருது?

            # 🔥 condition: after 10 min
            if diff >= 0:

                # 🔁 every 5 min once
                if int(diff) % 300 > 60:
                    # print(f"     mod: {mod} | window ok: {mod <= 60}")  # ✅ mod check

                    continue

                # ❌ already sent same retry skip
                already_sent = Notification.objects.filter(
                    follow_up=follow,
                    notification_type="missed_followup",
                    retry_count=notif.retry_count + 1
                ).exists()

                if already_sent:
                    continue

                lead = follow.lead
                message = f"{lead.full_name} - Missed follow-up!"

                # 💾 save log
                new_notif = Notification.objects.create(
                    user=user,
                    title="Missed_Follow-up Reminder",
                    follow_up=follow,
                    notification_type="missed_followup",
                    message=message,
                    retry_count=notif.retry_count + 1
                )
                MissedFollowUpHistory.objects.create(
                    sent_at=datetime.now(),
                    message=message,
                    follow_up=follow,
                    lead_id=lead
                )
                # 📡 websocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"notif_user_{user.id}",
                    {
                        "type": "send_notification",
                        "notification_type": "missed_followup",
                        "title": "Missed Follow-up",
                        "message": message,
                        "data": {
                            "followup_id": follow.id,
                            "retry": new_notif.retry_count
                        }
                    }
                )

                print(f"🔁 Missed sent {new_notif.retry_count} → {user.id}")

    except Exception as e:
        print(f"❌ missed task error: {e}")

# @task()
# def notification_task():
#     try:
#         tele_id = 1  

#         try:
#             user = User.objects.get(pk=tele_id)  
#         except User.DoesNotExist:
#             raise NotFound(detail=f"User with id {tele_id} not found")
        
        
        
#         setting=UserSettings.objects.filter(follow_up_reminders=True,user=user).first()
        
        
#         ist = zoneinfo.ZoneInfo('Asia/Kolkata')
#         now = timezone.now().astimezone(ist)
#         print('IST:', now)
#         print("reminderr",setting.reminder_time)
            
#         remain_follow=FollowUp.objects.filter(                
#             telecaller_id=user,
#                 is_attended=False)
            
#         print(remain_follow)
#         scheduled_count=0
#         for follow in remain_follow:
#             print(follow.scheduled_at)
#             task_eta = follow.scheduled_at - timedelta(
#                 minutes=int(setting.reminder_time)
#             )
#             print('eta',task_eta)
            
#             # Convert task_eta to IST for comparison
#             task_eta_ist = task_eta.astimezone(ist)
            
#             print("ist eta",task_eta_ist)
#             # Check if task_eta is within ±1 minute of now
#             diff = abs((task_eta_ist - now).total_seconds())
            
#             if diff <= 60:  # within 60 seconds window
#                 scheduled_count += 1
#                 print('Reminder triggered for follow:', follow.id)
        
#         followup = FollowUp.objects.filter(pk=follow.id).first()
#         lead = followup.lead
#         scheduled_ist = followup.scheduled_at.astimezone(ist).strftime('%I:%M %p')
#         lead_name = lead.full_name
        
#         message = f"{lead_name} - {setting.reminder_time} minutes-ல் followup இருக்கு!"

#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"notif_user_1",
#             {
#                 "type": "send_notification",
#                 "notification_type": "followup_reminder",
#                 "title": "Follow-up Reminder",
#                 "message": message,
#                 "data": {
#                     "followup_id": follow.id,
#                     "lead_name":lead_name,
#                     "scheduled_at": scheduled_ist
#                 }
#             }
#         )
        
#     except Exception as e:
#         raise APIException(e)    
 
# notification_task()   
    

    


    
    
# @task()  
def send_followup_reminder_task(user_id, followup_id):
    try:
        print('task start')
        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        
        setting = UserSettings.objects.filter(user_id=user_id).first()

        followup = FollowUp.objects.filter(pk=followup_id).first()
        if not followup:
            print(f"[BLOCKED] followup {followup_id} not found")
            return

        lead = followup.lead
        scheduled_ist = followup.scheduled_at.astimezone(ist).strftime('%I:%M %p')
        lead_name = lead.full_name

        # ──────────────────────────────────────────
        # reminder ON  → "X minutes முன்னாடி" message
        # reminder OFF → "time வந்துடுச்சு" message (exact time)
        # ──────────────────────────────────────────
        if setting and setting.follow_up_reminders:
            message = f"{lead_name} - {setting.reminder_time} minutes-ல் followup இருக்கு!"
        else:
            message = f"{lead_name} - time வந்துடுச்சு!"

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notif_user_{user_id}",
            {
                "type": "send_notification",
                "notification_type": "followup_reminder",
                "title": "Follow-up Reminder",
                "message": message,
                "data": {
                    "followup_id": followup_id,
                    "lead_name":lead_name,
                    "scheduled_at": scheduled_ist
                }
            }
        )
        print(f"[SENT] followup reminder to user {user_id}")

    except Exception as e:
        print(f"[Task ERROR] {str(e)}")
        raise