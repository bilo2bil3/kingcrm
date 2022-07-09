import requests
import environ
from django.core.management.base import BaseCommand
from leads.management.commands.utils import add_leads
from leads.models import Lead, LeadsSheet


env = environ.Env()

class Command(BaseCommand):
    API_KEY = env('GOOGLE_API_KEY')
    ENDPOINT_URL = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}'
    PARAMS = {'key': API_KEY}
    def add_arguments(self, parser):
        pass

    # function to get the data from google sheets
    def get_data(self, sheet_id, sheet_range):
        url = self.ENDPOINT_URL.format(sheet_id, sheet_range)
        response = requests.get(url, params=self.PARAMS)
        return response.json()


       
            #     [first_name, last_name, source, service, email, country_code, phone_number, country, campaign] = lead

            #     phone_number = country_code + phone_number
                
            #     # skip duplicate leads
            #     # if new lead exist in db
            #     if phone_number in Lead.objects.values_list('phone_number', flat=True):
            #         continue

            #     Lead.objects.create(
            #         first_name=first_name,
            #         last_name=last_name,
            #         source=source,
            #         service=service,
            #         email=email,
            #         phone_number=phone_number,
            #         country=country,
            #         campaign=campaign,
            #         organisation=sheet.organisation,
            #         agent=sheet.agent
            #     )
