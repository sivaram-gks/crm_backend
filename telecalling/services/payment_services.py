# from ..models import *
from ..models.leads import Lead
from ..models.paymentinfo import PaymentFollowUp,PaymentInfo,PaymentHistory 
from rest_framework.exceptions import APIException
from datetime import datetime, timedelta
from ..services.query_services import exec_raw_sql
from django.db import transaction

def fetch_all_payment(user,**data):
    try:
        id=user.id
        
        
        date_filter_type = data.get("date_filter_type", "year")
        from_date = data.get("from_date")
        to_date = data.get("to_date")
        
        today = datetime.now().date()

        # Logic for Daily, Weekly, Monthly, Yesterday
        if date_filter_type == "today":
            from_date = today
            to_date = today
        elif date_filter_type == "yesterday":
            from_date = today - timedelta(days=1)
            to_date = from_date
        elif date_filter_type == "weekly":
            from_date = today - timedelta(days=7)
            to_date = today
        elif date_filter_type == "monthly":
            from_date = today - timedelta(days=30)
            to_date = today
        elif date_filter_type == "year":
            from_date = "2026-01-01" 
            to_date = today
        elif date_filter_type=="custom":
            from_date=from_date
            to_date=to_date

   
        params = {
            "id": id,
            "from_date": str(from_date) if from_date else "",
            "to_date": str(to_date) if to_date else "",
            "filter_type": str(date_filter_type) if date_filter_type else "",
            "amount_stage_id": data.get("pending_amount_id") or 0,
            "course_name_id": data.get("course_name_id") or 0,
            "course_time_id": data.get("course_time_id") or 0,
            "course_plan_id": data.get("course_plan_id") or 0,
            "payment_stage": data.get("payment_stage_id") or 0
        }
        print(params)
        pay=exec_raw_sql("D_FETCH_ALL_PENDING_PAYMENTS",params)

        return pay
        
    except Exception as e:
        raise APIException(e)
    
    
 
def pending_payment_tile(user):
    try:
        id=user.id
        tile=exec_raw_sql("D_FETCH_PAYMENT_TILES",{"id":id})
        return tile   
    
    except Exception as e:
        raise APIException(e)



@transaction.atomic
def payment_details(user, **data):
    try:

        lead = Lead.objects.filter(id=data.get("lead_id")).first()

        if not lead:
            raise APIException("Lead not found")

        if not lead.course:
            raise APIException("Lead has no course assigned.")

        paid_amount = float(data.get("paid_amount", 0))
        total_fee = float(lead.course.course_fees)

        # ==========================================
        # CHECK EXISTING PAYMENT INFO
        # ==========================================

        payment_info = PaymentInfo.objects.filter(lead=lead).first()

        # ==========================================
        # FIRST PAYMENT
        # ==========================================

        if not payment_info:
            pending_amount = total_fee - paid_amount

            payment_info = PaymentInfo.objects.create(
                lead=lead,
                amount_paid=paid_amount,
                pending_amount=pending_amount,
                summary=data.get("notes"),
                created_by=str(user),
            )

        # ==========================================
        # UPDATE EXISTING PAYMENT
        # ==========================================

        else:
            total_paid = payment_info.amount_paid + paid_amount

            payment_info.amount_paid = total_paid
            payment_info.summary = data.get("notes")
            payment_info.updated_by = str(user)
            payment_info.save()

        # ==========================================
        # PAYMENT HISTORY ENTRY
        # ==========================================

        payment_history = PaymentHistory.objects.create(
            payment=payment_info,
            paid_amount=paid_amount,
            pending_amount=data.get("pending_amount"),
            due_stage_id=data.get("payment_status_id"),
            due_date=data.get("due_date"),
            notes=data.get("notes"),
            created_by=str(user),
        )


        # ==========================================
        # ✅ MARK EXISTING FOLLOWUP AS ATTENDED / COMPLETED
        # ==========================================

        if payment_info.pending_amount == 0 or payment_info.is_full_payment:
            PaymentFollowUp.objects.filter(
                payment__payment__lead=lead,
                is_attended=False
            ).update(
                is_attended=True,
                attended_at=datetime.now(),
                followup_status="Completed",
                updated_by=str(user)
            )
        else:
            existing_followup = PaymentFollowUp.objects.filter(
                payment__payment__lead=lead,
                is_attended=False,
                followup_status="Pending"
            ).order_by("-created_at").first()

            if existing_followup:
                existing_followup.is_attended = True
                existing_followup.attended_at = datetime.now()
                existing_followup.followup_status = "Completed"
                existing_followup.updated_by = str(user)
                existing_followup.save()

            if data.get("next_followup"):
                PaymentFollowUp.objects.create(
                    payment=payment_history,
                    followup_date=data.get("next_followup"),
                    created_by=str(user),
                )

        return "Payment Updated Successfully"

    except Exception as e:
        raise APIException(str(e))
    
    
    
def payment_history(user,**data):
    try:
        id=data.get("lead_id")
        lead = Lead.objects.filter(id=data.get("lead_id")).first()

        if not lead:
            raise APIException("Lead not found")
        print(lead)
        history=exec_raw_sql("D_FETCH_ONE_LEAD_PAYMENT_HISTORY",{"id":id})
        print(history)
        return history
        
    except Exception as e:
        raise APIException(e)
    
    

