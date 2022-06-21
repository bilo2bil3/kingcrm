from django.contrib import admin

from schedule.models import Schedule, ReminderNotification

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'lead', 'date', 'time']

# Register your models here.
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(ReminderNotification)