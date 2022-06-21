from django.contrib import admin

from schedule.models import Schedule, ReminderNotification

# Register your models here.
admin.site.register(Schedule)
admin.site.register(ReminderNotification)