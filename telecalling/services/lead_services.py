# from ..models import *
from ..models.courses import Course
from ..models.leads import Lead
from ..models.paymentinfo import PaymentInfo,PaymentFollowUp
from rest_framework.exceptions import APIException
from datetime import datetime, timedelta
from django.utils import timezone
from ..services.query_services import exec_raw_sql
from ..tasks import *
from django.utils.dateparse import parse_datetime
from django.db.models import F
from  ..tasks.course_task import *

def fetch_leads(user,**data):
    try: 
        # id=data.get("tele_id")
        id=user.id
        lead_filter_type=data.get("lead_filter_type")
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
            from_date = today.replace(day=1)
            to_date = today
        elif date_filter_type == "year":
            from_date = "2026-01-01" 
            to_date = today
        elif date_filter_type=="custom":
            from_date=from_date
            to_date=to_date

   
        params = {
            "id":id,
            "filter_type": f"'{lead_filter_type}'" if lead_filter_type else "NULL" ,
            "from_date": f"'{from_date} 00:00:00'" if from_date else "NULL",
            "to_date": f"'{to_date} 23:59:59'" if to_date else "NULL",
            "date_filter":str(date_filter_type),
            "pipeline_stage_id": data.get("pipeline_stage_id") or 0,
            "campaign_id": data.get("campaign_name_id") or 0,
            "lead_source_id": data.get("lead_source_id") or 0,
            "course_name_id": data.get("course_name_id") or 0,
            "priority_id": data.get("priority_id") or 0,
            "course_plan_id": data.get("course_plan_id") or 0,
            "payment_status": data.get("payment_status") or 0,
            "followup_status": data.get("followup_status") or "NULL",
        }
        # params = {
        #     "id":id,
        #     "filter_type": f"'{filter_type}'" if filter_type else "NULL" 
        # }
        print(params)
        lead=exec_raw_sql("D_FETCH_ALL_LEADS_DATA",params)
        count=exec_raw_sql("D_FETCH_ALL_LEAD_LABEL_COUNT",params)
        # print(count)
        # print(lead)
        return lead,count
    except Exception as e:
        raise APIException(e)
        
      
def fetch_pipeline_leads(user, **data):
    try:
        filter_type = data.get("date_filter_type", "year")

        from_date = data.get("from_date")
        to_date = data.get("to_date")

        today = datetime.now().date()
        ref_date = data.get("ref_date", today)

        if filter_type == "today":
            from_date = today
            to_date = today
        elif filter_type == "yesterday":
            from_date = today - timedelta(days=1)
            to_date = from_date
        elif filter_type == "weekly":
            from_date = today - timedelta(days=7)
            to_date = today
        elif filter_type == "monthly":
            from_date = today.replace(day=1)
            to_date = today
        elif filter_type == "year":
            from_date = today - timedelta(days=365)
            to_date = today
        elif filter_type == "custom":
            from_date = from_date
            to_date = to_date

        params = {
            "id": user.id,
            "from_date": str(from_date),
            "to_date": str(to_date),
            "filter_type": filter_type,
            "pipeline_stage_id": data.get("pipeline_stage_id"),
            "lead_source_id": data.get("lead_source_id"),
            "course_name_id": data.get("course_name_id"),
            "priority_id": data.get("priority_id"),
            "course_plan_id": data.get("course_plan_id"),
            "payment_status": data.get("payment_status") ,
            "followup_status": data.get("followup_status") or "",
        }
        print(params)
        lead = exec_raw_sql("D_FETCH_PIPELINE_STATGE_LEADS", params)
        

        return lead
    except Exception as e:
        raise APIException(e)
    
    
    
        
def course_count(**data):
    try:
        
        course=Course.objects.filter(id=data.get("id")).first()
        
        print(course)
        if course is  None:
            raise APIException("Course id Already exists")
        
        course.admission_count+=data.get("count")
        
        print(course.admission_count)
        course.save()
        course_count_task()
        
        return f"{course.course_name} is count updated"
    except Exception as e:
        raise APIException(e)
    
    
    
    
    
  
    
    
DROPDOWN_MODEL_MAP = {
    "lead_source": LeadSource,
    "campaign_name": CampaignName,
    "priority": Priority,
    "pipeline_stage": PipelineStage,
    "preferred_timing": PreferredTime,
    "education": Education,
    "course_name": CourseName,
    "course_plan": CoursePlan,
    "course_time": CourseTiming,
    "lead_filter":FilterLeads,
    "payment_stage":PaymentStage,
    "payment_status":PaymentStage,
    "pending_amount":AmountStage,
    "call_stage":Stages,
    "call_select_tag":SelectTag,
    "payment_filter":FilterPayment,
    "pipeline_filter":FilterPipeline
}   


