from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework import serializers, status
from rest_framework.response import Response

from ..services.payment_services import (
    fetch_all_pending_payments_admin, export_pending_payments_admin,
    get_pending_payment_filter_dropdowns_admin
)
from telecalling.tasks.api_log_task import api_history_log


@authentication_classes([])
@permission_classes([])
class GetPendingPaymentFilterDropdownsAdmin(APIView):
    """
    Pending Payments Page -> Filter Modal Dropdowns API.
    Supports GET & POST requests.
    """
    def get(self, request):
        result = get_pending_payment_filter_dropdowns_admin()
        return Response({"data": result}, status=status.HTTP_200_OK)

    def post(self, request):
        result = get_pending_payment_filter_dropdowns_admin()
        return Response({"data": result}, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class FetchAllPendingPaymentsAdmin(APIView):
    """
    Pending Payments Page -> 1st API: Fetch All Pending Payments & Summary Cards API.
    Supports both GET & POST requests.
    """
    class InputSerializers(serializers.Serializer):
        search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        date_filter = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        date_filter_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        from_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        to_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        sort_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        pipeline_id = serializers.IntegerField(required=False, allow_null=True)
        course_name_id = serializers.IntegerField(required=False, allow_null=True)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True)
        course_timing_id = serializers.IntegerField(required=False, allow_null=True)
        payment_stage_id = serializers.IntegerField(required=False, allow_null=True)
        pending_amount_range = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        page = serializers.IntegerField(required=False, default=1)
        limit = serializers.IntegerField(required=False, default=1000)

    def get(self, request):
        query_params = {
            "search": request.query_params.get("search"),
            "date_filter": request.query_params.get("date_filter") or request.query_params.get("date_filter_type"),
            "from_date": request.query_params.get("from_date"),
            "to_date": request.query_params.get("to_date"),
            "sort_by": request.query_params.get("sort_by"),
            "pipeline_id": request.query_params.get("pipeline_id"),
            "course_name_id": request.query_params.get("course_name_id"),
            "course_plan_id": request.query_params.get("course_plan_id"),
            "course_timing_id": request.query_params.get("course_timing_id"),
            "payment_stage_id": request.query_params.get("payment_stage_id"),
            "pending_amount_range": request.query_params.get("pending_amount_range"),
            "page": int(request.query_params.get("page", 1)),
            "limit": int(request.query_params.get("limit", 1000))
        }
        result = fetch_all_pending_payments_admin(**query_params)
        return Response({"data": result}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = fetch_all_pending_payments_admin(**serializer.validated_data)

        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data,
            'response_payload': {"status": result.get("status"), "total_count": result.get("total_count")},
            'status_code': 200
        }
        api_history_log(log_data)

        return Response({"data": result}, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class ExportPendingPaymentsAdmin(APIView):
    """
    Pending Payments Page -> Export Pending Payments Excel API.
    Lime Green Header (#84C225), Bold White Font, Center Alignment, Auto Widths.
    """
    class InputSerializers(serializers.Serializer):
        search = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        date_filter = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        date_filter_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        from_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        to_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        sort_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        pipeline_id = serializers.IntegerField(required=False, allow_null=True)
        course_name_id = serializers.IntegerField(required=False, allow_null=True)
        course_plan_id = serializers.IntegerField(required=False, allow_null=True)
        course_timing_id = serializers.IntegerField(required=False, allow_null=True)
        payment_stage_id = serializers.IntegerField(required=False, allow_null=True)
        pending_amount_range = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def get(self, request):
        query_params = {
            "search": request.query_params.get("search"),
            "date_filter": request.query_params.get("date_filter") or request.query_params.get("date_filter_type"),
            "from_date": request.query_params.get("from_date"),
            "to_date": request.query_params.get("to_date"),
            "sort_by": request.query_params.get("sort_by"),
            "pipeline_id": request.query_params.get("pipeline_id"),
            "course_name_id": request.query_params.get("course_name_id"),
            "course_plan_id": request.query_params.get("course_plan_id"),
            "course_timing_id": request.query_params.get("course_timing_id"),
            "payment_stage_id": request.query_params.get("payment_stage_id"),
            "pending_amount_range": request.query_params.get("pending_amount_range")
        }
        return export_pending_payments_admin(**query_params)

    def post(self, request):
        serializer = self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)

        return export_pending_payments_admin(**serializer.validated_data)
