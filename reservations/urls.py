from django.urls import path
from .views import CreateReservationView, ListReservationView, ReleaseReservationView

urlpatterns = [
    path('', ListReservationView.as_view(), name='list_reservations'),
    path('create/', CreateReservationView.as_view(), name='create_reservation'),
    path('<int:pk>/release/', ReleaseReservationView.as_view(), name='release_reservation'),
]