DROPDOWN_VALUE_MAP = {
    "course_name": "coursename",
    "course_plan": "courseplan",
    "course_time": "coursetime",
    "lead_source": "name",
    "campaign_name": "name",
    "priority": "name",
    "pipeline_stage": "name",
    "preferred_timing": "name",
    "education": "name",
    "lead_filter":"name",
    "payment_stage":"name",
    "payment_status":"name",
    "pending_amount":"name",
    "call_stage":"name",
    "call_select_tag":"name",
    "payment_filter":"name",
    "pipeline_filter":"name"
}


DROPDOWN_FILTER_MAP = {
    "course_plan": ["courses__name_id"],
    "course_time": ["courses__name_id", "courses__plan_id"],
    "call_select_tag": ["stages__id"],
}


def get_selected_option(**data):
    try:
        input_key = data.get("dropdown_category")

        if input_key not in DROPDOWN_MODEL_MAP:
            return []

        model = DROPDOWN_MODEL_MAP[input_key]
        filters = {}

        # is_active field irundha mattum apply pannum
        if "is_active" in [f.name for f in model._meta.fields]:
            filters["is_active"] = True

        # ---- multi-field dependent filter ----
        if input_key in DROPDOWN_FILTER_MAP:
            filter_fields = DROPDOWN_FILTER_MAP[input_key]

            if input_key == "course_time":
                name_id = data.get("course_name_id")
                plan_id = data.get("filter_id")

                if name_id not in [None, "", 0, "0"]:
                    filters["courses__name_id"] = name_id
                if plan_id not in [None, "", 0, "0"]:
                    filters["courses__plan_id"] = plan_id

            else:
                filter_id = data.get("filter_id")
                if filter_id not in [None, "", 0, "0"]:
                    filters[filter_fields[0]] = filter_id

        value_field = DROPDOWN_VALUE_MAP.get(input_key)

        annotations = {
            "label": F(value_field),
            "value": F("id"),
        }

        values_fields = ["label", "value"]

        # ---- course_time ku mattum course_fees um anupanum ----
        if input_key == "course_time":
            annotations["course_fees"] = F("courses__course_fees")
            values_fields.append("course_fees")

        queryset = (
            model.objects.filter(**filters)
            .annotate(**annotations)
            .order_by("label", "id")
            .values(*values_fields)
            .distinct("label")
        )

        return list(queryset)

    except Exception as e:
        raise APIException(str(e))
    
    
