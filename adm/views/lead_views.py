from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from ..services.lead_services import (
    fetch_all_leads_admin, add_new_lead_admin, get_add_lead_dropdowns_admin,
    upload_lead_excel_admin, export_all_leads_admin, get_filter_dropdowns_admin,
    fetch_pipeline_leads_admin, fetch_lead_details_admin,
    get_mark_as_won_info_admin, mark_as_won_admin, get_mark_as_lost_info_admin, 
    mark_as_lost_admin, edit_lead_admin
)
from telecalling.tasks.api_log_task import api_history_log

@authentication_classes([])
@permission_classes([])
class FetchAllLeadsAdmin(APIView):
   
    class InputSerializers(serializers.Serializer):
        lead_filter_type = serializers.CharField(required=False, default="all")
        search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        tele_id = serializers.IntegerField(required=False, allow_null=True)
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        date_filter_type = serializers.CharField(required=False, default="all")
        pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        lead_source_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        course_name_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        priority_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        campaign_name_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        sort_by = serializers.CharField(required=False, default="-created_at")
        page = serializers.IntegerField(required=False, default=1)
        page_size = serializers.IntegerField(required=False, allow_null=True, default=1000)
        
    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = fetch_all_leads_admin(**serializer.validated_data)


        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"stats": result.get("stats"), "total": result.get("total")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response({"data": result}, status=status.HTTP_200_OK)



   
# -------------------------------------admin add new lead views------------------------------------------
    
@authentication_classes([])
@permission_classes([])
class AddNewLeadAdmin(APIView):
    """
    GET  -> Modal open aagum podhu Dropdowns tarum (Pipelines, Campaigns, Sources, Telecallers)
    POST -> Form Submit pannum podhu puthu lead-ah save pannum
    """
    class InputSerializers(serializers.Serializer):
        first_name = serializers.CharField(required=False, allow_blank=True)
        last_name = serializers.CharField(required=False, allow_blank=True)
        full_name = serializers.CharField(required=False, allow_blank=True)
        mobile_no = serializers.CharField(required=True)
        email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
        pipeline = serializers.CharField(required=False, default="Education")
        pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True, default=1)
        campaign_id = serializers.IntegerField(required=False, allow_null=True)
        campaign = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        lead_source_id = serializers.IntegerField(required=False, allow_null=True)
        source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
        enquiry_date = serializers.DateTimeField(required=False, allow_null=True)
        priority_id = serializers.IntegerField(required=False, default=4)
        
        
    def get(self, request):
        """Modal open aagum podhu Dropdowns edukka"""
        result = get_add_lead_dropdowns_admin()
        return Response({"data": result}, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        """Form Submit panni puthu lead-ah save panna"""
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = add_new_lead_admin(user=request.user, **serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': result,
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data": result}, status=status.HTTP_201_CREATED)




# ----------------------------upload lead excel file view------------------------------------------

@authentication_classes([])
@permission_classes([])
class UploadLeadExcelAdmin(APIView):
    """
    Admin Bulk Excel/CSV Lead Upload API (.csv, .xls, .xlsx).
    Parses file and inserts leads into telecalling_lead table.
    """
    parser_classes = (MultiPartParser, FormParser)
    class InputSerializers(serializers.Serializer):
        file = serializers.FileField(required=True)
    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data['file']
        result = upload_lead_excel_admin(file_obj=uploaded_file, user=request.user)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': {'file_name': uploaded_file.name, 'file_size': uploaded_file.size},
            'response_payload': result,
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({"data": result}, status=status.HTTP_201_CREATED)
    
    
    
    
# ------------------------------export_all_leads_admin-----------------------

@authentication_classes([])
@permission_classes([])
class ExportAllLeadsAdmin(APIView):
    """
    Admin Leads Page -> Export Button API.
    """
    class InputSerializers(serializers.Serializer):
        lead_filter_type = serializers.CharField(required=False, default="all")
        search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        tele_id = serializers.IntegerField(required=False, allow_null=True)
        from_date = serializers.DateField(required=False)
        to_date = serializers.DateField(required=False)
        date_filter_type = serializers.CharField(required=False, default="all")
        pipeline_stage_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        lead_source_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        course_name_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        priority_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        campaign_name_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        sort_by = serializers.CharField(required=False, default="-created_at")

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = export_all_leads_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status"), "total_exported": result.get("total_exported")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response({"data": result}, status=status.HTTP_200_OK)
    
    
    

# -------------------------------get_filter_dropdowns_admin-----------------------

@authentication_classes([])
@permission_classes([])
class GetFilterDropdownsAdmin(APIView):
    """
    Admin Leads Page -> Filter Modal Dropdowns API (Supports both GET & POST).
    """
    def get(self, request):
        result = get_filter_dropdowns_admin()
        return Response({"data": result}, status=status.HTTP_200_OK)

    def post(self, request):
        result = get_filter_dropdowns_admin()
        return Response({"data": result}, status=status.HTTP_200_OK)
    
    
    
    
# --------------------------------------fetch_pipeline_leads_admin----------------------------------

@authentication_classes([])
@permission_classes([])
class FetchPipelineLeadsAdmin(APIView):
    """
    Admin Pipeline View (Kanban Cards API).
    """
    class InputSerializers(serializers.Serializer):
        pipeline_id = serializers.IntegerField(required=False, default=1)
        search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        lead_source_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        campaign_name_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        assigned_to_id = serializers.IntegerField(required=False, allow_null=True, default=0)
        date_filter_type = serializers.CharField(required=False, default="all")
        from_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        to_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = fetch_pipeline_leads_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status"), "message": result.get("message")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)


# --------------------------------------fetch_lead_details_admin----------------------------------

@authentication_classes([])
@permission_classes([])
class FetchLeadDetailsAdmin(APIView):
    """
    Admin Lead Details & Activity Timeline Modal API.
    """
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = fetch_lead_details_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)
    
    
    
    
# ---------------------------get_mark_as_won_info_admin-----------------------------

@authentication_classes([])
@permission_classes([])
class GetMarkAsWonInfoAdmin(APIView):
    """
    Get Mark as Won Modal Details API (POST with Serializer Validation).
    """
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)

    def post(self, request):
        # 🔴 Validating lead_id via Serializer before proceeding
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        lead_id = serializer.validated_data.get("lead_id")
        result = get_mark_as_won_info_admin(lead_id)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)
    
    
    
    
