from django.db import models
from .delete_base_model import SafeDeleteModel



class Perm(SafeDeleteModel):
    name = models.CharField(max_length=50)
    display_value = models.CharField(max_length=100)
    code = models.CharField(max_length=50, db_index=True, unique=True)
    # perm_group = models.CharField(max_length=50)
    # perm_cat = models.CharField(max_length=30, null=True, blank=True)

    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'telecalling_perm'