def lead_form_details(user, **data):
    try:
        # ✅ Lead fetch
        lead = Lead.objects.filter(id=data.get("lead_id")).first()
        
        if lead is None:
            raise APIException("Lead Not Found")
        
        print("Received data:", data)
        
        # ✅ Basic Info Update
        if data.get("fullname"):
            lead.full_name = data.get("fullname")
        if data.get("mobile"):
            lead.mobile_no = data.get("mobile")
        if data.get("alternative_mobile"):
            lead.alternative_mobile = data.get("alternative_mobile")
        if data.get("email"):
            lead.email = data.get("email")
        if data.get("location"):
            lead.location = data.get("location")
        if data.get("education_id"):
            lead.education_id = data.get("education_id")
        if data.get("passed_out_year"):
            lead.passed_out_year = data.get("passed_out_year")
        if data.get("experience"):
            lead.experience = data.get("experience")

        # ✅ Lead Info Update
        if data.get("enquiry_date"):
            lead.enquiry_date = data.get("enquiry_date")
        if data.get("current_status"):
            lead.current_status = data.get("current_status")
        if data.get("lead_source_id"):
            lead.lead_source_id = data.get("lead_source_id")
        if data.get("campaign_name_id"):
            lead.campaign_id = data.get("campaign_name_id")
        if data.get("course_plan_id"):
            lead.course_plan_id = data.get("course_plan_id")
        if data.get("course_name_id"):
            lead.course_name_id = data.get("course_name_id")
        if data.get("course_timing_id"):
            lead.course_timing_id = data.get("course_timing_id")
        if data.get("preferred_timing_id"):
            lead.preferred_timing_id = data.get("preferred_timing_id")
        
        # ✅ Course Management
        course = None
        if data.get("course_name_id") and data.get("course_plan_id") and data.get("course_timing_id"):
            course = Course.objects.filter(
                name_id=data.get("course_name_id"),
                plan_id=data.get("course_plan_id"),
                time_id=data.get("course_timing_id"),
            ).first()
            
            if course is None:
                raise APIException("Course Not Found")
            
            lead.course = course
            print(f"Course assigned: {course}")
            
            # ✅ Seat Management - Only if moving to Won stage
            old_pipeline_stage = lead.pipeline_stage_id
            if old_pipeline_stage != 3 and data.get("pipeline_stage_id") == 3:
                if course.seats_left <= 0:
                    raise APIException("No seats available")
                
                course.admission_count += 1
                course.save()
                print(f"Admission Count Updated: {course.admission_count}")
        
        # ✅ Pipeline Update
        if data.get("pipeline_stage_id"):
            lead.pipeline_stage_id = data.get("pipeline_stage_id")
        if data.get("priority_id"):
            lead.priority_id = data.get("priority_id")
        
        # ✅ Save Lead - IMPORTANT: Save before payment processing
        lead.updated_by = str(user)
        lead.save()
        print(f"Lead saved successfully. Pipeline stage: {lead.pipeline_stage_id}")
        
        # ✅ Payment Info Update - Only when pipeline stage is 3 (Won)
        # 🔧 FIX: use lead.pipeline_stage_id (DB-saved value, always correct)
        # instead of data.get("pipeline_stage_id") — old code skipped this
        # whole block (and silently dropped due_date/payment_status updates)
        # whenever the incoming payload didn't include pipeline_stage_id.
        if lead.pipeline_stage_id == 3:
            print("Processing payment for Won stage...")
            
            # Validate required fields for payment
            if not lead.course:
                raise APIException("Course information is required for payment")
            
            paid_amount = float(data.get("amount_paid", 0))
            total_fee = float(lead.course.course_fees)
            print(f"Total Fee: {total_fee}, Paid Amount: {paid_amount}")
            
            # ✅ Check existing payment info
            payment_info = PaymentInfo.objects.filter(lead=lead).first()
            
            # ✅ First payment
            if not payment_info:
                print("Creating new payment info...")
                pending_amount = total_fee - paid_amount
                
                payment_info = PaymentInfo.objects.create(
                    lead=lead,
                    amount_paid=paid_amount,
                    pending_amount=pending_amount,
                    summary=data.get("notes", ""),
                    created_by=str(user),
                )
                print(f"Payment info created: {payment_info.id}")
            
            # ✅ Update existing payment
            else:
                print(f"Updating existing payment info: {payment_info.id}")
                total_paid = payment_info.amount_paid + paid_amount
                
                payment_info.amount_paid = total_paid
                payment_info.pending_amount = total_fee - total_paid
                payment_info.summary = data.get("notes", payment_info.summary)
                payment_info.updated_by = str(user)
                payment_info.save()  # ✅ CRITICAL FIX: Save the updated payment info
                print(f"Payment info updated. Total paid: {total_paid}")
            
            # ✅ Payment History Entry
            payment_history = PaymentHistory.objects.create(
                payment=payment_info,
                paid_amount=paid_amount,
                pending_amount=data.get("pending_amount", payment_info.pending_amount),
                due_stage_id=data.get("payment_status_id"),
                due_date=data.get("due_date"),
                notes=data.get("notes", ""),
                created_by=str(user),
            )
            print(f"Payment history created: {payment_history.id}")
            
            # ✅ Mark existing followup as attended (Optional - Commented in your code)
            # existing_followup = PaymentFollowUp.objects.filter(
            #     payment__payment__lead=lead,
            #     is_attended=False,
            #     followup_status="Pending"
            # ).order_by("-created_at").first()
            # 
            # if existing_followup:
            #     existing_followup.is_attended = True
            #     existing_followup.attended_at = datetime.now()
            #     existing_followup.followup_status = "Completed"
            #     existing_followup.updated_by = str(user)
            #     existing_followup.save()
            
            # ✅ New followup entry (Optional - Commented in your code)
            # if data.get("next_followup"):
            #     followup_datetime = data.get("next_followup")
            #     if isinstance(followup_datetime, str):
            #         followup_datetime = parse_datetime(followup_datetime)
            #     
            #     PaymentFollowUp.objects.create(
            #         payment=payment_history,
            #         followup_date=followup_datetime,
            #         created_by=str(user),
            #     )
        
        # ✅ Referral Details
        referal_list = data.get("referal_list") or []
        for re in referal_list:
            ReferalDetails.objects.create(
                referal_name=re.get("name", ""),
                referal_number=re.get("number", ""),
                referal_lead=lead,
                created_by=user
            )
        
        return {"message": "Lead Updated Successfully"}
    
    except Exception as e:
        print(f"Error in lead_form_details: {str(e)}")
        raise APIException(str(e))

    
    
