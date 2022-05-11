#!/bin/bash
cd $HOME/kingcrm
source $HOME/.local/share/virtualenvs/kingcrm-EZ-qjEbz/bin/activate
export GOOGLE_API_KEY=AIzaSyDu3ba8tAbu9vUm57tS3LmpTZ5xFTaqU8s
export READ_DOT_ENV_FILE=True
python manage.py load_leads_from_gsheets
