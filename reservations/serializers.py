from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'locker', 'user', 'reserved_at', 'released_at']
        read_only_fields = ['user', 'reserved_at', 'released_at']