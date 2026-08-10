from ..models.user import User
from ..models.courses import CourseName 
from ..models.courses import CoursePlan
from ..models.courses import Course
from ..models.leads import FilterPipeline
from ..models.notification import Notification 
from rest_framework.exceptions import APIException
from django.utils import timezone
from datetime import datetime, timedelta
from ..services.query_services import exec_raw_sql
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models.follow_up import FollowUp



def normalize_date_range(filter_type, from_date=None, to_date=None):
    try:
        import zoneinfo
        ist = zoneinfo.ZoneInfo('Asia/Kolkata')
        today = datetime.now(ist).date()
    except Exception:
        today = datetime.now().date()

    ft = str(filter_type or "").lower().strip()

    if ft in ["today", "daily"]:
        return today, today
    elif ft == "yesterday":
        y = today - timedelta(days=1)
        return y, y
    elif ft in ["weekly", "week"]:
        return today - timedelta(days=7), today
    elif ft in ["monthly", "month"]:
        return today - timedelta(days=30), today
    elif ft in ["year", "yearly"]:
        return today.replace(month=1, day=1), today
    elif ft == "custom" and from_date and str(from_date) != "None":
        try:
            fd = datetime.strptime(str(from_date), "%Y-%m-%d").date() if isinstance(from_date, str) else from_date
            td = datetime.strptime(str(to_date), "%Y-%m-%d").date() if isinstance(to_date, str) else (to_date or today)
            return fd, td
        except Exception:
            return today.replace(month=1, day=1), today
    else:
        return today.replace(month=1, day=1), today


def dashboard_top_tile(user,**data):
    try:
        id=user.id
        filter_type = data.get("filter_type", "monthly")
        from_d, to_d = normalize_date_range(filter_type, data.get("from_date"), data.get("to_date"))

        params = {
            "id": id,
            "from_date": str(from_d),
            "to_date": str(to_d),
            "filter_type": str(filter_type)
        }
        pay=exec_raw_sql("D_FETCH_DASHBOARD_TOP_TILES",params)
        return pay
        
    except Exception as e:
        raise APIException(e)
    
    
def fetch_pipeline_funnel(user,**data):
    try:
        id = user.id
        filter_type = data.get("filter_type", "year")
        from_d, to_d = normalize_date_range(filter_type, data.get("from_date"), data.get("to_date"))

        params = {
            "id": id,
            "from_date": str(from_d),
            "to_date": str(to_d),
            "filter_type": str(filter_type)
        }

        result = exec_raw_sql("D_FETCH_PIPELINE_FUNNEL", params)
        return {"funnel": result}

    except Exception as e:
        raise APIException(e)
    
    
def fetch_dashboard_analytics(user,**data):
    try:
        id=user.id
        filter_type = data.get("filter_type", "month")
        from_d, to_d = normalize_date_range(filter_type, data.get("from_date"), data.get("to_date"))

        params = {
            "id": id,
            "from_date": str(from_d),
            "to_date": str(to_d),
        }

        performance   = exec_raw_sql("D_FETCH_TELECALLER_PERFORMANCE", params)
        enrollment    = exec_raw_sql("D_FETCH_ENROLLMENT_BY_COURSE_TELE", params)
        loss_analysis = exec_raw_sql("D_FETCH_LOSS_ANALYSIS_TELE", params)
        return {
            "performance": performance[0] if performance else {},
            "enrollment":enrollment if enrollment else {},
            "loss_analysis": {
                "total_lost": sum(l["total_lost"] for l in loss_analysis) if loss_analysis else 0,
                "reasons": [
                    {
                        "label": l["reason"],
                        "value": l["total_lost"],
                        "percentage": l["percentage"]
                    }
                    for l in (loss_analysis or [])
                ]
            }
        }
    except Exception as e:
        raise APIException(e)
    
    

