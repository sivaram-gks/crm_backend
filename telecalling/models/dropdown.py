from django.db import models
from .delete_base_model import SafeDeleteModel


class DropdownCategory(SafeDeleteModel):
    category_name=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)    

    def __str__(self):
        return f"{self.category_name}"
    class Meta:
        db_table = 'telecalling_dropdown_category'
        
        
class Dropdown(SafeDeleteModel):
    category=models.ForeignKey(DropdownCategory, on_delete=models.SET_NULL, null=True, related_name='category')
    name=models.CharField(max_length=100)
    sub_name=models.CharField(max_length=100,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)    

    def __str__(self):
        return f"{self.name}"
    class Meta:
        db_table = 'telecalling_dropdown'
        
        
        
