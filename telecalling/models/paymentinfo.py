from django.db import models
from django.core.validators import MinValueValidator
from .delete_base_model import SafeDeleteModel
from ..models import *


class PaymentInfo(SafeDeleteModel):


    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='payments')
    # total_package_value = models.FloatField()
    amount_paid = models.FloatField( validators=[MinValueValidator(0)])
    pending_amount = models.FloatField(  editable=False)
    
    is_full_payment = models.BooleanField(default=False)
    payment_status= models.IntegerField(null=True)
    
   
    # next_follow_up = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)    

    def save(self, *args, **kwargs):

        # ✅ course fee
        total_fee = self.lead.course.course_fees

        # ✅ pending calculation
        self.pending_amount = total_fee - self.amount_paid

        # ✅ prevent negative
        if self.pending_amount < 0:
            self.pending_amount = 0

        # ✅ status
        if self.amount_paid >= total_fee:
            self.is_full_payment = True
            self.payment_status = 1

        elif self.amount_paid > 0:
            self.is_full_payment = False
            self.payment_status = 2

        else:
            self.is_full_payment = False
            self.payment_status = 3

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for {self.lead.full_name} - {self.payment_status}"
    
    class Meta:
        db_table = 'telecalling_payment_info'
        
        
        
        
        
class PaymentHistory(models.Model):

    payment = models.ForeignKey(
        PaymentInfo,
        on_delete=models.CASCADE,
        related_name='payment_histories'
    )

    paid_amount = models.FloatField()
    pending_amount= models.FloatField( validators=[MinValueValidator(0)])
    due_stage= models.ForeignKey(PaymentStage,on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(null=True, blank=True)

    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)    


    class Meta:
        db_table = "telecalling_payment_history"

    def __str__(self):
        return f"{self.payment.lead.full_name} - {self.paid_amount}"
    
    
    


class PaymentFollowUp(models.Model):

    payment = models.ForeignKey(
        PaymentHistory,
        on_delete=models.CASCADE,
        related_name='payment_followups'
    )

    followup_date = models.DateTimeField()

    attended_at = models.DateTimeField(null=True, blank=True)

    is_attended = models.BooleanField(default=False)

    followup_status = models.CharField(
        max_length=50,
        default='Pending'
    )

    created_from_call = models.ForeignKey(
        'CallDetails',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payment_scheduled_followups'
    )

    attended_via_call = models.ForeignKey(
        'CallDetails',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payment_attended_followups'
    )

    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)    


    class Meta:
        db_table = "telecalling_payment_followup"

    def __str__(self):
        return f"{self.payment.lead.full_name} Payment Followup"