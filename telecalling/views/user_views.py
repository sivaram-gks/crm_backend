from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator
from ..models import *
from ..services.user_services import *
from rest_framework.decorators import authentication_classes, permission_classes
from ..tasks.api_log_task import api_history_log


@authentication_classes([])
@permission_classes([])
class CreateUser(APIView):
    class InputSerializer(serializers.Serializer):
        # name = serializers.CharField(required = True)
        # last_name = serializers.CharField(required = False)
        username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
        email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
        mobile_number = serializers.CharField(required =True,allow_null = True)
        role_id = serializers.IntegerField()
        password = serializers.CharField(required = True)
        confirm_password = serializers.CharField(required = True)
    def post(self, request):
        print(1)
        # authorize_request('api_perm_add_user', request.user)
        print(2)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        usr = create_user(request.user.username,**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': {},
            'response_payload': {}, 
            'status_code': 201
        }
        api_history_log(log_data)
        return Response({'data': {'user': usr}}, status=status.HTTP_201_CREATED)
        #return Response(usr,status = status.HTTP_201_CREATED)



@authentication_classes([])
@permission_classes([]) 
class CreateRole(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Role.objects.all())])
        display_value = serializers.CharField(required=True)
        code = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Role.objects.all())])
        description = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_code =create_role( **serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': {},
            'response_payload': {}, 
            'status_code': 200
        }
        api_history_log(log_data)
        return Response({'data': {'role_code': role_code}}, status=status.HTTP_200_OK)
  
  



@authentication_classes([])
@permission_classes([]) 
class CollectionQueryApi(APIView):
    class InputSerializer(serializers.Serializer):
        key=serializers.CharField(required=True)
        query=serializers.CharField(required=True) 
    
    def post(self,request):
        serializer=self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=collection_query_service(**serializer.validated_data)
        return Response({"data":data},status=status.HTTP_201_CREATED)



@authentication_classes([])
@permission_classes([])
class CreateToken(APIView):
    class InputSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField(write_only=True)
        source = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def post(self, request):
        print(request.data)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, user_details = create_token(**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data, 
            'response_payload': {}, 
            'status_code': 200
        }
        api_history_log(log_data)

        print({"data" : {"token" : token,"user_details" : user_details}})
        return Response({"data" : {"token" : token,"user" : user_details}},status=status.HTTP_200_OK)
        


