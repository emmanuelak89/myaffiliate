from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import *

class BioSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    class Meta:
        model = Bio
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField()
    influencer = serializers.CharField()
    class Meta:
        model = Job
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):
    BidSentBy = serializers.CharField()
    class Meta:
        model = Job
        fields = '__all__'