def fetch_one_lead(**data):
    try:
        lead = Lead.objects.filter(id=data.get("lead_id")).first()
        
        if lead is None:
            raise APIException("Lead Not Found")
        lead=exec_raw_sql("D_FETCH_ONE_LEAD",{"id":data.get("lead_id")})
        


        
        return lead
    except Exception as e:
        raise APIException(e)


def fetch_call_history(**data):
    try:
        lead = Lead.objects.filter(id=data.get("lead_id")).first()
        
        if lead is None:
            raise APIException("Lead Not Found")
        lead=exec_raw_sql("D_FETCH_ONE_LEAD_CALL_HISTORY",{"id":data.get("lead_id")})
        
        print(lead)

        
        return lead
    except Exception as e:
        raise APIException(e)
    
    
    
def call_connect_api(user,**data):
    try:
        lead = Lead.objects.filter(id=data.get("lead_id")).first()
        
        if lead is None:
            raise APIException("Lead Not Found")
        
                # ==========================================
        # FOLLOWUP SLOT VALIDATION FIRST
        # ==========================================

        if data.get("next_followup"):

            followup_datetime = data.get("next_followup")

            if isinstance(followup_datetime, str):
                followup_datetime = parse_datetime(followup_datetime)

            if not followup_datetime:
                raise APIException("Invalid followup datetime")

            exists = FollowUp.objects.filter(
                telecaller=user,
                scheduled_at__year=followup_datetime.year,
                scheduled_at__month=followup_datetime.month,
                scheduled_at__day=followup_datetime.day,
                scheduled_at__hour=followup_datetime.hour,
                scheduled_at__minute=followup_datetime.minute,
                is_attended=False
            ).exists()

            if exists:
                raise APIException(
                    "Follow-up already scheduled for this time."
                )

        
        current_stage = lead.pipeline_stage_id

        # Only update stage if not Won
        if current_stage != 3:
            lead.pipeline_stage_id = 2
            lead.save()
        print(data)
    
        call=CallDetails.objects.create(
                lead=lead,
                telecaller=user,
                connection_status=data.get("connection_status"),
                duration_seconds=data.get("call_duration"),
                stage_id=data.get("stage_id"),
                select_tag_id=data.get("select_tag_id" or 'null'),
                conversation_summary=data.get("call_summary"),
                upload_recording=data.get("upload_record"),
                created_by=str(user)    
            )
        print("call",call)
        existing_call =FollowUp.objects.filter(lead=lead,is_attended=False).order_by('-id').first()
        print("existing",existing_call)
        if existing_call:
            existing_call.is_attended=True
            existing_call.attended_at=datetime.now()
            existing_call.attended_via_call=call
            existing_call.updated_by =str(user)  
            existing_call.save()
        
        # ==========================================
        # ✅ MARK EXISTING FOLLOWUP AS ATTENDED
        # ==========================================

        existing_followup = PaymentFollowUp.objects.filter(
            payment__payment__lead=lead,
            is_attended=False,
            followup_status="Pending"
        ).order_by("-created_at").first()

        if existing_followup:
            existing_followup.is_attended = True
            existing_followup.attended_at = datetime.now()
            existing_followup.followup_status = "Completed"
            existing_followup.attended_via_call=call
            existing_followup.updated_by = str(user)
            existing_followup.save()
            
            
        print("exsitng update")
        payment_history = PaymentHistory.objects.filter(payment__lead=lead).first()
        print(payment_history)
        if data.get("next_followup"):

            if current_stage == 3:

                PaymentFollowUp.objects.create(
                    payment=payment_history,
                    followup_date=followup_datetime,
                    created_from_call=call,
                    created_by=user,
                )

            else:

                FollowUp.objects.create(
                    lead=lead,
                    telecaller=user,
                    scheduled_at=followup_datetime,
                    created_from_call=call,
                    created_by=user,
                )
            
        return "done"
       
    except Exception as e:
        raise APIException(e)
    
    
    
    
def call_disconnect_select_api(user,**data):
    try:

        lead = Lead.objects.filter(id=data.get("lead_id")).first()
        
        id=data.get("lead_id")

        if lead is None:
            raise APIException("Lead Not Found")   
        
        tag=exec_raw_sql("D_FETCH_DISCONNECT_SELECT",{"id":id})

        return tag
        
    except Exception as e:
        raise APIException(str(e))    

