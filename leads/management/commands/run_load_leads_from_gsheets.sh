#!/bin/bash
cd $HOME/kingcrm
source $HOME/.local/share/virtualenvs/kingcrm-wDqBJNVH/bin/activate
export GOOGLE_API_KEY=AIzaSyBgmTksVWTTuAfAbc46XcR9E0wjlvtUM_g
export READ_DOT_ENV_FILE=True
python manage.py load_leads_from_gsheets
