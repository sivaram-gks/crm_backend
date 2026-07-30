from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from ..services.file_services import *
from django.http import FileResponse
from rest_framework.decorators import authentication_classes, permission_classes
from ..tasks.api_log_task import api_history_log


class DailyReportApi(APIView):
    class InputSerializer(serializers.Serializer):
        id=serializers.IntegerField(required=True)

        
    def post(self,request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report=daily_report( **serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': report, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({'data': report}, status=status.HTTP_200_OK)



class SubmitDailyReportView(APIView):
    """API 1: Submit report - Store in DB"""
    class InputSerializers(serializers.Serializer):
        id = serializers.IntegerField(required=True)
        data = serializers.JSONField(required=False, default={})
        tomorrow_conversation = serializers.IntegerField(required=False, default=0)
        lead_for_tomorrow = serializers.IntegerField(required=False, default=0)
        own_message = serializers.CharField(required=False, default="")
    
    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        response_data = submit_daily_report(
            user=request.user,
            **serializer.validated_data
        )
        
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': response_data,
            'status_code': 200
        }
        api_history_log(log_data)
        
        return Response(response_data, status=status.HTTP_200_OK)

class DownloadDailyReportView(APIView):    
    def get(self, request):
        response_data = download_daily_reports(
            user=request.user
        )
        
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': "",
            'response_payload': response_data,
            'status_code': 200
        }
        api_history_log(log_data)
        
        return Response(response_data, status=status.HTTP_200_OK)