def call_disconnect_api(user, **data):
    try:

        lead = Lead.objects.filter(id=data.get("lead_id")).first()

        if lead is None:
            raise APIException("Lead Not Found")

        # ==========================================
        # FOLLOWUP SLOT VALIDATION FIRST
        # ==========================================

        if data.get("next_followup"):

            followup_datetime = data.get("next_followup")

            if isinstance(followup_datetime, str):
                followup_datetime = parse_datetime(followup_datetime)

            if not followup_datetime:
                raise APIException("Invalid followup datetime")

            exists = FollowUp.objects.filter(
                telecaller=user,
                scheduled_at__year=followup_datetime.year,
                scheduled_at__month=followup_datetime.month,
                scheduled_at__day=followup_datetime.day,
                scheduled_at__hour=followup_datetime.hour,
                scheduled_at__minute=followup_datetime.minute,
                is_attended=False
            ).exists()

            if exists:
                raise APIException(
                    "Follow-up already scheduled for this time."
                )

        # ==========================================
        # BELOW CODE EXECUTES ONLY IF VALIDATION PASS
        # ==========================================

        current_stage = lead.pipeline_stage_id 

        # Only update stage if not Won
        if current_stage not in [1, 3]:
            lead.pipeline_stage_id = 2
            lead.save()

        call = CallDetails.objects.create(
            lead=lead,
            telecaller=user,
            connection_status="Disconnected",
            # select_tag_id=data.get("select_tag_id"),
            created_by=user,
        )
        if data.get("select_tag_id")==7:
            call.other_reason=data.get("other_reason")
            pass
        existing_call = FollowUp.objects.filter(
            lead=lead,
            is_attended=False
        ).order_by("-id").first()

        if existing_call:
            existing_call.is_attended = True
            existing_call.attended_at = datetime.now()
            existing_call.attended_via_call = call
            existing_call.updated_by = str(user)
            existing_call.save()

        DisconnectedDetails.objects.create(
            call=call,
            select_tag_id=data.get("select_tag_id"),
            retry_notes=data.get("retry_notes"),
            created_by=str(user),
        )

        # ==========================================
        # ✅ MARK EXISTING FOLLOWUP AS ATTENDED
        # ==========================================

        existing_followup = PaymentFollowUp.objects.filter(
            payment__payment__lead=lead,
            is_attended=False,
            followup_status="Pending"
        ).order_by("-created_at").first()

        if existing_followup:
            existing_followup.is_attended = True
            existing_followup.attended_at = datetime.now()
            existing_followup.followup_status = "Completed"
            existing_followup.attended_via_call=call
            existing_followup.updated_by = str(user)
            existing_followup.save()
            
            
        print("exsitng update")
        payment_history = PaymentHistory.objects.filter(payment__lead=lead).first()
        print(payment_history)
        if data.get("next_followup"):

            if current_stage == 3:

                PaymentFollowUp.objects.create(
                    payment=payment_history,
                    followup_date=followup_datetime,
                    created_from_call=call,
                    created_by=user,
                )

            else:

                FollowUp.objects.create(
                    lead=lead,
                    telecaller=user,
                    scheduled_at=followup_datetime,
                    created_from_call=call,
                    created_by=user,
                )
        return "done"

    except Exception as e:
        raise APIException(str(e))
    
    
def add_new_lead(user,**data):
    try:
        pipeline=PipelineStage.objects.filter(name="new lead").first()
        
        campaign=CampaignName.objects.filter(id=data.get("campaign_id")).first()
        if campaign is None:
            raise APIException("Campaign Not Found")
        
        number_exists=Lead.objects.filter(mobile_no=data.get("mobile")).first()
        print(number_exists)
        if number_exists:
            raise APIException(
               f"{data.get("mobile")} already exists. Assigned to {number_exists.assigned_to}"
            )
        
        lead=Lead.objects.create(
            full_name=data.get("full_name"),
            mobile_no=data.get("mobile"),
            enquiry_date=data.get("enquiry_date"),
            campaign_id=campaign.id,
            pipeline_stage_id=pipeline.id,
            assigned_to_id=user.id,
            priority_id=4,
            lead_source_id=4,
            created_by=user
        )
        send_lead_assigned_notification(lead.id, lead.assigned_to_id,assigned_by_id=None)
        return f"{lead.full_name} New Lead created successfully"
    except Exception as e:
        raise APIException(str(e))
    
    
