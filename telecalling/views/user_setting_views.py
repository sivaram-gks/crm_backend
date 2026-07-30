from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.decorators import authentication_classes, permission_classes

from ..services.user_setting_services import (
    get_all_settings_service,
    update_notification_service,
    update_followup_service,
    update_caller_service,
    update_messaging_service,
    update_notes_service,
    update_lead_preference_service,
    update_security_service,
)

from ..services.notification_services import *
from ..tasks.api_log_task import api_history_log

# ─── GET all settings ───────────────────────────────────────────'
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# @authentication_classes([])  # or whichever you use
# @permission_classes([])
class GetAllSettingsApi(APIView):
    # permission_classes = [IsAuthenticated]
    # class InputSerializer(serializers.Serializer):
    #     tele_id=serializers.IntegerField(required=True)

    def get(self, request):
        print(request.user)
        data = get_all_settings_service(user=request.user)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': {}, 
            'response_payload': data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


# ─── Notification ────────────────────────────────────────────────
# @authentication_classes([])
# @permission_classes([])
class NotificationSettingApi(APIView):

    class InputSerializer(serializers.Serializer):
        follow_up_reminders      = serializers.BooleanField(required=False)
        sound_alerts             = serializers.BooleanField(required=False)
        reminder_time            = serializers.CharField( required=False)
        notify_new_lead_assigned = serializers.BooleanField(required=False)
        notify_missed_followups  = serializers.BooleanField(required=False)
        notify_reassigned_leads  = serializers.BooleanField(required=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_notification_service(
            user=request.user,
            **serializer.validated_data
        )
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload':data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


# ─── Follow-up ───────────────────────────────────────────────────
class FollowUpSettingApi(APIView):
    # permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        auto_suggestion_followup_date   = serializers.BooleanField(required=False)
        auto_manual_followup_edit       = serializers.BooleanField(required=False)
        followup_mandatory_before_close = serializers.BooleanField(required=False)
        mark_followup_as_completed      = serializers.BooleanField(required=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_followup_service(
            user=request.user,
            **serializer.validated_data
        )
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


# ─── Calling ─────────────────────────────────────────────────────
class CallerSettingApi(APIView):
    # permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        enable_click_to_call      = serializers.BooleanField(required=False)
        make_call_notes_mandatory = serializers.BooleanField(required=False)
        default_call_outcome      = serializers.CharField( required=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_caller_service(
            user=request.user,
            **serializer.validated_data
        )
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


# ─── Messaging ───────────────────────────────────────────────────
class MessagingSettingApi(APIView):
    # permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        enable_message_templates = serializers.BooleanField(required=False)
        allow_custom_templates   = serializers.BooleanField(required=False)
        auto_send_messages       = serializers.BooleanField(required=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_messaging_service(
            user=request.user,
            **serializer.validated_data
        )
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload':data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


# ─── Notes & Templates ───────────────────────────────────────────
class NotesSettingApi(APIView):
    # permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        make_notes_mandatory        = serializers.BooleanField(required=False)
        enable_quick_note_templates = serializers.BooleanField(required=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_notes_service(
            user=request.user,
            **serializer.validated_data
        )
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


# ─── Lead Preferences ────────────────────────────────────────────
class LeadPreferenceSettingApi(APIView):
    # permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        default_view  = serializers.CharField( required=False)
        sort_leads_by = serializers.CharField(required=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_lead_preference_service(
            user=request.user,
            **serializer.validated_data
        )
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


# ─── Security ────────────────────────────────────────────────────
class SecuritySettingApi(APIView):
    # permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        two_factor_authentication = serializers.BooleanField(required=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_security_service(
            user=request.user,
            **serializer.validated_data
        )
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': data, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({"data": data}, status=status.HTTP_200_OK)
    
    
    
# class TestingNotifiy(APIView):
#     class InputSerializer(serializers.Serializer):
#         tele_id=serializers.IntegerField(required=True)
#     def post(self, request):
#         serializer = self.InputSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = notification_reminder_services(
#             # user=request.user,
#             **serializer.validated_data
#         )
#         return Response({"data": data}, status=status.HTTP_200_OK)