def get_date_filter_label(filter_type, from_date=None, to_date=None):
    """Get human-readable date filter label"""
    today = datetime.now().date()
    
    if filter_type == "today":
        return f"Today ({today.strftime('%b %d, %Y')})"
    elif filter_type == "yesterday":
        yesterday = today - timedelta(days=1)
        return f"Yesterday ({yesterday.strftime('%b %d, %Y')})"
    elif filter_type == "weekly":
        if from_date:
            return f"Last 7 Days ({from_date.strftime('%b %d')} - {today.strftime('%b %d, %Y')})"
        return f"Last 7 Days"
    elif filter_type == "monthly":
        if from_date:
            return f"Month of {from_date.strftime('%B %Y')}"
        return f"This Month"
    elif filter_type == "year":
        if from_date:
            return f"Year {from_date.strftime('%Y')}"
        return f"This Year"
    elif filter_type == "custom":
        if from_date and to_date:
            return f"{from_date.strftime('%b %d, %Y')} - {to_date.strftime('%b %d, %Y')}"
        return f"Custom Range"
    else:
        return "Yearly"

    
def get_user_details(user):
    """
    Safely get user details without causing serialization errors
    """
    try:
        # Get user name from the user object
        user_name = str(user)
        print(user_name)
        
        # Try to get user object from database
        try:
            user_obj = User.objects.get(id=user.id)
            
            # Get user name - try different field names
            if hasattr(user_obj, 'first_name') and user_obj.first_name:
                user_name = user_obj.first_name
                # if hasattr(user_obj, 'last_name') and user_obj.last_name:
                #     user_name = f"{user_name} {user_obj.last_name}"
            elif hasattr(user_obj, 'name') and user_obj.name:
                user_name = user_obj.name
            elif hasattr(user_obj, 'username') and user_obj.username:
                user_name = user_obj.username
            
            # Get user role - IMPORTANT FIX: Check if role is a ManyToMany field
            user_role = "Telecaller"
            
            # If user has role attribute
            if hasattr(user_obj, 'role'):
                role_value = user_obj.role
                
                # Check if it's a ManyRelatedManager (ManyToMany field)
                if 'ManyRelatedManager' in str(type(role_value)):
                    # It's a ManyToMany field, get the first role
                    try:
                        # Try to get role name from the many-to-many relation
                        if hasattr(role_value, 'all'):
                            roles = role_value.all()
                            if roles.exists():
                                first_role = roles.first()
                                if hasattr(first_role, 'name'):
                                    user_role = first_role.name
                                elif hasattr(first_role, 'role_name'):
                                    user_role = first_role.role_name
                                elif hasattr(first_role, 'title'):
                                    user_role = first_role.title
                    except:
                        pass
                elif isinstance(role_value, str):
                    user_role = role_value
                else:
                    # Try to convert to string
                    user_role = str(role_value)
            
            # If still "Telecaller", try other fields
            if user_role == "Telecaller" or user_role == "":
                if hasattr(user_obj, 'user_type') and user_obj.user_type:
                    user_role = str(user_obj.user_type)
                elif hasattr(user_obj, 'designation') and user_obj.designation:
                    user_role = str(user_obj.designation)
                elif hasattr(user_obj, 'role_name') and user_obj.role_name:
                    user_role = str(user_obj.role_name)
                
        except User.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error getting user details: {e}")
        
        return {
            "name": user_name,
            "role": user_role
        }
        
    except Exception as e:
        # Fallback for any other error
        return {
            "name": str(user),
            "role": "Telecaller"
        }

