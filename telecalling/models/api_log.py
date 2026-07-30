from django.db import models
from .user import User
from .delete_base_model import SafeDeleteModel


class Api_Log(SafeDeleteModel):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    api_name=models.CharField(max_length=100)
    method=models.CharField(max_length=100)
    request_payload=models.JSONField()
    response_payload=models.JSONField()
    status=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.api_name) if self.api_name else "No Name"
    
    class Meta:
        db_table="telecalling_api_log"
