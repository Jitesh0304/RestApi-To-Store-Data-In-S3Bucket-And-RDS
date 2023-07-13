from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSeralizer,\
      UserChangePassword, SendPasswordResetEmailSerializer, UserPasswordResetSerializer, VerifyOtpSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .utils import *
import jwt
from decouple import config

        ## This will generate token manually...... JWT manualy generated token
# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }




def get_tokens_for_user(user):
    refreshToken = RefreshToken.for_user(user)
    accessToken = refreshToken.access_token
            ## decode the JWT .... mension the same name of th e secrete_key what ever you have written in .env file
    decodeJTW = jwt.decode(str(accessToken), config('DJANGO_SECRET_KEY'), algorithms=["HS256"])
            # add payload here!!
    decodeJTW['user'] = str(user)
    decodeJTW['name'] = str(user.name)
            # encode
    encoded = jwt.encode(decodeJTW, config('DJANGO_SECRET_KEY'), algorithm="HS256")
    return {
        'refresh': str(refreshToken),
        'access': str(encoded),
    }


    # create new user 
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format =None):
        serializer = UserRegistrationSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):

                    ## If a user send some extra fields data.. Then this error will occure
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields 
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            
            user = serializer.save()
            sent_otp_by_email(serializer.data['email'])
            return Response({'msg':'Registarion Successful... Verify your account'}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)





        ## verify OTP .. If OTP is correct then make the ((user.is_verify = True))
class VerifyOtp(APIView):

    def post(self, request):
        data = request.data 
        serializer = VerifyOtpSerializer(data= data)
        if serializer.is_valid():
                    ## If a user send some extra fields data.. Then this error will occure
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields 
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            email = serializer.data['email']
            otp = serializer.data['otp']
            user = User.objects.filter(email= email)
            if not user.exists():
                return Response({'msg':f'User is not present with {email}'}, status= status.HTTP_404_NOT_FOUND)
            if user[0].is_verified == True:
                return Response({'msg':'Your account is already verified...No verifictaion needed... You can login'}, status= status.HTTP_405_METHOD_NOT_ALLOWED)
            user = User.objects.get(email=email)
            if user.otp != otp:
                return Response({'msg':'Wrong OTP'}, status= status.HTTP_400_BAD_REQUEST)
            if user.otp == otp:                        
                user.is_verified = True      ## is_verified is a field in User model.. Bydefault it is false
                user.save()
                return Response({'msg':'Account verification is complete.... You can login'}, status= status.HTTP_200_OK) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




        ## This is for User login
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format= None):
        serializer = UserLoginSerializer(data= request.data)
        if serializer.is_valid(raise_exception= True):

                        ## If a user send some extra fields data.. Then this error will occure
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields 
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email= email, password = password)
            if user is not None:
                user = User.objects.get(email= email)
                if user.is_verified == True:
                    token = get_tokens_for_user(user)
                    return Response({'token': token}, status=status.HTTP_200_OK)
                else:
                    return Response({'msg':'User is not verified'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'msg':'Email or Password is not Valid'},
                                status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)    




            ## this is for perticular user profile view
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format= None):
        serializer = UserProfileSeralizer(request.user)
        return Response(serializer.data, status= status.HTTP_200_OK)




            ## this is for password change
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format= None):
        serializer = UserChangePassword(data = request.data, context ={'user':request.user})
        if serializer.is_valid(raise_exception= True):

                        ## If a user send some extra fields data.. Then this error will occure
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields 
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
           
            return Response({'msg':'Password Changed Successfully'}, status.HTTP_200_OK)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)




        ## this is for sending email to the user
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format= None):
        serializer = SendPasswordResetEmailSerializer(data = request.data)
        
        if serializer.is_valid(raise_exception= True):
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields 
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            
            return Response({'msg':'Password Reset OTP has been sent to your Email. Please check your Email'},
                            status= status.HTTP_200_OK)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)




            ## this is for reset the password
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format= None):
        serializer = UserPasswordResetSerializer(data= request.data)

        if serializer.is_valid(raise_exception= True):
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            
            return Response({'msg':'Password reset successfully'}, status= status.HTTP_200_OK)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)