def get_dashboard_pdf_data(user, **data):
    """
    Main function to get all dashboard data for PDF creation
    Returns only the data, not the PDF file
    """
    try:
        filter_type = data.get("filter_type", "year")
        from_date = data.get("from_date")
        to_date = data.get("to_date")
        
        # Get user details safely
        user_details = get_user_details(user)
        print("user",user_details)
        # Fetch all dashboard data
        stats_cards = dashboard_top_tile(user, **data)
        pipeline_data = fetch_pipeline_funnel(user, **data)
        analytics_data = fetch_dashboard_analytics(user, **data)
        # course_data = fetch_course_availability(user, **data)
        
        # Get date filter label
        date_filter_label = get_date_filter_label(filter_type, from_date, to_date)
        
        # Prepare complete dashboard response - Match your exact required format
        dashboard_response = {
            "data": {
                "generated_for": user_details["name"],
                "role": user_details["role"],
                "date_filter_label": date_filter_label,
                "stats_cards": stats_cards,
                # "course_availability": course_data,
                "pipeline": pipeline_data,
                "performance": analytics_data.get("performance", {}),
                "enrollment_by_courses": analytics_data.get("enrollment", {}),
                "loss_analysis": analytics_data.get("loss_analysis", {})
            }
        }
        
        return dashboard_response
        
    except Exception as e:
        raise APIException(f"Failed to get dashboard data: {str(e)}")
    
def add_course_details(user,**data):
    try:

        
        c_name=CourseName.objects.filter(id=data.get("course_name_id")).first()
        
        c_paln=CoursePlan.objects.filter(id=data.get("course_plan_id")).first()
        course_plan=c_paln.courseplan
        course_name = c_name.coursename  # ✅ Fixed here

        initialname = ''.join(
            word[0].upper()
            for word in course_name.split()
        )
        initialplan = ''.join(
            word[0].upper()
            for word in course_plan.split()
        )

        existing_count = Course.objects.filter(
            course_name=c_name,
            course_plan=c_paln
        ).count()

        batch_code = f"{initialplan}-{initialname}-B{existing_count + 1}"

        
        course=Course.objects.create(
            course_name_id=data.get("course_name_id"),
            course_plan_id=data.get("course_plan_id"),
            course_time_id=data.get("course_time_id"),
            course_fees=data.get("fees"),
            batch=batch_code,
            starting_date=data.get("start_date"),
            closing_date=data.get("start_date"),
            total_seats=data.get("total_seat"),
            created_by="admin"
        )
        
        
        return {
            "detail": "Course created successfully",
            "status_code": 201,
            "data": {
                "id": course.id,
                "batch": course.batch,
                "course_name": course_name
            }
        }      
    except Exception as e:
        raise APIException(e)    
    


def add_course(**data):
    try:
        FilterPipeline.objects.create(
            name=data.get("name"),
            # stages_id=9,
            is_active=True,
            created_by="admin"
        )
        # pass
        return "created {name} sucessfull"
    except Exception as e:
        raise APIException(str(e))
    
    
    
def mark_notification_read(user, **data):
    try:
        notification_id = data.get("notification_id")

        notification = Notification.objects.filter(
            id=notification_id,
            user_id=user.id
        ).first()

        if not notification:
            raise APIException("Notification not found")

        # Notification read
        notification.is_read = True
        notification.updated_at = timezone.now()
        notification.save()

        # -----------------------------------
        # FollowUp notification update
        # -----------------------------------
        if notification.follow_up_id:
            # Mark all notifications for this follow-up as read
            Notification.objects.filter(
                follow_up_id=notification.follow_up_id,
                user_id=user.id
            ).update(
                is_read=True,
                updated_at=timezone.now(),
                updated_by=user.username
            )

        # Broadcast refresh to BOTH notification and reminder WebSocket channels
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f"notif_user_{user.id}",
            {
                "type": "refresh_notifications",
                "user_id": user.id,
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"reminder_user_{user.id}",
            {
                "type": "refresh_remainder",
                "user_id": user.id,
            }
        )

        return {"success": True, "id": notification.id}

    except APIException:
        raise
    except Exception as e:
        raise APIException(str(e))


def get_group_name(notif_type, user_id):
    reminder_types = ["followup_reminder", "missed_followup", "reminder"]
    
    if notif_type in reminder_types:
        return f"reminder_user_{user_id}"
    return f"notif_user_{user_id}"
    
    
    
    
    
    
    
    
    
    
    
    
    