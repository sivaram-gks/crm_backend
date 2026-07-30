from django.db import models
from django.core.exceptions import ValidationError
from .dropdown import Dropdown
from django.core.validators import MinValueValidator
from .delete_base_model import SafeDeleteModel

# class Course(SafeDeleteModel):
#     course_name = models.CharField(max_length=255)
#     course_plan = models.CharField(max_length=255) # e.g., Full Stack, Data Science
#     course_fees=models.FloatField(validators=[MinValueValidator(0)],default=16000)
#     starting_date = models.DateField()
#     closing_date = models.DateField()
    
#     total_seats = models.IntegerField(default=0)
#     admission_count = models.IntegerField(default=0)
#     seats_left = models.IntegerField() # Manual-a edit panna mudiyathu
    
#     status = models.CharField(max_length=20, default='Open')
#     created_at=models.DateTimeField(auto_now_add=True,null=True)
#     created_by=models.CharField(max_length=50,null=True)
#     updated_at=models.DateTimeField(auto_now=True,null=True)
#     updated_by=models.CharField(max_length=50,null=True)

#     def save(self, *args, **kwargs):
#         # Seats calculation logic
#         self.seats_left = self.total_seats - self.admission_count
        
#         # Oru vaela seats full aayiduchuna status-a auto-va 'Full' nu mathu
#         if self.seats_left <= 0:
#             self.status = 'Closed'
#             self.seats_left = 0
            
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.course_name} ({self.course_plan})"
    
#     class Meta:
#         db_table = 'telecalling_course'
        
        
        
class Course(SafeDeleteModel):

    name = models.ForeignKey(
        'CourseName',
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses')
    plan = models.ForeignKey(
        'CoursePlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    time = models.ForeignKey(
        'CourseTiming',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    batch=models.CharField(max_length=50,null=True)
    course_fees=models.FloatField(validators=[MinValueValidator(0)],default=16000)
    starting_date = models.DateField()
    closing_date = models.DateField()
    is_active=models.BooleanField(default=False)
    total_seats = models.IntegerField(default=0)
    admission_count = models.IntegerField(default=0)
    seats_left = models.IntegerField() # Manual-a edit panna mudiyathu
    
    status = models.CharField(max_length=20, default='Open')
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)

    def save(self, *args, **kwargs):
        # Seats calculation logic
        self.seats_left = self.total_seats - self.admission_count
        
        # Oru vaela seats full aayiduchuna status-a auto-va 'Full' nu mathu
        if self.seats_left <= 0:
            self.status = 'Closed'
            self.seats_left = 0
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.plan})"
    
    class Meta:
        db_table = 'telecalling_course'
        
   

class CourseName(SafeDeleteModel):
    coursename= models.CharField(null=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)
    
    def __str__(self):
        return str(self.coursename)
    
    class Meta:
        db_table = 'telecalling_course_name'

        
class CoursePlan(SafeDeleteModel):
    courseplan= models.CharField(null=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)
    
    def __str__(self):
        return str(self.courseplan)
    
    class Meta:
        db_table = 'telecalling_course_plan'
        
        
        
class CourseTiming(SafeDeleteModel):
    coursetime=models.CharField(null=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    created_by=models.CharField(max_length=50,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)
    updated_by=models.CharField(max_length=50,null=True)
    
    def __str__(self):
        return str(self.coursetime)
    
    class Meta:
        db_table = 'telecalling_course_time'