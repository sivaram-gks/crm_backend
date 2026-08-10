import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import * 
from .services.query_services import *
from django.conf import settings
from django.db.models import Q
from datetime import datetime, timedelta
import zoneinfo
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken




class CourseDetails(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "course_details"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "course_details":
            fetch_list = await self.stock_data()

            await self.send(text_data=json.dumps({
                "payload": fetch_list
            },default=str))
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def course_data(self, event):
        course_list = event['data']
        await self.send(text_data=json.dumps({
            'payload': course_list
        }))   
    @sync_to_async
    def stock_data(self):
        data=exec_raw_sql('D_FETCH_ALL_COURSE_DATA',{})
        return data 
    
    
  
  
  
  
    
class ReminderNotificationConsumer(AsyncWebsocketConsumer):
   
    async def connect(self):
            # 1. URL-la irunthu token-ah edukkirom
            query_string = self.scope.get("query_string", b"").decode("utf-8")
            query_params = parse_qs(query_string)
            token = query_params.get("token", [None])[0]
            
            print(f"DEBUG: Received Token: {token}")

            if token:
                # 2. Database-la intha user irukkaangala-nu check panrom (pgAdmin DB search)
                user = await self.get_user_from_jwt(token)
                print("user",user)
                
                if user:
                    self.user_id = user.id
                    self.group_name = f"reminder_user_{self.user_id}"
                    
                    await self.channel_layer.group_add(self.group_name, self.channel_name)
                    await self.accept()
                    print(f"✅ DB Verified: {user.username} (ID: {user.id}) connected to Postgres.")
                else:
                    print("DEBUG: User not found or Token invalid")
                    await self.close()
            else:
                print("DEBUG: No token in Query String")
                await self.close()
    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "reminder_notification":
            fetch_list = await self.get_user_notifications(self.user_id)

            await self.send(text_data=json.dumps({
                "payload": fetch_list
            },default=str))
    async def disconnect(self, close_code):
        # await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name, 
                    self.channel_name
                )
    async def reminder_notification(self, event):
        print(f"📩 Event received: {event}")
        await self.send(text_data=json.dumps({
            "notification_type": event.get("notification_type"),
            "title":             event.get("title"),
            "message":           event.get("message"),
            "data":              event.get("data"),
        }, default=str))
        print(f"✅ Sent to frontend!")
        
        
    async def refresh_remainder(self, event):
        print(f"🔄 Refresh triggered for user: {self.user_id}")
        
        # DB la irunthu latest UNREAD list mattum eduthu anuppu
        fetch_list = await self.get_user_notifications(self.user_id)

        await self.send(text_data=json.dumps({
            "action": "refresh",
            "payload": fetch_list
        }, default=str))
        print("[OK] Unread list refreshed & sent to frontend!")
        
    @sync_to_async
    def get_user_notifications(self, user_id, limit=50):
        """
        Get reminders (missed follow-up 5-min recurring alerts) for a user from database
        """
        # Fetch unread 5-minute recurring missed follow-up alerts for active Follow Up stage leads
        notifications = Notification.objects.filter(
            user_id=user_id,
            notification_type__in=["missed_followup", "reminder"],
            follow_up__lead__pipeline_stage__name__iexact="follow up",
            is_read=False
        ).order_by("-created_at")[:limit]

        return [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'notification_type': n.notification_type,
                'date': str(n.created_at),
                'scheduled_remainder': str(n.scheduled_remainder) if n.scheduled_remainder else None,
                'read': n.is_read,
                'lead_id': n.lead_id or (n.follow_up.lead_id if n.follow_up else None)
            }
            for n in notifications
        ]

    
    @sync_to_async
    def get_user_from_jwt(self, token):
        try:
            # JWT token-ah decode panni user id edukkurom
            decoded_data = UntypedToken(token)
            user_id = decoded_data.get("uid") or decoded_data.get("user_id")
            print('user_id',user_id)
            # Intha line thaan pgAdmin/Postgres-la poi user-ah thedum
            return User.objects.get(id=user_id)
        except Exception as e:
            print(f"[ERROR] JWT Error: {e}")
            return None
        
        


