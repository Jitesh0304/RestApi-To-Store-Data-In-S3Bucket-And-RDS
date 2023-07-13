from django.shortcuts import render
from .serializers import AwsSerializeres
from .models import AwsCredential
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated



import boto3
from botocore.client import ClientError



class AWSview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,  format= None):
        user = self.request.user
        dt = AwsCredential.objects.filter(user = user)
        if not dt:
            return Response({'detail': 'You have not saved your AWS credentials...'}, status=status.HTTP_404_NOT_FOUND)
        else:
            dt = AwsCredential.objects.get(user = user)
            serializer = AwsSerializeres(dt)
            return Response(serializer.data)



    def post(self, request, format= None):
        # serializer = AwsSerializeres(data =request.data)
        serializer = AwsSerializeres(data=request.data, context={'request': request})
        user = self.request.user
        dt = AwsCredential.objects.filter(user = user)
        if dt:
            return Response({'msg':'User already have one AWS account'}, status=status.HTTP_208_ALREADY_REPORTED)
        if serializer.is_valid():
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields 
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            accessID = serializer.validated_data['accessID']
            secretKey = serializer.validated_data['secretKey']
            bucketName = serializer.validated_data['bucketName']
            regionName = serializer.validated_data['regionName']
            try:
                s3_client = boto3.client('s3',
                                        aws_access_key_id = accessID,
                                        aws_secret_access_key = secretKey)
                s3_client.head_bucket(Bucket=bucketName)                     
                bucket_exit = 'Yes'
            except Exception:      ## ClientError
                bucket_exit = 'No' 

            if bucket_exit == 'Yes':
                serializer.save()               ## user = self.request.user
                return Response({'msg':'Your data has been saved'}, status= status.HTTP_201_CREATED)
            else:
                return Response({'msg':'No bucket exist with this details'}, status= status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
            




    def put(self, request, format= None):
        user = self.request.user
        dt = AwsCredential.objects.filter(user = user)
        if not dt:
            return Response({'msg':'You have not saved your aws credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            dt = AwsCredential.objects.get(user = user)
            serializer = AwsSerializeres(dt,data= request.data)
            if serializer.is_valid():
                input_data = set(serializer.initial_data.keys())
                required_fields = set(serializer.fields.keys())
                ext_data =  input_data - required_fields 
                if ext_data:
                    return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
                accessID = serializer.validated_data['accessID']
                secretKey = serializer.validated_data['secretKey']
                bucketName = serializer.validated_data['bucketName']
                regionName = serializer.validated_data['regionName']
                try:
                    s3_client = boto3.client('s3',
                                            aws_access_key_id = accessID,
                                            aws_secret_access_key = secretKey)
                    s3_client.head_bucket(Bucket=bucketName)                     
                    bucket_exit = 'Yes'
                except Exception:                ## ClientError
                    bucket_exit = 'No' 

                if bucket_exit == 'Yes':
                    serializer.save()               ## user = self.request.user
                    return Response({'msg':'Complete Data updated'}, status=status.HTTP_200_OK)
                else:
                    return Response({'msg':'No bucket exist !! Please Enter correct data'}, status= status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    



    def patch(self, request, format= None):
        user = self.request.user
        dt = AwsCredential.objects.filter(user = user)
        if not dt:
            return Response({'msg':'You have not saved your aws credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            dt = AwsCredential.objects.get(user = user)
            serializer = AwsSerializeres(dt, data= request.data, partial=True)
            if serializer.is_valid():
                input_data = set(serializer.initial_data.keys())
                required_fields = set(serializer.fields.keys())
                ext_data =  input_data - required_fields 
                if ext_data:
                    return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
                serializer.save()               
                return Response({'msg':'Partial Data updated'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)



    def delete(self, request, format=None):
        user = self.request.user
        dt = AwsCredential.objects.filter(user = user)
        if not dt:
            return Response({'msg':'You have not saved your aws credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            dt = AwsCredential.objects.get(user = user)
            dt.delete()
            return Response({'msg':'Data deleted'}, status=status.HTTP_200_OK)