from django.urls import path
from .views import (
    CreateReservationView,
    ListReservationView,
    ReservationDetailView,
    ReleaseReservationView
)

urlpatterns = [
    path('', ListReservationView.as_view(), name='list_reservations'),
    path('<int:pk>/', ReservationDetailView.as_view(), name='reservation_detail'),
    path('<int:pk>/release/', ReleaseReservationView.as_view(), name='release_reservation'),
]