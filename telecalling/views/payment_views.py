from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from ..services.payment_services import *
from rest_framework.decorators import authentication_classes, permission_classes
from ..tasks.api_log_task import api_history_log



class FetchAllPayment(APIView):
    class InputSerilaizers(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        date_filter_type = serializers.CharField(required=False, default="year") 
        course_name_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        course_time_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        payment_stage_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        pending_amount_id = serializers.CharField(required=False, allow_null=True,default=0)
    
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment=fetch_all_payment(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': payment, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":payment},status=status.HTTP_202_ACCEPTED)
    
  
  
class PendingPaymentTiles(APIView):
    def get (self,request):
        tile=pending_payment_tile(user=request.user)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  {}, 
            'response_payload': {}, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":tile},status=status.HTTP_202_ACCEPTED)
            
  
  
  
class PaymentDetails(APIView):
    class InputSerilaizers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)
        paid_amount = serializers.IntegerField(required=True)
        pending_amount = serializers.IntegerField(required=False)
        due_date = serializers.DateField(required=False, allow_null=True)
        payment_status=id=serializers.CharField(required=False)
        next_followup = serializers.DateTimeField(required=False, allow_null=True)
        notes = serializers.CharField(required=False, allow_blank=True)

        def to_internal_value(self, data):
            data = data.copy()

            for key, value in data.items():
                if value == "":
                    data[key] = None

            return super().to_internal_value(data)
        
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment=payment_details(request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': payment, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":payment},status=status.HTTP_202_ACCEPTED)
    

class PaymentHistoryApi(APIView):
    class InputSerilaizers(serializers.Serializer):
        lead_id=serializers.IntegerField(required=True)
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        history=payment_history(request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': history, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":history},status=status.HTTP_202_ACCEPTED)