from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from telecalling.views import api_history_log

from ..services.loss_lead_approval_services import (
    fetch_loss_lead_approval_requests_admin,
    get_loss_lead_approval_filter_dropdowns_admin,
    export_loss_lead_approval_requests_admin,
    action_loss_lead_approval_admin
)


@authentication_classes([])
@permission_classes([])
class FetchLossLeadApprovalRequestsAdmin(APIView):
    """
    POST & GET -> Loss Lead Approval Request Page Table Data & Summary API.
    """
    class InputSerializers(serializers.Serializer):
        search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        date_filter = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        date_filter_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        from_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        to_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        loss_reason_id = serializers.IntegerField(required=False, allow_null=True)
        assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
        course_id = serializers.IntegerField(required=False, allow_null=True)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True)
        campaign_id = serializers.IntegerField(required=False, allow_null=True)
        approval_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        sort_by = serializers.CharField(required=False, default="-updated_at")
        page = serializers.IntegerField(required=False, default=1)
        page_size = serializers.IntegerField(required=False, allow_null=True, default=250)

    def get(self, request):
        result = fetch_loss_lead_approval_requests_admin(**request.query_params.dict())
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = fetch_loss_lead_approval_requests_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user and request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status"), "total_count": result.get("data", {}).get("total_count")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class GetLossLeadApprovalFilterDropdownsAdmin(APIView):
    """
    GET & POST -> Filter Modal Dropdown Options API for Loss Lead Approval Page.
    """
    def get(self, request):
        result = get_loss_lead_approval_filter_dropdowns_admin()
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        result = get_loss_lead_approval_filter_dropdowns_admin()
        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class ExportLossLeadApprovalRequestsAdmin(APIView):
    """
    POST & GET -> Lime Green Excel Export API for Loss Lead Approval Requests Page.
    """
    class InputSerializers(serializers.Serializer):
        search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        date_filter = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        from_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        to_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        loss_reason_id = serializers.IntegerField(required=False, allow_null=True)
        assigned_to_id = serializers.IntegerField(required=False, allow_null=True)

    def get(self, request):
        result = export_loss_lead_approval_requests_admin(**request.query_params.dict())
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = export_loss_lead_approval_requests_admin(**serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class ActionLossLeadApprovalAdmin(APIView):
    """
    POST -> Action Buttons API for Loss Lead Approval Requests Page.
    Handles 3 Figma Actions: 'approve' (Green Tick), 'reject' (Red Cross), 'reassign' (Blue Refresh).
    """
    class InputSerializers(serializers.Serializer):
        lead_id = serializers.IntegerField(required=False, allow_null=True)
        id = serializers.IntegerField(required=False, allow_null=True)
        action_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        action = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
        can_retarget = serializers.BooleanField(required=False, default=True)
        remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        final_remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        detailed_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        comments = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = {**serializer.validated_data, **request.data}
        result = action_loss_lead_approval_admin(**payload)

        log_data = {
            'user_id': request.user.id if request.user and request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': result,
            'status_code': 200
        }
        api_history_log(log_data)

        return Response(result, status=status.HTTP_200_OK)
