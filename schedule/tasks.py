import json
from channels.layers import get_channel_layer
from celery import shared_task
from asgiref.sync import async_to_sync
from .models import ReminderNotification
from celery import Celery, states
from celery.exceptions import Ignore
import asyncio

@shared_task(bind=True)
def reminder_notification(self, reminder_id):
    try:
        notification = ReminderNotification.objects.get(pk=reminder_id)
        channel_layer = get_channel_layer()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(channel_layer.group_send(
            'notification_reminder', {
                'type': 'send_notification',
                'message': {
                    "message": notification.message,
                    "user_id": notification.user.id,
                    "lead_id": notification.lead.id,
                }
            }
        ))
        notification.sent = True
        notification.save()
    except ReminderNotification.DoesNotExist:
        self.update_state(
            state = 'FAILURE',
            meta = {'exe': "Not Found"}
        )
        raise Ignore()
    except:
        self.update_state(
            state = 'FAILURE',
            meta = {'exe': "Failed"}
        )
        raise Ignore()
    return "Done"