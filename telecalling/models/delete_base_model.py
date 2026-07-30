from django.db import models
from django.apps import apps
from decimal import Decimal
from django.forms.models import model_to_dict
from datetime import date, datetime   # ✅ add this import


class SafeDeleteModel(models.Model):
    class Meta:
        abstract = True

    def delete(self):
        return None

    # def save_delete(self, user_id=None):
    #     LogModel = apps.get_model('telecalling', 'DeletedDataLog')
        
    #     obj_data = model_to_dict(self)
        
    #     LogModel.objects.create(
    #         table_name=self._meta.db_table,
    #         row_id=self.id,
    #         data=obj_data,
    #         deleted_by_id=user_id
    #     )

    #     return super(SafeDeleteModel, self).delete()
    def save_delete(self, user_id=None):
        LogModel = apps.get_model('telecalling', 'DeletedDataLog')
        
        obj_data = model_to_dict(self)

        # 👇 existing loop (DO NOT CHANGE structure)
        for field in self._meta.fields:
            value = getattr(self, field.name)
            
            if isinstance(value, models.fields.files.FieldFile):
                obj_data[field.name] = value.url if value else None

            # ✅ JUST ADD THIS BLOCK (nothing else change)
            elif isinstance(value, (date, datetime)):
                obj_data[field.name] = value.isoformat()
            
            elif isinstance(value, Decimal):  
                obj_data[field.name] = float(value)

        LogModel.objects.create(
            table_name=self._meta.db_table,
            row_id=self.id,
            data=obj_data,
            deleted_by_id=user_id
        )

        return super(SafeDeleteModel, self).delete()