from django.contrib import admin
from django.urls import path
# from .views.auth_views import *
from .views.user_views import * 
from .views.file_views import *
# from .views.whatsapp_view import *
from .views.dynamic_exprt_excel import *
from .views.dynamic_pdf import *
from .views.daily_report_views import *
from .views.lead_views import *
from .views.payment_views import *
from .views.dashboard_views import *
from .views.user_setting_views import *
from .views.export_views import *





urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_token',CreateToken.as_view()),
    path('api/token/refresh/', RefreshTokenView.as_view(), name='refresh_token'),
    path('create_user',CreateUser.as_view()),
    path('create_role',CreateRole.as_view()),
    path('get_select_option',GetSelectOption.as_view()),
    path('collection_query',CollectionQueryApi.as_view()),    #collection api
    path('lead_upload_excel',ExcelUpload.as_view()),
    path('lead_preview_excel',PreviewLeadExcel.as_view()),
    # path('export/<str:app_label>/<str:model_name>/', DynamicExportExcel.as_view()),  # excel formate change models
    # path('export/<str:table_name>/', DynamicExportExcel.as_view()),   # excel fromate change query datas
    # path('excel_export/', DynamicExportExcel.as_view()),
    # path('pdf_genrate/<str:table_name>/<int:id>/',DynamicPdfGenrate.as_view()),
    path('daily_report_api',DailyReportApi.as_view()),
    # path('download_daily_report',DownloadDailyReport.as_view()),
    path('add_new_lead',AddNewLead.as_view()),
    path('fetch_pipeline_lead',FetchPipelineLead.as_view()),            #pipeline all lead data fetch api
    path('fetch_all_leads',FetchAllLeads.as_view()),                    #fetch all leads datas api
    path('fetch_one_lead',FetchOneLead.as_view()),                      #fetch one lead data api
    path('fetch_lead_payment_history',PaymentHistoryApi.as_view()),     #fetch one lead payment histroy api
    path('fetch_lead_call_history',FetchCallHistoryApi.as_view()),      #fetch one lead all call history api
    path('fetch_one_lead_form',LeadFormDetail.as_view()),                #fetch one lead from update api
    path('fetch_one_loss_data',FetchOneLossLeadDetail.as_view()),
    path('loss_detail_update',LossLeadUpdateApi.as_view()),
    path('fetch_one_won_data',FetchOneWonLeadDetail.as_view()),
    path('won_detail_update',WonLeadUpdateApi.as_view()),
    path('call_connect_api',CallConnectForm.as_view()),
    path('call_disconncet_api',CallDisconnectForm.as_view()),
    path('fetch_all_payments',FetchAllPayment.as_view()),               #fetch all payment details api
    path('payment_details',PaymentDetails.as_view()),                   #one lead payment details form api
    path('pending_payment_tile',PendingPaymentTiles.as_view()),         #pending payment page tile card api
    path('dashboard_tile',DashboardTopTile.as_view()),                  #dashborad page tile card api with date filter
    path('pipeline_funnel',FetchPipelineFunnel.as_view()),              #dashboard page pipeline funnel fetch api 
    path('tele_performance',FetchTelePerformance.as_view()),            #tele performance,enrolement ,lost reasons data show in api     
    path('add_course',AddCourseDetails.as_view()),                      #add new course details api
    path('update_course_count',UpdateCourse.as_view()),                 #update course details api
    
    
    path('get_all_settings',GetAllSettingsApi.as_view()),               # tele setting page all datas api
    path('notification_api',NotificationSettingApi.as_view()),          # tele notification update api
    path('followup_update_api',FollowUpSettingApi.as_view()),           #
    path('call_setting_update_api',CallerSettingApi.as_view()),
    path('message_Setting_api',MessagingSettingApi.as_view()),
    path('note_setting_api',NotesSettingApi.as_view()),
    path('lead_preference_api',LeadPreferenceSettingApi.as_view()),
    path('tw_fa_api',SecuritySettingApi.as_view()),
    
    path('dropdown_cate_create',CreateDropdownCate.as_view()),
    path('create_dropdown',CreateDropdownSub.as_view()),
    path('get_selected_option',GetSelectedOption.as_view()),
    path('disconnect_select_tag',CallDisconnectSelectTag.as_view()),
    path('mark_notification_read',MarkNotificationRead.as_view()),
    path('generate_otp',GenerateOtpView.as_view()),
    path('get_export_column',ExportColumnsView.as_view()),
    path('export_json_data',ExportData.as_view()),     #export excel code 
    path('dashboard/pdf-data/', GetDashboardPDFData.as_view(), name='dashboard-pdf-data'),
    path('daily-report/submit', SubmitDailyReportView.as_view(), name='daily-report-submit'),
    
    # API 2: Download report - Get report data
    path('daily-report/download', DownloadDailyReportView.as_view(), name='daily-report-download'),
    path('add',Coursename.as_view())

]