@authentication_classes([])
@permission_classes([])
class RefreshTokenView(APIView):
    class InputSerializer(serializers.Serializer):
        refresh = serializers.CharField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh = RefreshToken(serializer.validated_data['refresh'])
            
            new_access = str(refresh.access_token)
            
            # ROTATE_REFRESH_TOKENS=True வச்சிருந்தா புது refresh token கிடைக்கும்
            new_refresh = str(refresh)
            log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data, 
            'response_payload': {}, 
            'status_code': 200
            }
            api_history_log(log_data)
            return Response({
                "data": {
                    "access": new_access,
                    "refresh": new_refresh
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            raise AuthenticationFailed(detail='Refresh token expired or invalid. Please login again.')


class GetSelectOption(APIView):
    class InputSerializers(serializers.Serializer):
        fields=serializers.CharField(required=True)
    
    def post(self,request):
        print(1)
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=get_select_options(**serializer.validated_data)
        log_data = {
            'user_id': request.user.id if request.user.id else None,
            'api_name': request.path,
            'method': request.method,
            'request_payload': serializer.validated_data, 
            'response_payload':data, 
            'status_code': 202
        }
        api_history_log(log_data)
        
        return Response({"data":data},status=status.HTTP_202_ACCEPTED)


# @authentication_classes([])
# @permission_classes([])
class GenerateOtpView(APIView):
    class InputSerializers(serializers.Serializer):
        mobile=serializers.IntegerField(required=True)
        # email=serializers.EmailField(required=True)
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        generateotp=generate_otp(serializer.validated_data)
        return Response({'data':generateotp},status=status.HTTP_201_CREATED)



class CreateDropdownCate(APIView):
    class InputSerializers(serializers.Serializer):
        category=serializers.CharField(required=True)
    
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        dropdown=drop_cate(user=request.user,**serializer.validated_data)
        return Response({'data':dropdown},status=status.HTTP_201_CREATED)
    
    
    
    
class CreateDropdownSub(APIView):
    class InputSerializers(serializers.Serializer):
        name=serializers.CharField(required=True)
        category_id=serializers.IntegerField(required=True)
        sub_name=serializers.CharField(required=False)
    
    def post(self,request):
        serializer=self.InputSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        dropdown=drop_sub(user=request.user,**serializer.validated_data)
        return Response({'data':dropdown},status=status.HTTP_201_CREATED)
    
    


# @authentication_classes([])
# @permission_classes([])
# class TaskScheduleDb(APIView):
#     class InputSerializers(serializers.Serializer):
#         task_name=serializers.CharField()
#         hour=serializers.IntegerField()
#         minute=serializers.IntegerField()
#         enabled=serializers.BooleanField()
    
#     def post(self,request):
#         serializer=self.InputSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data=task_schedule_db(**serializer.validated_data)
        
#         return Response({"data":data},status=status.HTTP_201_CREATED)
        
   
# class FetchAllUsers(APIView):
#     def get(self,request):
#         fetch_all=fetch_all_users()
#         return Response({"data":fetch_all},status=status.HTTP_202_ACCEPTED)
    

# class FetchOneUserDeatail(APIView):
#     class InputSerializers(serializers.Serializer):
#         id=serializers.IntegerField(required=True)
    
#     def post(self,request):
#         serializer=self.InputSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data=fetch_one_user(**serializer.validated_data)
        
#         return Response({"data":data},status=status.HTTP_202_ACCEPTED)


# class UpdateUserDetail(APIView):
#     class InputSerializers(serializers.Serializer):
#         id=serializers.IntegerField(required=True)
#         name=serializers.CharField(required=True)
#         email = serializers.EmailField(required=True)
#         mobile=serializers.CharField(required=True)
#         status=serializers.BooleanField(required=True)
#         starting_date=serializers.CharField(required=True)
#         role_id=serializers.IntegerField(required=True)
    
#     def post(self,request):
#         serializer=self.InputSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data=update_user_detail(**serializer.validated_data)
        
#         return Response({"data":data },status=status.HTTP_202_ACCEPTED)
    
   
# class AddUserDetail(APIView):
#     class InputSerializers(serializers.Serializer):
#         name=serializers.CharField(required=True)
#         email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
#         mobile_number = serializers.CharField(required =True,allow_null = True)
#         role_id=serializers.IntegerField(required=True)
#         start_date=serializers.DateField(required=False)
#         end_date=serializers.DateField(required=False)
    
    
#     def post(self,request):
#         serializer=self.InputSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data=add_user_detail(**serializer.validated_data)
        
#         return Response({"data":data},status=status.HTTP_201_CREATED)
    






    
 

# class CreatePermission(APIView):
#     class InputSerializers(serializers.Serializer):
#         name=serializers.CharField(required=True)
#         display_value=serializers.CharField(required=True)
#         code=serializers.CharField(required=True)

#     def post(self,request):
#         serializer=self.InputSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data=create_permission(**serializer.validated_data)
#         return Response({"data":data},status=status.HTTP_201_CREATED)




# class AddPermissionRole(APIView):
#     class InputSerializers(serializers.Serializer):
#         role_id=serializers.IntegerField(required=True)
#         perm_id=serializers.IntegerField(required=True)
        
#     def post(self,request):
#         serializer=self.InputSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data=add_perm_role(**serializer.validated_data)
        
#         return Response({"data":data},status=status.HTTP_201_CREATED)
