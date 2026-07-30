from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.two_fa_service import *

class Enable2FAView(APIView):
    def post(self, request):
        data = generate_2fa_secret(request.user)
        return Response(data)


class Verify2FAView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        success, message = verify_2fa_otp(request.user, otp)

        if success:
            return Response({"message": message})
        return Response({"error": message}, status=400)


class Disable2FAView(APIView):
    def post(self, request):
        success, message = disable_2fa(request.user)

        if success:
            return Response({"message": message})
        return Response({"error": message}, status=404)


class Login2FAVerifyView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        success, message = verify_login_otp(request.user, otp)

        if success:
            return Response({"message": message})
        return Response({"error": message}, status=400)