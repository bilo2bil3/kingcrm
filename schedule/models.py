import datetime
from django.db import models
from django.core.exceptions import ValidationError

from leads.models import Lead, User

# Create your models here.
class Schedule(models.Model):
    lead = models.ForeignKey(Lead, related_name='lead_reminder', on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    date = models.DateField()
    time = models.TimeField()
    user = models.ForeignKey(User, related_name='schedule', on_delete=models.CASCADE, default=1)
    
    def __str__(self) -> str:
        return self.title

class ReminderNotification(models.Model):
    user = models.ForeignKey(User, related_name='reminder_notifications', on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message = models.CharField(max_length=30)
    reminder_on = models.DateTimeField()
    sent = models.BooleanField(default=False)
    # read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["-reminder_on"]