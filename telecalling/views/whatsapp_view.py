# whatsapp meta code setup
from rest_framework.views import APIView
from rest_framework import serializers

from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.http import HttpResponse
from ..services.whatsapp_services import (whatsapp_lead_create,send_whatsapp_message)
from rest_framework.decorators import authentication_classes, permission_classes

# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def whatsapp_webhook(request):

#     # =========================
#     # ✅ 1. Verification (GET)
#     # =========================
#     if request.method == "GET":
#         mode = request.GET.get("hub.mode")
#         token = request.GET.get("hub.verify_token")
#         challenge = request.GET.get("hub.challenge")

#         if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
#             return HttpResponse(challenge)

#         return HttpResponse("Verification failed", status=403)

#     # =========================
#     # ✅ 2. Receive Messages (POST)
#     # =========================
#     try:
#         data = request.data
#         print("FULL DATA:", data)

#         entry = data.get("entry", [])
#         if not entry:
#             return Response({"status": "no entry"})

#         changes = entry[0].get("changes", [])
#         if not changes:
#             return Response({"status": "no changes"})

#         value = changes[0].get("value", {})
#         messages = value.get("messages", [])

#         if not messages:
#             return Response({"status": "no message"})

#         message = messages[0]

#         phone = message.get("from")
#         text = message.get("text", {}).get("body", "")
#         name = value.get("contacts", [{}])[0].get("profile", {}).get("name", "User")

#         if not text or not phone:
#             return Response({"error": "Invalid data"}, status=400)

#         message_body = text.lower()

#         print(f"User: {name}, Phone: {phone}, Message: {message_body}")

#         # =========================
#         # ✅ 3. Auto Reply Logic
#         # =========================

#         # Greeting
#         if "hi" in message_body or "hello" in message_body:
#             send_whatsapp_message(
#                 phone,
#                 f"Hi {name} 👋\nWelcome! How can I help you?\n\nType:\n1️⃣ Course\n2️⃣ Fees"
#             )

#         # Fees
#         elif "fees" in message_body:
#             send_whatsapp_message(
#                 phone,
#                 "💰 Our course fees start from ₹12,000.\nWould you like full details?"
#             )

#         # Python
#         elif "python" in message_body:
#             send_whatsapp_message(
#                 phone,
#                 "🐍 We offer Python + Django Fullstack course.\nDuration: 3 months."
#             )

#         # Course list
#         elif "course" in message_body:
#             send_whatsapp_message(
#                 phone,
#                 "📚 Available Courses:\n- Python\n- Django\n- React\n- Fullstack"
#             )

#         # Lead capture keywords
#         elif any(keyword in message_body for keyword in [
#             'course details', 'fees', 'syllabus', 'duration',
#             'django', 'react', 'fullstack', 'admission'
#         ]):
#             whatsapp_lead_create(
#                 name=name,
#                 mobile_no=phone,
#                 message=message_body
#             )

#             send_whatsapp_message(
#                 phone,
#                 f"✅ Thanks {name}!\nOur team will contact you soon 📞"
#             )

#         # Default reply
#         else:
#             send_whatsapp_message(
#                 phone,
#                 "🤖 Sorry, I didn't understand.\nPlease type:\n👉 course\n👉 fees"
#             )

#         return Response({"status": "success"})

#     except Exception as e:
#         print("Webhook Error:", e)
#         return Response({"error": "Something went wrong"}, status=500)






@authentication_classes([])
@permission_classes([]) 
class WhatsappWebhook(APIView):

    class InputSerializer(serializers.Serializer):
        hub_mode = serializers.CharField()
        hub_verify_token = serializers.CharField()
        hub_challenge = serializers.CharField()

    def get(self, request):
        data = {
            "hub_mode": request.GET.get("hub.mode"),
            "hub_verify_token": request.GET.get("hub.verify_token"),
            "hub_challenge": request.GET.get("hub.challenge"),
        }

        serializer = self.InputSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data

        if (
            validated["hub_mode"] == "subscribe"
            and validated["hub_verify_token"] == settings.WEBHOOK_VERIFY_TOKEN
        ):
            return HttpResponse(validated["hub_challenge"])

        return HttpResponse("Verification failed", status=status.HTTP_403_FORBIDDEN)
    
    
    def post(self,request):
        try:
                data = request.data
                print("FULL DATA:", data)

                entry = data.get("entry", [])
                if not entry:
                    return Response({"status": "no entry"})

                changes = entry[0].get("changes", [])
                if not changes:
                    return Response({"status": "no changes"})

                value = changes[0].get("value", {})
                messages = value.get("messages", [])

                if not messages:
                    return Response({"status": "no message"})

                message = messages[0]

                phone = message.get("from")
                text = message.get("text", {}).get("body", "")
                name = value.get("contacts", [{}])[0].get("profile", {}).get("name", "User")

                if not text or not phone:
                    return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

                message_body = text.lower()

                print(f"User: {name}, Phone: {phone}, Message: {message_body}")

                # =========================
                # ✅ 3. Auto Reply Logic
                # =========================

                # Greeting
                if "hi" in message_body or "hello" in message_body:
                    send_whatsapp_message(
                        phone,
                        f"Hi {name} 👋\nWelcome! How can I help you?\n\nType:\n1️⃣ Course\n2️⃣ Fees"
                    )

                # Fees
                elif "fees" in message_body:
                    send_whatsapp_message(
                        phone,
                        "💰 Our course fees start from ₹12,000.\nWould you like full details?"
                    )

                # Python
                elif "python" in message_body:
                    send_whatsapp_message(
                        phone,
                        "🐍 We offer Python + Django Fullstack course.\nDuration: 3 months."
                    )

                # Course list
                elif "course" in message_body:
                    send_whatsapp_message(
                        phone,
                        "📚 Available Courses:\n- Python\n- Django\n- React\n- Fullstack"
                    )

                # Lead capture keywords
                elif any(keyword in message_body for keyword in [
                    'course details', 'fees', 'syllabus', 'duration',
                    'django', 'react', 'fullstack', 'admission'
                ]):
                    print('lead')
                    whatsapp_lead_create(
                        name=name,
                        mobile_no=phone,
                        message=message_body
                    )
                    print('create')
                    send_whatsapp_message(
                        phone,
                        f"✅ Thanks {name}!\nOur team will contact you soon 📞"
                    )

                # Default reply
                else:
                    send_whatsapp_message(
                        phone,
                        "🤖 Sorry, I didn't understand.\nPlease type:\n👉 course\n👉 fees"
                    )

                return Response({"status": "success"})

        except Exception as e:
            print("Webhook Error:", e)
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        





































































































