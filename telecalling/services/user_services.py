# from ..models import *
from ..models.leads import Lead
from ..models.user import User
from ..models.role import Role
from ..models.collection_query import CollectionQuery
from ..models.dropdown import DropdownCategory,Dropdown
import datetime
from django.utils import timezone
import logging
import uuid
from ..services.query_services import exec_raw_sql
from django.db.models import Q
logger = logging.getLogger('django')

import datetime
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings  ##b add
# from ..models import User
# from ..models.role import *
from django.db.models import Q ##b add
import random




def create_user(user_name,**data):
    try:
        user = User.objects.filter(email = data.get('email')).first()
        if user is not None:
            raise APIException("Email id Already exists")

        number = None
        if data.get('mobile_number'):
            number = User.objects.filter(mobile=data.get('mobile_number')).first()
        if number is not None:
            raise APIException("Mobile is Already exists")

        user = User.objects.create_user(data.get('username'),data.get('email'),data.get('password'))
        if data.get('role_id'):
            user.role.add(data.get('role_id'))
        user.first_name=data.get('first_name')
        user.last_name=data.get('last_name')
        user.is_active=True
        user.mobile=data.get('mobile_number')
        user.gender = data.get('gender')
        user.ending_date = data.get('ending_date')
        user.address = data.get('address')
        user.validate_token = User.objects.make_random_password(10) + uuid.uuid4().hex[:6].upper()

        user.save()
        data["user_id"] = user.id

        return {
    "id": user.id,
    "username": user.username,
    "email": user.email,
    "first_name": user.first_name,
    # "mobile": user.mobile
}
    except Exception as e:
        raise APIException(e)


def create_role(**data):
    try:
        role = Role(name=data.get('name'),
                    display_value=data.get('display_value'),
                    code=data.get('code'),
                    description = data.get('description'),
                    #  created_by=user_name
                     )
        role.save()
        return role.code

    except Exception as e:
        raise APIException(str(e))
    




def collection_query_service(**data):
    try:
        query=CollectionQuery.objects.create(key=data.get('key'),
                                             query=data.get('query'),
                                            )
        query.save()
        return {"collection query created"}
    except Exception as e:
        raise APIException(e)



def get_select_options(**data):
    try:
        field = data.get('fields')
        values = exec_raw_sql(field, {})
        return values
    except Exception as e:
        raise APIException(e)
    
    


def create_token(**data):

    username = data.get('username').lower()
    password = data.get('password')

    print(username)

    expired = User.objects.filter(
        Q(email=username) | Q(mobile=username),
        is_active=False
    )

    print(expired)

    if expired.exists():
        raise AuthenticationFailed(
            detail='Your plan has expired. Please renew your plan.'
        )

    user_obj = User.objects.filter(
        Q(mobile=username) |
        Q(username=username) |
        Q(email=username)
    ).first()

    print('user_obj', user_obj)

    # IMPORTANT FIX
    if user_obj is None:
        raise AuthenticationFailed(
            detail='User does not exist'
        )

    user = authenticate(
        username=user_obj.username,
        password=password
    )

    print('user', user)

    if user is None:
        raise AuthenticationFailed(
            detail='Invalid Username or Password'
        )

    if user.ending_date is None:

        user.last_login = datetime.datetime.now()
        user.save()

        refresh_tkn = RefreshToken.for_user(user)
        access_tkn = refresh_tkn.access_token

    elif user.ending_date >= datetime.datetime.now().date():

        user.last_login = datetime.datetime.now()
        user.save()

        refresh_tkn = RefreshToken.for_user(user)
        access_tkn = refresh_tkn.access_token

    else:
        raise AuthenticationFailed(
            detail='Your plan has expired. Please renew your plan.'
        )

    token_data = {
        "access": str(access_tkn),
        "refresh": str(refresh_tkn)   
    }

    user_data = {
        "user_email": user.email,
        "user_id": user.id,
        "user_mobile": user.mobile,
        "user_name":user.first_name
    }

    return token_data,user_data 



def drop_cate(user,**data):
    try:
        
        drop=DropdownCategory.objects.filter(category_name=data.get("category")).first()
        
        if drop is not None:
            raise APIException(f" {drop.category_name} Category is already exicted")        
        
        drop_category=DropdownCategory.objects.create(
            category_name=data.get("category"),
            created_by=user
        )
        
        return f"{drop_category.category_name} category is created sucessfully"
    
    except Exception as e:
        raise APIException(e)







def drop_sub(user,**data):
    try:
        
        # drop=DropdownCategory.objects.filter(id=data.get("category_id")).first()
        # print(drop)
        # if drop is not None:
        #     raise APIException(" Category is not found")        
        
        drop_sub=Dropdown.objects.create(
            name=data.get("name"),
            category_id=data.get("category_id"),
            sub_name=data.get("sub_name"),
            created_by=user
        )
        
        
        return f"{drop_sub.name} category is created sucessfully"
    
    except Exception as e:
        raise APIException(e)


















import random
import requests

from urllib.parse import quote
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.hashers import make_password

from rest_framework.exceptions import APIException




def generate_otp(data):
    try:
        mobile = str(data.get("mobile"))
        user = User.objects.filter(mobile=mobile).first()
        print(user)
        if not user:
            raise APIException("Email not found. Please enter a valid registered email.")

        # ==========================
        # GENERATE OTP
        # ==========================

        otp = str(random.randint(100000, 999999))

        # current_time = timezone.now()

        # expires = current_time + timedelta(minutes=5)

        # ==========================
        # SMS API DETAILS
        # ==========================

        api_key = "pdtPO9aL4m8RSQTV"

        sender_id = "MDTDMO"

        # ==========================
        # MESSAGE
        # ==========================

        message = f"""
Dear User, Your OTP for login to My Dreams Technology is {otp}.
Valid for 30 minutes. Please do not share this OTP.
Regards, My Dreams Technology Team
"""

        # Encode Message
        encoded_message = quote(message)

        # ==========================
        # API URL
        # ==========================

        url = (
            f"http://app.mydreamstechnology.in/vb/apikey.php"
            f"?apikey={api_key}"
            f"&senderid={sender_id}"
            f"&number={mobile}"
            f"&message={encoded_message}"
        )

        # ==========================
        # SEND SMS
        # ==========================

        response = requests.get(url)

        print("SMS STATUS :", response.status_code)

        print("SMS RESPONSE :", response.text)

        return {
            "message": "OTP sent successfully",
            # "otp_id": table.id,
            # remove this in production
            "otp": otp
        }

    except Exception as e:

        raise APIException(str(e))
