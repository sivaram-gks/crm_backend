from rest_framework.exceptions import APIException, NotFound
from ..models import *
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
import zoneinfo





def notification_reminder_service(user):
    try:
        setting = UserSettings.objects.filter(
            user=user,
        ).first()


        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        now = timezone.now().astimezone(ist)
        print('IST:', now)
        


        now = timezone.now()
        if(setting.reminder_time):
            FollowUp.objects.filter(id__in=[165,158]).update(
                scheduled_at=now  + timedelta(minutes=1)+ timedelta(minutes=int(setting.reminder_time))),  
            
        if(setting.reminder_time):
            FollowUp.objects.filter(id__in=[78,136,1,98,2]).update(
                scheduled_at=now  + timedelta(minutes=1)+ timedelta(minutes=int(setting.reminder_time))),  
# + timedelta(minutes=2)
      

        # ──────────────────────────────────────────────
        # CASE 1: reminder disabled → fire AT scheduled_at exactly
        # ──────────────────────────────────────────────
        if not setting or not setting.follow_up_reminders:
            pending_followups = FollowUp.objects.filter(
                telecaller_id=user,
                scheduled_at__lte=now + timedelta(minutes=1),  # 1 min window
                scheduled_at__gte=now - timedelta(minutes=1),
                is_attended=False,
                attended_at__isnull=True
            )

            if not pending_followups.exists():
                return {"scheduled": False, "reason": "reminder disabled, no followups at scheduled time"}

            scheduled_count = 0
            for followup in pending_followups:
                # send_followup_reminder_task(
                #     user_id=user.id,
                #     followup_id=followup.id
                # )
                print(f"[OK - NO REMINDER] followup={followup.id} fires at exact scheduled_at={followup.scheduled_at}")
                scheduled_count += 1

            return {
                "scheduled": True,
                "count": scheduled_count,
                "reminder_before": "0 minutes (exact time)"
            }

        # ──────────────────────────────────────────────
        # CASE 2: reminder enabled → fire BEFORE scheduled_at
        # ──────────────────────────────────────────────
        pending_followups = FollowUp.objects.filter(
            telecaller_id=user,
            scheduled_at__lte=now + timedelta(minutes=int(setting.reminder_time)),
            is_attended=False,
            attended_at__isnull=True
        )

        if not pending_followups.exists():
            return {"scheduled": False, "reason": "no pending followups"}

        scheduled_count = 0
        for followup in pending_followups:
            task_eta = followup.scheduled_at - timedelta(
                minutes=int(setting.reminder_time)
            )

            if task_eta < now:
                print(f"[SKIP] followup {followup.id} eta already passed")
                continue

            # send_followup_reminder_task(
            #     user_id=user.id,
            #     followup_id=followup.id
            # )
            print(f"[OK] followup={followup.id} fires at {task_eta}")
            scheduled_count += 1

        return {
            "scheduled": True,
            "count": scheduled_count,
            "reminder_before": f"{setting.reminder_time} minutes"
        }

    except APIException:
        raise
    except Exception as e:
        raise APIException(detail=str(e))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

# def notification_reminder_service(user):
#     try:
#         setting = UserSettings.objects.filter(
#             user=user,
#             follow_up_reminders=True
#         ).first()
#         print(setting)
#         if not setting:
#             return {"scheduled": False, "reason": "reminder disabled"}

#         ist = zoneinfo.ZoneInfo('Asia/Kolkata')
#         now = timezone.now().astimezone(ist)
#         print('IST:', now)
        


#         now = timezone.now()
#         FollowUp.objects.filter(id__in=[158,159,160,161,162,163,164,165,168]).update(
#             scheduled_at=now + timedelta(minutes=5),
#         )
#     # எல்லா followups-உம் print பண்ணு
#         for f in FollowUp.objects.filter(telecaller_id=1):
#             print({
#                 "id": f.id,
#                 "scheduled_at": f.scheduled_at,
#                 "now": now,
#             })
#         pending_followups = FollowUp.objects.filter(
#             telecaller_id=user,
#             scheduled_at__lte=now + timedelta(minutes=int(setting.reminder_time)),
#             is_attended=False,
#             attended_at__isnull=True
#         )
        
#         print(now)
#         # print("pen",pending_followups.values())
#         if not pending_followups.exists():
#             return {"scheduled": False, "reason": "no pending followups"}

#         scheduled_count = 0

#         for followup in pending_followups:
#             print(followup.scheduled_at)
#             task_eta = followup.scheduled_at - timedelta(  # ✅ timedelta
#                 minutes=int(setting.reminder_time)
#             )
#             print("task_eta:", task_eta)
#             print("now     :", now)

#             if task_eta < now:
#                 print("task_eta < now",task_eta < now)
#                 print(f"[SKIP] followup {followup.id} eta already passed")
#                 continue
#             print('task')
#             send_followup_reminder_task(
#                 user_id=user.id,
#                 followup_id=followup.id
#             )

#             print(f"[OK] followup={followup.id} fires at {task_eta}")
#             scheduled_count += 1

#         return {
#             "scheduled": True,
#             "count": scheduled_count,
#             "reminder_before": f"{setting.reminder_time} minutes"
#         }

#     except APIException:
#         raise
#     except Exception as e:
#         raise APIException(detail=str(e))





# def notification_reminder_services(**data):
#     try:
#         tele_id = data.get("tele_id")  

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
        
        
        


#         return {
#             "scheduled": True,
#             "count": scheduled_count,
#             "reminder_before": f"{setting.reminder_time} minutes"
#         }

#     except Exception as e:
#         raise APIException(e)