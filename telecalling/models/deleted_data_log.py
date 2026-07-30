from django.db import models
from .user import User
from .delete_base_model import SafeDeleteModel


class DeletedDataLog(SafeDeleteModel):
    table_name=models.CharField(max_length=100)
    row_id=models.IntegerField()
    data=models.JSONField()
    deleted_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="deleted_logs")
    deleted_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.table_name
    
    class Meta:
        db_table="telecalling_deleted_data_log"