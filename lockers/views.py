# lockers/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.core.cache import cache
import logging

from .models import Locker
from .serializers import LockerSerializer

# Setup logger
logger = logging.getLogger(__name__)

class LockerViewSet(viewsets.ModelViewSet):
    serializer_class = LockerSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Locker.objects.all()
        return Locker.objects.filter(
            models.Q(status='available') |
            models.Q(assigned_to=user)
        )

    # ---------------------
    # List available lockers with Redis caching
    # ---------------------
    @action(detail=False, methods=['get'])
    def available(self, request):
        cache_key = "available_lockers"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returned available lockers from cache for user {request.user.id}")
            return Response(cached_data)

        lockers = Locker.objects.filter(status="available")
        serializer = self.get_serializer(lockers, many=True)

        cache.set(cache_key, serializer.data, timeout=60)
        logger.info(f"Queried DB for available lockers for user {request.user.id}")
        return Response(serializer.data)

    # ---------------------
    # Reserve a locker
    # ---------------------
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        locker = self.get_object()

        if locker.status == 'occupied':
            logger.warning(f"User {request.user.id} attempted to reserve occupied locker {locker.id}")
            return Response({"error": "Locker already occupied"}, status=status.HTTP_400_BAD_REQUEST)

        if Locker.objects.filter(assigned_to=request.user, status='occupied').exists():
            logger.warning(f"User {request.user.id} attempted to reserve multiple lockers")
            return Response({"error": "You already have a reserved locker"}, status=status.HTTP_400_BAD_REQUEST)

        locker.status = 'occupied'
        locker.assigned_to = request.user
        locker.save()

        logger.info(f"Locker {locker.id} reserved by user {request.user.id}")
        return Response({"message": "Locker reserved successfully", "locker_id": locker.id})

    # ---------------------
    # Release a locker
    # ---------------------
    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        locker = self.get_object()

        if locker.assigned_to != request.user:
            logger.warning(f"User {request.user.id} attempted to release locker {locker.id} they don't own")
            return Response({"error": "You cannot release this locker"}, status=status.HTTP_403_FORBIDDEN)

        locker.status = 'available'
        locker.assigned_to = None
        locker.save()

        logger.info(f"Locker {locker.id} released by user {request.user.id}")
        return Response({"message": "Locker released successfully", "locker_id": locker.id})