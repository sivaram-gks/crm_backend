from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

from adm.services.performance_services import (
    fetch_performance_overview_admin,
    assign_users_to_team_admin,
    update_telecaller_target_admin,
    get_performance_filter_dropdowns_admin,
    export_performance_overview_admin
)

@authentication_classes([])
@permission_classes([])
class FetchPerformanceOverviewAdmin(APIView):
    def post(self, request):
        result = fetch_performance_overview_admin(request.data)
        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class AssignUsersToTeamAdmin(APIView):
    def post(self, request):
        admin_user = request.user if getattr(request.user, 'is_authenticated', False) else None
        result = assign_users_to_team_admin(request.data, admin_user=admin_user)
        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class UpdateTelecallerTargetAdmin(APIView):
    def post(self, request):
        admin_user = request.user if getattr(request.user, 'is_authenticated', False) else None
        result = update_telecaller_target_admin(request.data, admin_user=admin_user)
        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class GetPerformanceFilterDropdownsAdmin(APIView):
    def get(self, request):
        result = get_performance_filter_dropdowns_admin()
        return Response(result, status=status.HTTP_200_OK)


@authentication_classes([])
@permission_classes([])
class ExportPerformanceOverviewAdmin(APIView):
    def post(self, request):
        return export_performance_overview_admin(request.data)
