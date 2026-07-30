import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import * 
from .services.query_services import *
from django.conf import settings
from datetime import datetime, timedelta
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
        print("✅ Unread list refreshed & sent to frontend!")
        
    @sync_to_async
    def get_user_notifications(self, user_id, limit=50):
        """
        Get notifications for a user from database
        """
        notifications = Notification.objects.filter(
            user_id=user_id,
            notification_type__in=["followup_reminder", "missed_followup","reminder"],
            # notification_type="reminder",
            is_read=False
        ).order_by("-created_at")
        
        return [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'notification_type': n.notification_type,
                'date': str(n.created_at),
                'scheduled_remainder': str(n.scheduled_remainder) if n.scheduled_remainder else None
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
                    print(f"✅ DB Verified: {user.username} (ID: {user.id}) connected to Postgres.")
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
        print(f"📩 Event received: {event}")
        await self.send(text_data=json.dumps({
            "notification_type": event.get("notification_type"),
            "title":             event.get("title"),
            "message":           event.get("message"),
            "data":              event.get("data"),
        }, default=str))
        print(f"✅ Sent to frontend!")
        
    async def refresh_notifications(self, event):
        print(f"🔄 Refresh triggered for user: {self.user_id}")

        fetch_list = await self.get_user_notifications(self.user_id)

        await self.send(text_data=json.dumps({
            "action": "refresh",
            "payload": fetch_list
        }, default=str))
        print("✅ Notification list refreshed & sent to frontend!")
    
    @sync_to_async
    def get_user_notifications(self, user_id, limit=50):
        """
        Get notifications for a user from database
        """
        notifications = Notification.objects.filter(
            user_id=user_id,
            notification_type__in=["notification","lead_notification","daily_followup_count"],
            is_read=False
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'notification_type': n.notification_type,
                'date': str(n.created_at),
                'scheduled_remainder': str(n.scheduled_remainder) if n.scheduled_remainder else None
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