# --------------------------------------mark_as_won_admin----------------------------------

@authentication_classes([])
@permission_classes([])
class MarkAsWonAdmin(APIView):
    """
    Submit Mark as Won Modal API.
    """
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)
        paid_through = serializers.CharField(required=False, default="Online")
        amount_paid = serializers.FloatField(required=False, default=0)
        is_full_payment = serializers.BooleanField(required=False, default=False)
        due_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        payment_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        next_followup = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        summary = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = mark_as_won_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status"), "message": result.get("message")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)
    
    
    


# ---------------------------get_mark_as_lost_info_admin, mark_as_lost_admin--------------------

@authentication_classes([])
@permission_classes([])
class GetMarkAsLostInfoAdmin(APIView):
    """
    Get Mark as Lost Modal Details API (POST).
    """
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        lead_id = serializer.validated_data.get("lead_id")
        result = get_mark_as_lost_info_admin(lead_id)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class MarkAsLostAdmin(APIView):
    """
    Submit Mark as Lost Modal API.
    """
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=False, allow_null=True)
        id = serializers.IntegerField(required=False, allow_null=True)
        stage = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        main_reason_id = serializers.IntegerField(required=False, allow_null=True)
        main_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        sub_reason_id = serializers.IntegerField(required=False, allow_null=True)
        sub_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        detailed_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = mark_as_lost_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status"), "message": result.get("message")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)
    
    
    
    

# --------------------------------------edit_lead_admin----------------------------------

@authentication_classes([])
@permission_classes([])
class EditLeadAdmin(APIView):
    """
    Admin Leads Page -> Edit Lead Modal Save API.
    """
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=False, allow_null=True)
        id = serializers.IntegerField(required=False, allow_null=True)
        first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        full_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        mobile_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        alt_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        email = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        created_at = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        enquiry_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        assigned_to = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        course_plan = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        course = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        pipeline = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        campaign = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        stage = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        tag = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        amount_paid = serializers.FloatField(required=False, allow_null=True)
        pending_amount = serializers.FloatField(required=False, allow_null=True)
        total_amount = serializers.FloatField(required=False, allow_null=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = edit_lead_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': result,
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)
    
    
    
    
