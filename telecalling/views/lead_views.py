from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from ..services.lead_services import *
from rest_framework.decorators import authentication_classes, permission_classes


class FetchAllLeads(APIView):
    class InputSerializers(serializers.Serializer):
        # tele_id=serializers.IntegerField(required=True)
        lead_filter_type=serializers.CharField(required=False)
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        date_filter_type = serializers.CharField(required=False, default="year") 
        
        pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        lead_source_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        course_name_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        priority_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        payment_status= serializers.IntegerField(required=False, allow_null=True,default=0)
        campaign_name_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead=fetch_leads(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': lead, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data":lead},status=status.HTTP_201_CREATED)
    
    



@authentication_classes([])
@permission_classes([])   
class UpdateCourse(APIView):
    class InputSerializers(serializers.Serializer):
        id=serializers.IntegerField(required=True)
        count=serializers.IntegerField(required=True)
        
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead=course_count(**serializer.validated_data)
        return Response({"data":lead},status=status.HTTP_201_CREATED)        
 
class AddNewLead(APIView):   
    class InputSerializers(serializers.Serializer):
        full_name=serializers.CharField(required=False,allow_null=True,allow_blank=True)
        mobile=serializers.CharField(required=True)
        campaign_id=serializers.IntegerField(required=False)
        enquiry_date=serializers.DateField(required=False,allow_null=True)
        
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead=add_new_lead(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': lead, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data":lead},status=status.HTTP_201_CREATED)      
   
   
    
class FetchPipelineLead(APIView):
    class InputSerializers(serializers.Serializer):
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        date_filter_type = serializers.CharField(required=False, default="today")
        
        pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        lead_source_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        course_name_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        priority_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True,default=0)
        payment_status = serializers.CharField(required=False, allow_null=True,default=0)
        followup_status = serializers.CharField(required=False, allow_blank=True, allow_null=True,default=0)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = fetch_pipeline_leads(user=request.user, **serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': lead,
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data": lead}, status=status.HTTP_202_ACCEPTED)


@authentication_classes([])
@permission_classes([])   
class GetSelectedOption(APIView):
    class InputSerializers(serializers.Serializer):
        dropdown_category=serializers.CharField(required=True)
        filter_id=serializers.CharField(required=False,allow_null=True,allow_blank=True)
        course_name_id=serializers.CharField(required=False,allow_null=True,allow_blank=True)        
        
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead=get_selected_option(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': lead, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":lead},status=status.HTTP_202_ACCEPTED)  







class LeadFormDetail(APIView):
    class InputSerializers(serializers.Serializer):
        # basic
        lead_id=serializers.IntegerField(required=True)
        fullname=serializers.CharField(required=False,allow_null=True)
        mobile=serializers.CharField(required=False,allow_null=True)
        alternative_mobile=serializers.CharField(required=False,allow_null=True,allow_blank=True)
        email=serializers.EmailField(required=False,allow_null=True,allow_blank=True)
        location=serializers.CharField(required=False,allow_null=True,allow_blank=True)
        education_id=serializers.IntegerField(required=False,allow_null=True)
        passed_out_year=serializers.CharField(required=False,allow_null=True,allow_blank=True)
        experience=serializers.CharField(required=False,allow_null=True,allow_blank=True)
        
        # lead 
        enquiry_date=serializers.DateTimeField(required=False,allow_null=True)
        current_status=serializers.CharField(required=False,allow_null=True)
        lead_source_id=serializers.IntegerField(required=False,allow_null=True)
        campaign_name_id=serializers.IntegerField(required=False,allow_null=True)
        # course_id=serializers.IntegerField(required=False,allow_null=True)
        course_plan_id=serializers.IntegerField(required=False,allow_null=True)
        course_name_id=serializers.IntegerField(required=False,allow_null=True)
        course_timing_id=serializers.IntegerField(required=False,allow_null=True)
        preferred_timing_id=serializers.IntegerField(required=False,allow_null=True)
        
        # pipeline
        pipeline_stage_id=serializers.IntegerField(required=False,allow_null=True)
        priority_id=serializers.IntegerField(required=False,allow_null=True)
        
        # payment info
        amount_paid=serializers.FloatField(required=False,allow_null=True)
        pending_amount=serializers.FloatField(required=False,allow_null=True)
        is_full_payment=serializers.BooleanField(required=False,allow_null=True)
        due_date=serializers.DateTimeField(required=False,allow_null=True)
        payment_status_id=serializers.IntegerField(required=False,allow_null=True)
        # next_followup=serializers.DateTimeField(required=False,allow_null=True)
        notes=serializers.CharField(required=False,allow_null=True)
        
        # referal
        referal_list=serializers.JSONField(required=False)

    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead=lead_form_details(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': lead, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data":lead},status=status.HTTP_201_CREATED)  
    
    
class FetchOneLead(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id=serializers.IntegerField(required=True)
        
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead=fetch_one_lead(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': lead, 
            'status_code': 202
        }
        api_history_log(log_data)
        return Response({"data":lead},status=status.HTTP_202_ACCEPTED)     




     
class FetchCallHistoryApi(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id=serializers.IntegerField(required=True)
        
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead=fetch_call_history(user=request.user,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': lead, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data":lead},status=status.HTTP_201_CREATED)     



    
class CallConnectForm(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)
        connection_status = serializers.CharField(required=True)
        call_duration = serializers.CharField(required=False)
        stage_id = serializers.CharField(required=False)
        select_tag_id = serializers.CharField(required=False,allow_null=True)
        next_followup = serializers.DateTimeField(required=False)
        call_summary = serializers.CharField(required=False,allow_blank=True)
        upload_record = serializers.FileField(required=False)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = call_connect_api(user=request.user, **serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': result, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data": result}, status=status.HTTP_201_CREATED)



class CallDisconnectSelectTag(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)  
    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = call_disconnect_select_api(user=request.user, **serializer.validated_data) 
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': result, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data": result}, status=status.HTTP_201_CREATED)

class CallDisconnectForm(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)      
        select_tag_id = serializers.CharField(required=False)
        next_followup = serializers.DateTimeField(required=False,allow_null=True)
        retry_notes = serializers.CharField(required=False,allow_null=True,allow_blank=True)
        other_reason=serializers.CharField(required=False,allow_null=True,allow_blank=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = call_disconnect_api(user=request.user, **serializer.validated_data) 
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': result, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data": result}, status=status.HTTP_201_CREATED)
 
 
 

class FetchOneLossLeadDetail(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)    
    def post(self,request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = fetch_one_loss_detail(user=request.user, **serializer.validated_data)  
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': {}, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data": result}, status=status.HTTP_201_CREATED)
     
     

class LossLeadUpdateApi(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)    
        pipeline_stage_id=serializers.IntegerField(required=True)
        priority_id=serializers.IntegerField(required=False)
        enquiry_date=serializers.DateTimeField(required=False)
        follow_up_days=serializers.CharField(required=True)
        main_reason_id=serializers.IntegerField(required=True)
        # sub_reason=serializers.CharField(required=True)
        loss_reason=serializers.CharField(required=True,allow_blank=True)
        
    def post(self,request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = loss_detail_update(user=request.user, **serializer.validated_data)  
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': result, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data": result}, status=status.HTTP_201_CREATED)



class FetchOneWonLeadDetail(APIView):
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)    
    def post(self,request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = fetch_one_won_detail(user=request.user, **serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload':  serializer.validated_data, 
            'response_payload': result, 
            'status_code': 201
        }
        api_history_log(log_data)  
        return Response({"data": result}, status=status.HTTP_201_CREATED)

class WonLeadUpdateApi(APIView):
    class InputSerilaizers(serializers.Serializer):
        lead_id=serializers.IntegerField(required=True)
        pipeline_stage_id=serializers.IntegerField(required=True)
        priority_id=serializers.IntegerField(required=False)
        paid_amount=serializers.IntegerField(required=True)
        pending_amount=serializers.IntegerField(required=False)
        due_date=serializers.DateField(required=False)
        # next_followup=serializers.DateTimeField(required=False)
        notes=serializers.CharField(required=False)
        
    def post(self,request):
        serializer=self.InputSerilaizers(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment=won_detail_update(request.user,**serializer.validated_data)
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