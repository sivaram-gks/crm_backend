from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from ..services.file_services import *
from ..tasks.api_log_task import api_history_log



class ExcelUpload(APIView):
    class InputSerializer(serializers.Serializer):
        leads= serializers.JSONField(required = True)
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        print('views',request.data)
        # 1. File check
        if not serializer.validated_data.get("leads"):
            return Response({"error": "File-ah upload pannunga (Key name: 'leads')"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. Service-ah call panrom
            report =lead_upload_excel(**serializer.validated_data)
            print('created file', report)
            log_data = {
            "user_id": request.user.id if request.user.id else None,
            "api_name": request.path,
            "method": request.method,
            "request_payload": serializer.validated_data,
            "response_payload": report,
            "status_code": 202,
            }
            api_history_log(log_data)
            
            if report:
                return Response({"message": report }, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Excel-la data edhum illa!"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print("Error:", str(e))
            return Response({"error": f"Error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        







class PreviewLeadExcel(APIView):
    class InputSerializer(serializers.Serializer):
        file = serializers.FileField(required=True)
 
    def post(self, request):
 
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        file_obj = serializer.validated_data["file"]
 
        allowed_extensions = (".csv", ".xlsx", ".xls")
        file_name_lower = file_obj.name.lower()
 
        if not file_name_lower.endswith(allowed_extensions):
            return Response(
                {"error": "Only .csv, .xlsx or .xls files are allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        try:
            report = preview_lead_excel(**serializer.validated_data)
        except Exception as e:
            return Response(
                {"error": f"Could not read the file. {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        log_data = {
            "user_id": request.user.id if request.user.id else None,
            "api_name": request.path,
            "method": request.method,
            "request_payload": {"file": file_obj.name},
            "response_payload": report,
            "status_code": 202,
        }
        api_history_log(log_data)
 
        return Response({"data": report}, status=status.HTTP_200_OK)


