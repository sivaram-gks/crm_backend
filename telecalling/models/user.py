from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from .role import Role
from datetime import datetime,date
from rest_framework.exceptions import APIException
from django.utils.crypto import get_random_string

class UserManager(BaseUserManager):
    def create_user(self, username, email,password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')
        
        if email is None:
            raise TypeError('Users must have an email address.')
        # if role == "student":
        #     check_username = User.objects.filter(username = username,email = email ).first()
        #     if check_username :
        #         if check_username.ending_date > datetime.now().date():
        #             raise APIException ("Email is already exists") 
        # username = "guyfthfhgf"
        # password = email[:3]+"1234"
        # user = self.model(username=self.normalize_username(username), email=self.normalize_email(email))  ##maddy
        user = self.model(username=self.normalize_username(username), email=self.normalize_email(email))      ##b add

        # user.starting_date = datetime.now().date()
        user.is_active = True
    
        user.set_password(password)
        # user.role_id = role_id
      
        user.save()
      
        return user

    def create_superuser(self, username, email, password):
        ##logger.info(password)
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
    
    
    def normalize_username(self,username):
        #logger.info("lower",username.strip().lower())
        return username.strip().lower()
    
    def make_random_password(self, length=10):
        """Generate a random password."""
        return get_random_string(length)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    user_profile = models.CharField(max_length=100,null = True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    gender = models.CharField(max_length=100,null = True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    mobile = models.CharField(max_length=25, null=True)
    user_type = models.CharField(max_length=25, null=True)
    address = models.CharField(max_length=500, null = True)
    wrong_pwd_counts = models.IntegerField(default=0)
    role = models.ManyToManyField(Role,related_name="user")
    # starting_date = models.DateField()"
    starting_date = models.DateField(default=date.today)  # Sets today's date by default
    ending_date = models.DateField(null=True,blank=True)
    email_verified = models.BooleanField(default=False)
    last_pwd_changed_at = models.DateTimeField(blank=True, null=True)
    validate_token = models.CharField(max_length=20, blank=True, null=True)
    validated_at = models.DateTimeField(blank=True, null=True)
    deact_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    joining_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # More fields required by Django when specifying a custom user model.

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case we want it to be the email field.
    USERNAME_FIELD = 'username'
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']
    REQUIRED_FIELDS=['mobile']   ##b add

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.first_name is None and self.last_name is None:
            return self.username
        elif self.last_name is None:
            return self.first_name
        elif self.first_name is None:
            return self.username
        else:
            return str(self.first_name) + ' ' + str(self.last_name)

    def get_short_name(self):
        return self.username

    def get_perms(self):
     
        perms_list = []
        ##logger.info("User name: " + self.username)
        ##logger.info("Roles List: " + str(self.roles))
        for r in self.roles.all():
            ##logger.info(r)
            
            perms_list = perms_list + list(r.perms.all().values_list("name", flat=True))
           
      
        ##logger.info("Perms List: " + str(perms_list))
        return perms_list
        
    def get_users(self):
        users = User.objects.all()
        users_list = []
        #for u in self.username.all():
            #users_list = users_list + list(u.values_list("name",flat=True))

        for user in users:
                users_list.append(user.username)

        ##logger.info(users_list)

        return users_list
    
    """def get_all_users(request):
    
        users = User.objects.all()

        user_names = []

        for user in users:
            user_names.append(user.username)

        return user_names"""
        
        
    