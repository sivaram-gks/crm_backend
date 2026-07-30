from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from ..services.dashboard_services import *
from ..tasks.api_log_task import api_history_log


class DashboardTopTile(APIView):
    class InputSerilaizers(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        filter_type = serializers.CharField(required=False, default="monthly") 
    
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        card=dashboard_top_tile(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': card, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":card},status=status.HTTP_202_ACCEPTED)
   
   
   
    
class FetchPipelineFunnel(APIView):
    class InputSerilaizers(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        filter_type = serializers.CharField(required=False, default="year") 
    
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        card=fetch_pipeline_funnel(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': card, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":card},status=status.HTTP_202_ACCEPTED)
        
        
    
    
        
class FetchTelePerformance(APIView):
    class InputSerilaizers(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        filter_type = serializers.CharField(required=False, default="year") 
    
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        card=fetch_dashboard_analytics(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': card, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":card},status=status.HTTP_202_ACCEPTED)
        
        

class GetDashboardPDFData(APIView):
    """
    API to get dashboard data for PDF creation
    Returns only the data structure needed for PDF
    """
    class InputSerializers(serializers.Serializer):
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        filter_type = serializers.CharField(required=False, default="year") 
    
    def post(self, request):
        try:
            serializer = self.InputSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get dashboard data for PDF
            dashboard_data = get_dashboard_pdf_data(
                user=request.user, 
                **serializer.validated_data
            )
            print('dashbora',dashboard_data)
            
            # Log the API call
            log_data = {
                'user_id': request.user.id if request.user.id else None,
                'api_name': request.path,
                'method': request.method,
                'request_payload': serializer.validated_data, 
                'response_payload': dashboard_data, 
                'status_code': 200
            }
            api_history_log(log_data)
            print('close')
            # Return only the data
            return Response({"data":dashboard_data},status=status.HTTP_202_ACCEPTED)
                
            
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddCourseDetails(APIView):
    class InputSerilaizers(serializers.Serializer):
        course_name_id=serializers.IntegerField(required=True)
        course_plan_id=serializers.IntegerField(required=True)
        course_time_id=serializers.CharField(required=True)
        fees=serializers.FloatField(required=True)
        start_date=serializers.DateField(required=True)
        total_seat=serializers.IntegerField(required=True)
        
    
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        card=add_course_details(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': card, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":card},status=status.HTTP_202_ACCEPTED)
    
    

class Coursename(APIView):
    class InputSerilaizers(serializers.Serializer):
        name=serializers.CharField(required=True)
        
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        card=add_course(user=request.user,**serializer.validated_data)
        return Response({"data":card},status=status.HTTP_202_ACCEPTED)
    
    
    

class MarkNotificationRead(APIView):
    class InputSerilaizers(serializers.Serializer):
        notification_id=serializers.IntegerField(required=True)
        
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        card=mark_notification_read(user=request.user,**serializer.validated_data)
        return Response({"data":card},status=status.HTTP_202_ACCEPTED)