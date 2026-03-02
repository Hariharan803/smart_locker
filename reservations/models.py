from django.db import models
from users.models import User
from lockers.models import Locker

class Reservation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    locker = models.ForeignKey(
        Locker,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    reserved_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} -> Locker {self.locker.locker_number}"