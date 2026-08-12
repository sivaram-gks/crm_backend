from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='led_teams'
    )
    badge_color = models.CharField(max_length=20, default="#E3F2FD")
    is_active = models.BooleanField(default=True)
    
    # Audit trail fields
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'adm_team'

    def __str__(self):
        return self.name