def fetch_one_loss_detail(user,**data):
    try:
        id=data.get("lead_id")
        lead = Lead.objects.filter(id=data.get("lead_id")).first()
        print(lead)
        if lead is None:
            raise APIException("Lead Not Found")
        
        loss=exec_raw_sql("D_FETCH_ONE_LOSS_LEAD_DATA",{"id":id})
        print(loss)
        
        return loss
    except Exception as e:
        raise APIException(str(e))
    
    
def loss_detail_update(user,**data):
    try:
        lead = Lead.objects.filter(id=data.get("lead_id")).first()

        if lead is None:
            raise APIException("Lead Not Found")
        print(lead)
        loss=LossLeadDetail.objects.create(
            lead=lead,
            reported_by=user,
            follow_up_days=data.get("follow_up_days"),
            main_reason_id=data.get("main_reason_id"),
            # sub_reason=data.get("sub_reason"),
            detailed_reason=data.get("loss_reason"),
            created_by=user
        )
        
        lead.pipeline_stage_id=data.get("pipeline_stage_id")
        lead.priority_id=data.get("priority_id")
        lead.save()
        
        return f"{loss.lead} this lead is {loss.follow_up_days} days followup you will add loss lead "
    except Exception as e:
        raise APIException(str(e))

   
   
 
def fetch_one_won_detail(user,**data):
    try:
        id=data.get("lead_id")
        lead = Lead.objects.filter(id=data.get("lead_id")).first()

        if lead is None:
            raise APIException("Lead Not Found")
        
        won=exec_raw_sql("D_FETCH_ONE_WON_LEAD_DATA",{"id":id})
        
        
        return won
    except Exception as e:
        raise APIException(str(e))
    
    
        
def won_detail_update(user, **data):
    try:
        id=user.id
        lead = Lead.objects.filter(id=id).first()
        print(lead.course_id)
        course = Course.objects.filter(id=lead.course_id).first()
        if not lead:
            raise APIException("Lead not found")

        if not lead.course:
            raise APIException(
                "Lead has no course assigned."
            )
            
        if course is None:
            raise APIException("Course Not Found")
        lead.course=course
        old_pipeline_stage=lead.pipeline_stage_id
        if (
                old_pipeline_stage != 3
                and data.get("pipeline_stage_id") == 3
            ):

            if course.seats_left <= 0:
                raise APIException("No seats available")

            course.admission_count += 1
            course.updated_by=str(user)

            course.save()

            print("Admission Count Updated")
            print(course.admission_count)
        lead.pipeline_stage_id=data.get("pipeline_stage_id")
        lead.priority_id=data.get("priority")

        if data.get("next_followup"):

            followup_datetime = data.get("next_followup")

            if isinstance(followup_datetime, str):
                followup_datetime = parse_datetime(followup_datetime)

                print("date",followup_datetime)
            existing_followup = PaymentFollowUp.objects.filter(
                payment__payment__lead__assigned_to=lead.assigned_to,
                followup_date__year=followup_datetime.year,
                followup_date__month=followup_datetime.month,
                followup_date__day=followup_datetime.day,
                followup_date__hour=followup_datetime.hour,
                followup_date__minute=followup_datetime.minute,
                followup_status="Pending"
            ).exists()

            print("exitfolow",existing_followup)
            if existing_followup:
                raise APIException(
                    f"Follow-up already exists at {followup_datetime.strftime('%d-%m-%Y %H:%M')}"
                )       

        paid_amount = float(data.get("paid_amount", 0))
        total_fee = float(lead.course.course_fees)

        # ==========================================
        # CHECK EXISTING PAYMENT INFO
        # ==========================================

        payment_info = PaymentInfo.objects.filter(
            lead=lead
        ).first()

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

        PaymentHistory.objects.create(
            payment=payment_info,
            paid_amount=paid_amount,
            pending_amount=data.get("pending_amount"),
            # payment_status=data.get("payment_status"),
            due_date=data.get("due_date"),
            notes=data.get("notes"),
            created_by=str(user),
        )

        # ==========================================
        # FOLLOWUP ENTRY
        # ==========================================

        if data.get("next_followup"):

            PaymentFollowUp.objects.create(
                payment=payment_info,
                followup_date=data.get("next_followup"),
                created_by=str(user),
            )
            lead.current_status="Follow Up"
            
        lead.save()
        return "Payment Updated Successfully"

    except Exception as e:
        raise APIException(str(e))