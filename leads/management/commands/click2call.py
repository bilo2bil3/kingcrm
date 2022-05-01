from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    CALL_ENDPOINT = 'https://w2mtrading.coperato.net/gaya/api_ns/Click2Call/byAgent'
    HANGUP_ENDPOINT = ''
    AGENT_NUMBER = '997'
    TEST_CLIENT_NUMBER = '+201023459934'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('agent_number', type=str)
        # parser.add_argument('client_number', type=str)

    def handle(self, *args, **options):
        # agent_number = options['agent_number']
        # client_number = options['client_number']
        r = requests.post(
            self.CALL_ENDPOINT,
            data={
                'agent': self.AGENT_NUMBER,
                'phone_num': self.TEST_CLIENT_NUMBER
            }
        )
        # print(r.status_code)
        # print(r.json())
        # print(r.request.body)
