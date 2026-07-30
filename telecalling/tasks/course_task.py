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
# from datetime import datetime, timedelta
import zoneinfo
from django.utils import timezone


@task()   
# @periodic_task(crontab(minute='*/1')) 
def course_count_task():
    try:
        # ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        # now = timezone.now()
        # print("current_time",{now})
        course=exec_raw_sql('D_FETCH_ALL_COURSE_DATA',{})
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "course_details",
            {
                "type": "course_data", 
                "data":course
            }
        )
        
    except Exception as e:
        raise APIException(e)
    
    