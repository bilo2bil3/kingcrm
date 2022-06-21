from datetime import datetime
from django.conf import settings
from django.utils import timezone
import pytz
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from schedule.models import ReminderNotification
from django_celery_beat.models import PeriodicTask, CrontabSchedule

@receiver(post_save, sender=ReminderNotification)
def notification_handler(sender, instance, created, **kwargs):
    if created:
        date = instance.reminder_on
        date = date.astimezone(tz=pytz.timezone(settings.TIME_ZONE)),
        
        schedule = CrontabSchedule.objects.create(
            hour=date[0].hour,
            minute=date[0].minute,
            day_of_month=date[0].day,
            month_of_year=date[0].month,
            timezone=settings.TIME_ZONE
        )
        
        task = PeriodicTask.objects.create(
            crontab=schedule,
            name="reminder-notification-" + str(instance.id),
            task='schedule.tasks.reminder_notification',
            args=json.dumps((instance.id,))
        )