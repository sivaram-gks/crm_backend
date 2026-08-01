
from django.urls import path
from .views.lead_views import ExportAllLeadsAdmin, FetchAllLeadsAdmin, AddNewLeadAdmin, FetchPipelineLeadsAdmin, GetFilterDropdownsAdmin, UploadLeadExcelAdmin, FetchLeadDetailsAdmin

urlpatterns = [
    path('fetch_all_leads_admin', FetchAllLeadsAdmin.as_view()),
    path('add_new_lead_admin', AddNewLeadAdmin.as_view()),  
    path('upload_lead_excel_admin', UploadLeadExcelAdmin.as_view()),
    path('export_all_leads_admin', ExportAllLeadsAdmin.as_view()),
    path('get_filter_dropdowns_admin', GetFilterDropdownsAdmin.as_view()),
    path('fetch_pipeline_leads_admin', FetchPipelineLeadsAdmin.as_view()),
    path('fetch_lead_details_admin', FetchLeadDetailsAdmin.as_view()),
]

