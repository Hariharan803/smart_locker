from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lockers.views import LockerViewSet
from reservations.views import ReservationViewSet

router = DefaultRouter()
router.register('lockers', LockerViewSet, basename='locker')
router.register('reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/', include(router.urls)),
]