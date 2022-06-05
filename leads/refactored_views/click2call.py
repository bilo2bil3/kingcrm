import datetime
import json
import requests
import environ
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
from leads.models import Lead


env = environ.Env()
READ_DOT_ENV_FILE = env.bool("READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    environ.Env.read_env()


@login_required
def click_to_call(request):
    if request.method == "POST":
        CALL_ENDPOINT = env("CLICK2CALL_CALL_ENDPOINT")
        payload = json.loads(request.body)
        lead_id = payload["lead"]
        lead = Lead.objects.get(pk=lead_id)
        agent_number = lead.agent.user.click2call_extension
        client_number = lead.phone_number
        print(f"###click2call: {agent_number} calling {client_number}")
        try:
            r = requests.post(
                CALL_ENDPOINT,
                data={
                    "agent": agent_number,
                    "phone_num": client_number,
                },
            )
            lead.last_called = datetime.datetime.now()
            lead.save()
            return HttpResponse("")
        except Exception as e:
            return HttpResponse(str(e))


@login_required
def hangup_call(request):
    if request.method == "POST":
        print("###click2call: disconneting")
        HANGUP_ENDPOINT = env("CLICK2CALL_HANGUP_ENDPOINT")
        agent_number = request.user.click2call_extension
        print(f"###click2call: {agent_number} hanging up")
        try:
            r = requests.post(HANGUP_ENDPOINT, data={"agent": agent_number})
            return HttpResponse("")
        except Exception as e:
            return HttpResponse(str(e))