class NotificationConsumer(AsyncWebsocketConsumer):
   
    async def connect(self):
            # 1. URL-la irunthu token-ah edukkirom
            query_string = self.scope.get("query_string", b"").decode("utf-8")
            query_params = parse_qs(query_string)
            token = query_params.get("token", [None])[0]
            
            print(f"DEBUG: Received Token: {token}")

            if token:
                # 2. Database-la intha user irukkaangala-nu check panrom (pgAdmin DB search)
                user = await self.get_user_from_jwt(token)
                print("user",user)
                
                if user:
                    self.user_id = user.id
                    self.group_name = f"notif_user_{self.user_id}"
                    
                    await self.channel_layer.group_add(self.group_name, self.channel_name)
                    await self.accept()
                    print(f"[OK] DB Verified: {user.username} (ID: {user.id}) connected to Postgres.")
                else:
                    print("DEBUG: User not found or Token invalid")
                    await self.close()
            else:
                print("DEBUG: No token in Query String")
                await self.close()
    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "notification":
            fetch_list = await self.get_user_notifications(self.user_id)

            await self.send(text_data=json.dumps({
                "payload": fetch_list
            },default=str))
    async def disconnect(self, close_code):
        # await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name, 
                    self.channel_name
                )
    async def notification(self, event):
        print(f"[EVENT] Event received: {event}")
        await self.send(text_data=json.dumps({
            "notification_type": event.get("notification_type"),
            "title":             event.get("title"),
            "message":           event.get("message"),
            "data":              event.get("data"),
        }, default=str))
        print(f"[OK] Sent to frontend!")
        
    async def refresh_notifications(self, event):
        print(f"[REFRESH] Refresh triggered for user: {self.user_id}")

        fetch_list = await self.get_user_notifications(self.user_id)

        await self.send(text_data=json.dumps({
            "action": "refresh",
            "payload": fetch_list
        }, default=str))
        print("[OK] Notification list refreshed & sent to frontend!")
    
    @sync_to_async
    def get_user_notifications(self, user_id, limit=50):
        """
        Get main notifications (New Lead, Initial Scheduled Follow-up Time Alert, Daily Count) for a user
        """
        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        now = datetime.now(ist)

        # 1. Automatically mark follow-ups as attended for leads that were moved to Won (3) or Loss (4)
        FollowUp.objects.filter(
            lead__pipeline_stage__name__in=["won", "loss"],
            is_attended=False
        ).update(is_attended=True)

        # 2. Check and generate initial follow-up reminder alerts when scheduled time arrives
        due_followups = FollowUp.objects.filter(
            Q(telecaller_id=user_id) | Q(lead__assigned_to_id=user_id),
            scheduled_at__lte=now,
            is_attended=False
        ).select_related('lead')

        for f in due_followups:
            exists = Notification.objects.filter(
                follow_up_id=f.id,
                notification_type__in=['followup_reminder', 'missed_followup']
            ).exists()

            if not exists:
                scheduled_at_ist = f.scheduled_at.astimezone(ist) if hasattr(f.scheduled_at, 'astimezone') else f.scheduled_at
                title = "Follow-up Reminder"
                message = f"Follow-up reminder for {f.lead.full_name} at {scheduled_at_ist.strftime('%I:%M %p') if hasattr(scheduled_at_ist, 'strftime') else str(scheduled_at_ist)}"

                Notification.objects.create(
                    user_id=user_id,
                    notification_type='followup_reminder',
                    title=title,
                    message=message,
                    follow_up_id=f.id,
                    scheduled_remainder=scheduled_at_ist,
                    is_read=False
                )

        notifications = Notification.objects.filter(
            user_id=user_id,
            notification_type__in=["notification", "lead_notification", "followup_reminder", "daily_followup_count"],
            is_read=False
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'notification_type': n.notification_type,
                'date': str(n.created_at),
                'scheduled_remainder': str(n.scheduled_remainder) if n.scheduled_remainder else None,
                'read': n.is_read,
                'lead_id': n.lead_id or (n.follow_up.lead_id if n.follow_up else None)
            }
            for n in notifications
        ]

    
    @sync_to_async
    def get_user_from_jwt(self, token):
        try:
            # JWT token-ah decode panni user id edukkurom
            decoded_data = UntypedToken(token)
            user_id = decoded_data.get("uid") or decoded_data.get("user_id")
            print('user_id',user_id)
            # Intha line thaan pgAdmin/Postgres-la poi user-ah thedum
            return User.objects.get(id=user_id)
        except Exception as e:
            print(f"❌ JWT Error: {e}")
            return None