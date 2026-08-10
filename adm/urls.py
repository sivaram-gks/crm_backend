from django.urls import path
from .views.lead_views import (
    ExportAllLeadsAdmin, FetchAllLeadsAdmin, AddNewLeadAdmin, 
    FetchPipelineLeadsAdmin, GetFilterDropdownsAdmin, UploadLeadExcelAdmin, 
    FetchLeadDetailsAdmin, GetMarkAsWonInfoAdmin, MarkAsWonAdmin, 
    GetMarkAsLostInfoAdmin, MarkAsLostAdmin, EditLeadAdmin
)
from .views.payment_views import (
    FetchAllPendingPaymentsAdmin, ExportPendingPaymentsAdmin,
    GetPendingPaymentFilterDropdownsAdmin
)
from .views.loss_lead_approval_views import (
    FetchLossLeadApprovalRequestsAdmin, GetLossLeadApprovalFilterDropdownsAdmin,
    ExportLossLeadApprovalRequestsAdmin, ActionLossLeadApprovalAdmin
)

urlpatterns = [
    path('fetch_all_leads_admin', FetchAllLeadsAdmin.as_view()),
    path('add_new_lead_admin', AddNewLeadAdmin.as_view()),  
    path('upload_lead_excel_admin', UploadLeadExcelAdmin.as_view()),
    path('export_all_leads_admin', ExportAllLeadsAdmin.as_view()),
    path('get_filter_dropdowns_admin', GetFilterDropdownsAdmin.as_view()),
    path('fetch_pipeline_leads_admin', FetchPipelineLeadsAdmin.as_view()),
    path('fetch_lead_details_admin', FetchLeadDetailsAdmin.as_view()),
    path('get_mark_as_won_info_admin', GetMarkAsWonInfoAdmin.as_view()),
    path('mark_as_won_admin', MarkAsWonAdmin.as_view()),
    path('get_mark_as_lost_info_admin', GetMarkAsLostInfoAdmin.as_view()),
    path('mark_as_lost_admin', MarkAsLostAdmin.as_view()),
    path('edit_lead_admin', EditLeadAdmin.as_view()),
    path('edit_lead', EditLeadAdmin.as_view()),
    
    # 💰 Pending Payments APIs
    path('fetch_all_pending_payments_admin', FetchAllPendingPaymentsAdmin.as_view()),
    path('export_pending_payments_admin', ExportPendingPaymentsAdmin.as_view()),
    path('get_pending_payment_filter_dropdowns_admin', GetPendingPaymentFilterDropdownsAdmin.as_view()),

    # 🛑 Loss Lead Approval Request APIs
    path('fetch_loss_lead_approval_requests_admin', FetchLossLeadApprovalRequestsAdmin.as_view()),
    path('get_loss_lead_approval_filter_dropdowns_admin', GetLossLeadApprovalFilterDropdownsAdmin.as_view()),
    path('export_loss_lead_approval_requests_admin', ExportLossLeadApprovalRequestsAdmin.as_view()),
    path('action_loss_lead_approval_admin', ActionLossLeadApprovalAdmin.as_view()),
]