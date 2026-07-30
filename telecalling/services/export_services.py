from .query_services import *
from ..services.dashboard_services import *
from ..services.lead_services import *
from ..services.payment_services import *
from rest_framework.response import Response


# config/export_columns.py

EXPORT_COLUMNS_CONFIG = {
    "lead": {
        "s_no":"S No",
        "id":"Id",
        "full_name": "Name",
        "mobile_no": "Mobile",
        "email":"Email",
        "tag":"Priority",
        "stage":"Pipeline Stage",
        "source": "Lead Source",
        "campaign_name":"Campaign Name",
        "course_name": "Course Name",
        "course_plan": "Course Plan",
        "course_timing": "Course Time",
        "pending_amount":"Pending Amount",
        "total_amount": "Total Amount",
        "enquiry_date": "Enquiry Date",
        "called_at":"Called At"
    },
    "pending-payments": {
        "s_no":"S No",
        "id":"Id",
        "full_name": "Lead Name",
        "mobile_no": "Mobile Number",
        "course_name": "Course Name",
        "course_plan": "Course Plan",
        "course_timing": "Course Time",
        "batch_name":"Batch Name",
        "enquiry_date":"Enquiry Date",
        "pending_amount": "Pending Amount",
        "next_follow_up":"Next Follow-Up",
        "amount_paid":"Amount Paid",
        "due_status":"Due Status",
        "payment_status_text": "Payment Status",
        "last_conversation": "Last Conversation",
        "due_date": "Due Date",
    },
    "pipeline-lead": {
        "s_no":"S No",
        "id":"Id",
        "name": "Lead Name",
        "mobile": "Mobile Number",
        "course_name": "Course Name",
        "course_plan": "Course Plan",
        "course_timing": "Course Time",
        "priority":"Priority",
         "source": "Lead Source",
         "timing":"Timing",
         "preferred_time":"Preferred Time",
         "date":"Date",
         "call_back":"Call Back",
         "attempts":"Attempts",
         "last_tried":"Last Tried",
         "retry_after":"Retry After",
         "tag":"Tag",
      "pending_amount":"Pending Amount",
      "amount_paid":"Amount Paid",
        "total_fees": "Total Amount",
        "payment_status": "Payment Status",
        "enquiry_date": "Enquiry Date",
        "called_at":"Called At",
        "due_date": "Due Date",
         "overdue_days":"Overdue Days",
         "attempts":"Attempts",
         "last_tried":"Last Tried",
         "lost_reason":"Lost Reason",
         "sub_reason":"Sub Reason",
         "follow_up_days":"FollowUp Days"
         
         
         
    },
}

def get_export_columns(**data):
    try:
        
        print(data.get("page"))
        
        columns_config = EXPORT_COLUMNS_CONFIG.get(data.get("page"))

        print(columns_config)
        if not columns_config:
            return Response({"message": "Invalid page"}, status=400)

        # Convert to list of {key, label} for frontend checkbox rendering
        columns = [
            {"key": key, "label": label}
            for key, label in columns_config.items()
        ]

        return columns
    except Exception as e:
        raise APIException(str(e))
    



def filter_columns_recursive(node, selected_columns):
    """
    Recursively walk through ANY nested structure (dict/list).
    Structure (keys, nesting) remains exactly same as original response.
    Only record dicts (has 'id' and 'name') get filtered to selected columns,
    and only if that column actually exists in the record.
    """
    if isinstance(node, dict):
        # Check if this dict looks like an actual record row
        if "id" in node and "name" in node:
            # Keep only selected columns that actually exist in this record
            return {col: node.get(col) for col in selected_columns if col in node}
        else:
            # Not a record - recurse into values, keep same structure/keys
            return {
                key: filter_columns_recursive(value, selected_columns)
                for key, value in node.items()
            }

    elif isinstance(node, list):
        return [filter_columns_recursive(item, selected_columns) for item in node]

    else:
        # Primitive value (string, int, None, etc.) - return as is
        return node
    
def get_export_data(user, **data):
    try:
        page = data.get("page")
        selected_columns = data.get("columns")

        print(page)
        print(selected_columns)

        # Step 1: Validate page + selected columns
        valid_columns = EXPORT_COLUMNS_CONFIG.get(page)

        if not valid_columns:
            return Response({"message": "Invalid page"}, status=400)

        invalid_cols = [c for c in selected_columns if c not in valid_columns]
        if invalid_cols:
            return Response(
                {"message": f"Invalid columns: {invalid_cols}"}, status=400
            )

        # Step 2: Fetch data based on page condition
        if page == "lead":
            report_data = fetch_leads(user=user, **data)

        elif page == "pending-payments":
            report_data = fetch_all_payment(user=user, **data)

        elif page == "pipeline-lead":
            report_data = fetch_pipeline_leads(user=user, **data)

        else:
            return Response({"message": "Invalid page"}, status=400)

        filtered_data = filter_columns_recursive(report_data, selected_columns)
        # print(filtered_data)
        return filtered_data

    except Exception as e:
        raise APIException(str(e))