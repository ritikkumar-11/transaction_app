from .models import *
from rest_framework import serializers

class TransctionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Transction
        fields = '__all__'
