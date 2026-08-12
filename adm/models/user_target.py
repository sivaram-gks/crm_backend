from django.db import models
from django.conf import settings

class UserTarget(models.Model):
    telecaller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='performance_targets'
    )
    target_month = models.DateField()
    target_admissions = models.IntegerField(default=50)
    target_calls = models.IntegerField(default=800)
    
    # Audit trail fields
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'adm_user_target'
        unique_together = ['telecaller', 'target_month']

    def __str__(self):
        return f"Target for {self.telecaller} ({self.target_month.strftime('%Y-%m')})"
