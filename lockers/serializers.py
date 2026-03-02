from rest_framework import serializers
from .models import Locker

class LockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locker
        fields = ['id', 'locker_number', 'location', 'status', 'assigned_to', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'assigned_to', 'created_at', 'updated_at']