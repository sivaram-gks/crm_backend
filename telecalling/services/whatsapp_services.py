#meta whatsapp code setup 

import requests
from django.conf import settings
from ..models import Lead, User


def assign_telecaller():
    telecallers = list(User.objects.filter(role__name="telecaller"))
    if not telecallers:
        return None

    last_lead = Lead.objects.exclude(assigned_to=None).order_by('-id').first()

    if not last_lead or last_lead.assigned_to not in telecallers:
        return telecallers[0]

    try:
        last_index = telecallers.index(last_lead.assigned_to)
        next_index = (last_index + 1) % len(telecallers)
        return telecallers[next_index]
    except ValueError:
        return telecallers[0]


# ✅ Meta WhatsApp send function
def send_whatsapp_message(phone, message):
    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print('res',response.json())
    return response.json()


def whatsapp_lead_create(**data):
    mobile_no = data.get("mobile_no")
    message = data.get("message")
    name = data.get("name", "Unknown")

    lead = Lead.objects.filter(mobile_no=mobile_no).first()

    if lead:
        if not lead.full_name:
            lead.full_name = name
            lead.save()
        return "Already exists"

    telecaller = assign_telecaller()

    # ✅ Create Lead
    new_lead = Lead.objects.create(
        full_name=name,
        mobile_no=mobile_no,
        lead_source="WhatsApp",
        current_status="New Enquiry",
        pipeline_stage="Working",
        priority="Warm",
        assigned_to=telecaller
    )

    # ✅ Send message via Meta API
    if telecaller:
        try:
            send_whatsapp_message(
                phone=mobile_no,
                message=f"Hi {name}, ungaluku help panna namma counselor {telecaller.username} assign aagi irukkaru. He will call you soon!"
            )
        except Exception as e:
            print(f"Meta Send Error: {e}")

    return "Lead Created"











































































































































#twilio service code setup working

# from twilio.rest import Client
# from django.conf import settings
# from ..models import Lead, User

# def get_twilio_client():
#     return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# def assign_telecaller():
#     # User model-la 'is_active' field irundha atha filter-la add pannikonga
#     telecallers = list(User.objects.filter(role__name="telecaller"))
#     if not telecallers:
#         return None

#     last_lead = Lead.objects.exclude(assigned_to=None).order_by('-id').first()

#     if not last_lead or last_lead.assigned_to not in telecallers:
#         return telecallers[0]

#     try:
#         last_index = telecallers.index(last_lead.assigned_to)
#         next_index = (last_index + 1) % len(telecallers)
#         return telecallers[next_index]
#     except ValueError:
#         return telecallers[0]

# def whatsapp_lead_create(**data):
#     mobile_no = data.get("mobile_no")
#     message = data.get("message")
#     name = data.get("name", "Unknown")

#     lead = Lead.objects.filter(mobile_no=mobile_no).first()

#     if lead:
#         if not lead.full_name:
#             lead.full_name = name
#             lead.save()
#         return "Already exists"

#     telecaller = assign_telecaller()
    
#     # Lead Create
#     new_lead = Lead.objects.create(
#         full_name=name,
#         mobile_no=mobile_no,
#         lead_source="WhatsApp",
#         current_status="New Enquiry",
#         pipeline_stage="Working",
#         priority="Warm",
#         assigned_to=telecaller
#     )

#     # --- TWILIO CLIENT USE PANRA IDAM ---
#     # Lead create aanathum, system-e oru message anuppum (Not using TwiML here)
#     if telecaller:
#         try:
#             client = get_twilio_client()
#             client.messages.create(
#                 from_=settings.TWILIO_WHATSAPP_NUMBER,
#                 body=f"Hi {name}, ungaluku help panna namma counselor {telecaller.username} assign aagi irukkaru. He will call you soon!",
#                 to=f"whatsapp:+{mobile_no}"
#             )
#         except Exception as e:
#             print(f"Twilio Send Error: {e}")

#     return "Lead Created"