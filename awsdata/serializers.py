from rest_framework import serializers
from .models import *



class AwsAnnoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwsAnnote
        fields = "__all__"

    def update(self, instance, validated_data):
            # Update the instance with the validated data
        instance.image_name = validated_data.get('image_name', instance.image_name)
        instance.bounding_boxes = validated_data.get('bounding_boxes', instance.bounding_boxes)
        instance.image_data = validated_data.get('image_data', instance.image_data)
        instance.save()
        return instance