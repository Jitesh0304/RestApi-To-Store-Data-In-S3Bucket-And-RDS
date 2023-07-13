from django.shortcuts import render
from .serializers import AwsAnnoteSerializer
from .models import AwsAnnote
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from aws.models import AwsCredential
import boto3
import json
import datetime
from botocore.client import ClientError



def bucket_check(USER):
    dt = AwsCredential.objects.filter(user = USER)
    if not dt:
        bucket_exit = 'No'
    if dt:
        aws_accessID = dt[0].accessID
        aws_secretKey = dt[0].secretKey
        aws_bucketName = dt[0].bucketName
        aws_s3_client = boto3.client('s3',
                                    aws_access_key_id = aws_accessID,
                                    aws_secret_access_key = aws_secretKey)
        try:
            aws_s3_client.head_bucket(Bucket=aws_bucketName)
            bucket_exit = 'Yes'
        except ClientError:
            bucket_exit = 'No'
    return bucket_exit



def listOFfiles(USER):
    try:
        dt = AwsCredential.objects.filter(user = USER)       ## we can use get also
        buck_name = dt[0].bucketName
        s3 = boto3.resource(
            service_name = 's3',
            region_name = dt[0].regionName,               
            aws_access_key_id = dt[0].accessID,      
            aws_secret_access_key = dt[0].secretKey  
        )

        filesList = []
        for obj in s3.Bucket(buck_name,).objects.all():
            filesList.append(obj.key)
    except Exception:
        filesList = None
    return filesList



def onefile(USER, filename):
    try:
        dt = AwsCredential.objects.filter(user = USER)
        buck_name = dt[0].bucketName
        s3 = boto3.resource(
            service_name = 's3',
            region_name = dt[0].regionName,                
            aws_access_key_id = dt[0].accessID,         
            aws_secret_access_key = dt[0].secretKey 
        )
        if filename.endswith('.json'):
            get_obj = s3.Bucket(buck_name).Object(filename).get()
        else:
            # get_obj= aws_s3_client.head_object(Bucket=aws_bucketName, Key=filename)
            get_obj = s3.Bucket(buck_name).Object(f'{filename}.json').get()
        obj_data = json.load(get_obj['Body'])
    except Exception:
        obj_data = None
    return obj_data






class AwsAnnoteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nm = None, format= None):
        name = nm
        user = self.request.user
        bucketPresent = bucket_check(user)
        if bucketPresent == "No":
            return Response({'msg':'You have not saved your bucket details or youur bucket details is not correct'})
        if name == None:
            allfiles = listOFfiles(user)
            if allfiles == None:
                return Response({'msg':'Your bucket region is not correct'}, status= status.HTTP_404_NOT_FOUND)
            if len(allfiles) == 0:
                return Response({'msg':'Bucket is empty'}, status= status.HTTP_204_NO_CONTENT)
            return Response(allfiles, status= status.HTTP_200_OK)
        if name:
            file = onefile(user, name)
            if file == None:
                return Response({'msg':f'No data present in bucket with -{name}- this name'}, status= status.HTTP_400_BAD_REQUEST)
            return Response(file, status= status.HTTP_200_OK)
        return Response({'msg':'something went wrong'}, status= status.HTTP_400_BAD_REQUEST)


    def post(self, request, format =None):
        user = self.request.user
        serializer = AwsAnnoteSerializer(data= request.data)
        if serializer.is_valid():

            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            
            dt = AwsCredential.objects.filter(user = user)
            if not dt:
                return Response({'msg':'Your aws credential is not save in database... first save your data'})
            
            name = serializer.data['image_name']
            img_name = name.rsplit(".", 1)[0]        ## it will remove the file extension like (.png, .jpeg, .jpg)
            try:
                awsID = dt[0].accessID
                awsKey = dt[0].secretKey
                awsbuck = dt[0].bucketName
                awsreg = dt[0].regionName
                s3_client = boto3.client('s3',
                                            aws_access_key_id = awsID,
                                            aws_secret_access_key = awsKey)
                json_data = serializer.validated_data
                json_data = json.dumps(serializer.validated_data).encode('utf-8')
                s3_client.put_object(Body= json_data, Bucket= awsbuck, Key= f'{img_name}.json' )
                return Response({'msg':'Data has been stored in Your S3 bucket....'}, status= status.HTTP_201_CREATED)
            except Exception:
                return Response({'msg':'Your AWS credential is not valid... Please provide valid credential'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    def delete(self, request, nm =None, format= None):
        name = nm
        user = self.request.user
        bucketPresent = bucket_check(user)
        if bucketPresent == "No":
            return Response({'msg':'You have not saved your bucket details or youur bucket details is not correct'})
        if bucketPresent == "Yes":
            dt = AwsCredential.objects.get(user = user)
            file = onefile(user, name)
            if file == None:
                return Response({'msg':f'{name} file is not present in your S3 bucket'}, status= status.HTTP_200_OK)
            try:
                awsID = dt.accessID
                awsKey = dt.secretKey
                awsbuck = dt.bucketName
                awsreg = dt.regionName
                s3_client = boto3.client('s3',
                                            aws_access_key_id = awsID,
                                            aws_secret_access_key = awsKey)
                if name.endswith('.json'):
                    s3_client.delete_object(Bucket = awsbuck, Key= f'{name}')
                    return Response({'msg':'Your data has been deleted'}, status= status.HTTP_200_OK)
                else:
                    s3_client.delete_object(Bucket = awsbuck, Key= f'{name}.json')
                    return Response({'msg':'Your data has been deleted'}, status= status.HTTP_200_OK)
            except Exception:
                return Response({'msg':f'{name} file not present'}, status= status.HTTP_400_BAD_REQUEST)
            # return Response({'msg':'You have not saved your S3 credential'}, status= status.HTTP_400_BAD_REQUEST)
        return Response({'msg':'something went wrong'}, status= status.HTTP_400_BAD_REQUEST)


############################################