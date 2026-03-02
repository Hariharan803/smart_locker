from django.db import models
from users.models import User

class Locker(models.Model):
    STATUS_CHOICES = (('available', 'Available'), ('occupied', 'Occupied'))

    locker_number = models.PositiveIntegerField(unique=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lockers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Locker {self.locker_number} - {self.status}"