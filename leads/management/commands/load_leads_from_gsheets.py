import requests
import environ
from django.core.management.base import BaseCommand
from leads.models import Lead, LeadsSheet


env = environ.Env()

class Command(BaseCommand):
    API_KEY = env('GOOGLE_API_KEY')
    ENDPOINT_URL = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}'
    PARAMS = {'key': API_KEY}
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for sheet in LeadsSheet.objects.all():
            sheet_id = sheet.url.split('d/')[-1].split('/')[0]
            sheet_range = f'{sheet.sheet_name}!A:H'

            url = self.ENDPOINT_URL.format(sheet_id, sheet_range)
            r = requests.get(url, params=self.PARAMS)
            if r.status_code != 200:
                raise Exception(f'connect to gsheets api | ERROR | {r.status_code}')

            rows = r.json().get('values', [])[1:]

            # to skip duplicate leads while uploading
            # we need to keep track of leads added for current session
            leads_to_add = []
            for row in rows:
                if row[5] in [lead[5] for lead in leads_to_add]:
                    continue
                leads_to_add.append(row)
            
            for lead in leads_to_add:
                [first_name, last_name, source, service, email, phone_number, country, campaign] = lead

                # skip duplicate leads
                # if new lead exist in db
                if phone_number in Lead.objects.values_list('phone_number', flat=True):
                    continue

                Lead.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    source=source,
                    service=service,
                    email=email,
                    phone_number=phone_number,
                    country=country,
                    campaign=campaign,
                    organisation=sheet.organisation,
                    agent=sheet.agent
                )
