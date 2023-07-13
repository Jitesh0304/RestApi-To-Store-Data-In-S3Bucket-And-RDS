from rest_framework import serializers
from .models import AwsCredential



import boto3
from botocore.client import ClientError


class AwsSerializeres(serializers.ModelSerializer):
    class Meta:
        model = AwsCredential
        fields = "__all__"
        read_only_fields = ['user']
        

                ## this is for post request.... With the help of this it can recognise the user automatically
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


            ## this is for patch request
    def update(self, instance, validated_data):
        accessID = validated_data.get('accessID', instance.accessID)
        secretKey = validated_data.get('secretKey', instance.secretKey)
        bucketName = validated_data.get('bucketName', instance.bucketName)
        regionName = validated_data.get('regionName', instance.regionName)
        try:
            s3_client = boto3.client('s3',
                                    aws_access_key_id = accessID,
                                    aws_secret_access_key = secretKey)
            s3_client.head_bucket(Bucket=bucketName)                     
            bucket_exit = 'Yes'
        except ClientError:
            bucket_exit = 'No'
        if bucket_exit == 'Yes':
            instance.accessID = accessID
            instance.secretKey = secretKey
            instance.bucketName = bucketName
            instance.regionName = regionName
            instance.save()
            return instance
        else:
            raise serializers.ValidationError({'msg': 'This bucket does not exist !! Please Enter correct data'})


