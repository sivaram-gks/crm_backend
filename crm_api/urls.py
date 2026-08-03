from django.conf.urls.static import static  # 👈 இங்கதான் '.static' சேர்க்கப்பட்டுள்ளது!
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from telecalling.views.whatsapp_view import *

from django.http import HttpResponse

urlpatterns = [
    path('', lambda request: HttpResponse("CRM API Backend Server Running Successfully!")),
    path('admin/', admin.site.urls),
    path('telecalling/', include('telecalling.urls')),

    # ✅ message receive (POST)
    path('api/whatsapp/webhook/', WhatsappWebhook.as_view()),
    
    path('adm/', include('adm.urls')),  
]

# Media Files Path Routing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)