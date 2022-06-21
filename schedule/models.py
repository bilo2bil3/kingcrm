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
    
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        # self.time = datetime.datetime.strftime(self.time, "%Y-%m-%dT%H:%M")
        if datetime.datetime.strptime(self.date, "%Y-%m-%d").date() < datetime.date.today():
            raise ValidationError("The date cannot be in the past!")
        super(Schedule, self).save(*args, **kwargs)

class ReminderNotification(models.Model):
    user = models.ForeignKey(User, related_name='reminder_notifications', on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message = models.CharField(max_length=30)
    reminder_on = models.DateTimeField()
    sent = models.BooleanField(default=False)
    # read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["-reminder_on"]