# ✅ Webhook Verification (Meta required)
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def verify_webhook(request):
#     mode = request.GET.get("hub.mode")
#     token = request.GET.get("hub.verify_token")
#     challenge = request.GET.get("hub.challenge")

#     if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
#         return JsonResponse(challenge, safe=False)
#     return JsonResponse("Verification failed", safe=False)


# ✅ Receive Messages from Meta
# @api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
# def whatsapp_webhook(request):

#     # ✅ Verification (GET)
#     if request.method == "GET":
#         mode = request.GET.get("hub.mode")
#         token = request.GET.get("hub.verify_token")
#         challenge = request.GET.get("hub.challenge")

#         if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
#             return HttpResponse(challenge)
#         return HttpResponse("Verification failed", status=403)

#     # ✅ Receive message (POST)
#     try:
#         data = request.data
#         print("FULL DATA:", request.data)

#         entry = data.get("entry", [])
#         if not entry:
#             return Response({"status": "no entry"})

#         changes = entry[0].get("changes", [])
#         if not changes:
#             return Response({"status": "no changes"})

#         value = changes[0].get("value", {})
#         messages = value.get("messages", [])

#         if not messages:
#             return Response({"status": "no message"})

#         message = messages[0]

#         phone = message.get("from")
#         text = message.get("text", {}).get("body", "")
#         name = value.get("contacts", [{}])[0].get("profile", {}).get("name", "User")

#         if not text or not phone:
#             return Response({"error": "Invalid data"}, status=400)

#         message_body = text.lower()

#         course_keywords = ['course details', 'fees', 'syllabus', 'duration', 'python', 'django', 'react', 'fullstack', 'admission']
#         is_course_query = any(keyword in message_body for keyword in course_keywords)

#         if is_course_query:
#             whatsapp_lead_create(
#                 name=name,
#                 mobile_no=phone,
#                 message=message_body
#             )

#         return Response({"status": "success"})

#     except Exception as e:
#         print("Webhook Error:", e)
#         return Response({"error": "Something went wrong"}, status=500)




#twilio whatsapp setup codes

# from twilio.request_validator import RequestValidator
# from django.conf import settings
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework import status
# from django.http import HttpResponse
# from ..services.whatsapp_services import whatsapp_lead_create

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def whatsapp_webhook(request):
#     # Twilio signature verify panna SID/Token back-end-la venum
    
#     user_name = request.data.get("ProfileName", "Unknown User")
#     message_body = request.data.get("Body", "").strip().lower()
#     from_number = request.data.get("From", "")

#     if not message_body or not from_number:
#         return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

#     phone = from_number.replace("whatsapp:", "").replace("+", "")
#     course_keywords = ['course details', 'fees', 'syllabus', 'duration', 'python', 'django', 'react', 'fullstack', 'admission']
#     is_course_query = any(keyword in message_body for keyword in course_keywords)

#     if is_course_query:
#             whatsapp_lead_create(
#                 name=user_name,
#                 mobile_no=phone,
#                 message=message_body
#             )
            
#             # English Format Reply
#             if 'fees' in message_body:
#                 reply_text = f"Hi {user_name}, thank you for inquiring about the fee structure. Our academic counselor will share the detailed fee break-up with you shortly."
#             elif any(kw in message_body for kw in ['python', 'django', 'react', 'fullstack']):
#                 reply_text = f"Hello {user_name}! Great choice. We have received your request for the Full Stack development syllabus. Our team will contact you soon."
#             else:
#                 reply_text = f"Thank you {user_name}! Your enquiry has been successfully registered. One of our representatives will get back to you within 24 hours."
#     else:
#             # General Help Reply
#         reply_text = f"Hi {user_name}, welcome to our Institute! To know more about our professional courses, please reply with 'Course Details' or 'Fees'."

#     response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
#     <Response>
#         <Message>{reply_text}</Message>
#     </Response>
#     """
#     return HttpResponse(response_xml, content_type="application/xml")