from django.urls import re_path
from .import consumers

websocket_urlpatterns = [
    # re_path(r'ws/users/$', consumers.DataConsumer.as_asgi()),
    re_path(r'ws/course/$',consumers.CourseDetails.as_asgi()),
    re_path(r'ws/notification/$',consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/reminder/$',consumers.ReminderNotificationConsumer.as_asgi())
    ]