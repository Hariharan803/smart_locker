# reservations/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
import logging

from .models import Reservation
from .serializers import ReservationSerializer
from lockers.models import Locker

# ---------------------
# Logger setup
# ---------------------
logger = logging.getLogger(__name__)

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ---------------------
    # Queryset based on user
    # ---------------------
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            queryset = Reservation.objects.all()
        else:
            queryset = Reservation.objects.filter(user=user)

        # Log the list view
        logger.info(
            "Reservations list fetched",
            extra={
                "event_type": "reservation_list",
                "user_id": user.id,
                "count": queryset.count(),
                "ip": self.request.META.get("REMOTE_ADDR"),
            }
        )
        return queryset

    # ---------------------
    # Create reservation
    # ---------------------
    def perform_create(self, serializer):
        user = self.request.user
        locker = serializer.validated_data['locker']

        # Check if user already has active reservation
        if Reservation.objects.filter(user=user, released_at__isnull=True).exists():
            logger.warning(
                "User attempted multiple active reservations",
                extra={"event_type": "reservation_failed", "user_id": user.id, "locker_id": locker.id}
            )
            raise ValidationError("You already have an active reservation.")

        # Check locker availability
        if locker.status != 'available':
            logger.warning(
                "User attempted to reserve an occupied locker",
                extra={"event_type": "reservation_failed", "user_id": user.id, "locker_id": locker.id}
            )
            raise ValidationError("Locker is not available.")

        # Update locker
        locker.status = 'occupied'
        locker.assigned_to = user
        locker.save()

        # Save reservation
        reservation = serializer.save(user=user)

        # Log reservation creation
        logger.info(
            "Reservation created",
            extra={
                "event_type": "reservation_created",
                "user_id": user.id,
                "locker_id": locker.id,
                "reservation_id": reservation.id,
                "ip": self.request.META.get("REMOTE_ADDR"),
            }
        )

        # Invalidate cached available lockers
        cache.delete("available_lockers")

    # ---------------------
    # Release reservation
    # ---------------------
    @action(detail=True, methods=['put'])
    def release(self, request, pk=None):
        reservation = self.get_object()
        locker = reservation.locker
        user = request.user

        if reservation.released_at:
            logger.warning(
                "User attempted to release already released locker",
                extra={"event_type": "release_failed", "user_id": user.id, "locker_id": locker.id}
            )
            raise ValidationError("Locker already released.")

        if locker.assigned_to != user:
            logger.warning(
                "User attempted to release locker not owned",
                extra={"event_type": "release_forbidden", "user_id": user.id, "locker_id": locker.id}
            )
            return Response({"error": "You cannot release this locker"}, status=status.HTTP_403_FORBIDDEN)

        # Release locker
        reservation.released_at = timezone.now()
        locker.status = 'available'
        locker.assigned_to = None
        locker.save()
        reservation.save()

        # Log release
        logger.info(
            "Reservation released",
            extra={
                "event_type": "reservation_released",
                "user_id": user.id,
                "locker_id": locker.id,
                "reservation_id": reservation.id,
                "ip": self.request.META.get("REMOTE_ADDR"),
            }
        )

        # Invalidate cached available lockers
        cache.delete("available_lockers")

        return Response(self.get_serializer(reservation).data)

    # ---------------------
    # List of available lockers (cached)
    # ---------------------
    @action(detail=False, methods=['get'])
    def available(self, request):
        cache_key = "available_lockers"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(
                "Returned cached available lockers",
                extra={
                    "event_type": "available_lockers_cached",
                    "user_id": request.user.id,
                    "count": len(cached_data),
                    "ip": request.META.get("REMOTE_ADDR"),
                }
            )
            return Response(cached_data)

        lockers = Locker.objects.filter(status="available")
        serializer = ReservationSerializer(lockers, many=True)  # If you want only locker info, you might use LockerSerializer

        cache.set(cache_key, serializer.data, timeout=60)

        logger.info(
            "Available lockers fetched from DB",
            extra={
                "event_type": "available_lockers_fetched",
                "user_id": request.user.id,
                "count": lockers.count(),
                "ip": request.META.get("REMOTE_ADDR"),
            }
        )

        return Response(serializer.data)