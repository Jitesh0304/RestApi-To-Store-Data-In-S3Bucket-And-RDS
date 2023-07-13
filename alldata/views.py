from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import boto3
from botocore.config import Config


class AnnoteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, nm = None, format = None):
        name = nm
        user = self.request.user
        if name is not None:
            dt = Annote.objects.filter(image_name =name, user= user)
            if not dt:
                return Response({'detail': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                dt = Annote.objects.get(image_name= name, user = user)
                serializer = AnnoteSerializer(dt)
                return Response(serializer.data)
        if name is None:
            dt = Annote.objects.filter(user= user)
            if not dt:
                return Response({'detail': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                dt = Annote.objects.filter(user=user)
                serializer = AnnoteSerializer(dt, many = True)
                return Response(serializer.data)





    def post(self, request, format =None):
        serializer = AnnoteSerializer(data= request.data)
        user = self.request.user
        if serializer.is_valid():
            input_data = set(serializer.initial_data.keys())
            required_fields = set(serializer.fields.keys())
            ext_data =  input_data - required_fields 
            if ext_data:
                return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
            
            img_name = serializer.validated_data['image_name']
            existing_data = Annote.objects.filter(image_name= img_name, user = user).first()
            print(existing_data)
            if existing_data:
                serializer.update(existing_data, serializer.validated_data)
                return Response({'msg':'older data updated'}, status= status.HTTP_200_OK)
            serializer.save(user=self.request.user)
            return Response({'msg':'Data created'}, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)





    def put(self, request, nm = None, format = None):
        name = nm
        user = self.request.user
        dt = Annote.objects.filter(image_name = name, user= user)
        if not dt:
            return Response({'detail': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            dt = Annote.objects.get(image_name = name, user= user)
            serializer = AnnoteSerializer(dt, data= request.data)
            if serializer.is_valid():
                dbImageName = dt.image_name
                if dbImageName != serializer.validated_data['image_name']:
                    return Response({'msg':"You cannot change image name"}, status.HTTP_400_BAD_REQUEST)
                input_data = set(serializer.initial_data.keys())
                required_fields = set(serializer.fields.keys())
                ext_data =  input_data - required_fields 
                if ext_data:
                    return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response({'msg':'Complete Data updated'})
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)




    def patch(self, request, nm = None, format = None):
        name = nm
        user = self.request.user
        dt = Annote.objects.filter(image_name = name, user= user)
        if not dt:
            return Response({'detail': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            dt = Annote.objects.get(image_name = name, user= user)
            serializer = AnnoteSerializer(dt, data= request.data, partial = True)
            if serializer.is_valid():
                input_data = set(serializer.initial_data.keys())
                required_fields = set(serializer.fields.keys())
                ext_data =  input_data - required_fields 
                if ext_data:
                    return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
                img = "image_name"
                if img in input_data:
                    dbImageName = dt.image_name
                    if dbImageName != serializer.validated_data['image_name']:
                        return Response({'msg':"You cannot change image name"}, status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response({'msg':'Partial Data updated'})
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)


    # def patch(self, request, nm=None, format=None):
    #     name = nm
    #     user = self.request.user
    #     try:
    #         instance = Annote.objects.get(image_name=name, user=user)
    #     except Annote.DoesNotExist:
    #         return Response({'detail': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = AnnoteSerializer(instance, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'msg': 'Partial Data updated'})
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, nm = None, forma = None):
        name = nm
        user = self.request.user
        dt = Annote.objects.filter(image_name =name, user= user)
        if not dt:
            return Response({'detail': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            dt = Annote.objects.get(image_name = name)
            dt.delete()
            return Response({'msg':'Data deleted'})




## store data in RDS and S3 bucket using one url

    # def post(self, request, format =None):
    #     serializer = AnnoteSerializer(data= request.data)
    #     user = self.request.user
    #     if serializer.is_valid():
    #         input_data = set(serializer.initial_data.keys())
    #         required_fields = set(serializer.fields.keys())
    #         ext_data =  input_data - required_fields 
    #         if ext_data:
    #             return Response({'msg':f"You have provided extra field {ext_data}"}, status.HTTP_400_BAD_REQUEST)
    #         img_name = serializer.validated_data['image_name']
    #         existing_data = Annote.objects.filter(image_name= img_name, user = user).first()
    #         if existing_data:
    #             serializer.update(existing_data, serializer.validated_data)
    #             return Response({'msg':'older data updated'}, status= status.HTTP_200_OK)
    #                     ## for AWS
    #         data = serializer.data
    #         json_data = json.dumps(data)
    #         name = img_name.rsplit(".", 1)[0]
    #         file_name = f'{name}.json'
    #         file = ContentFile(json_data.encode())
    #         file_path = default_storage.save(file_name, file)
    #         file_url = default_storage.url(file_path)

    #         serializer.save(user=self.request.user)
    #         return Response({'msg':'Data created'}, status= status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)