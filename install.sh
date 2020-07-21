#!/usr/bin/env bash
sudo apt update
sudo apt install python3-pip
sudo apt-get install python3-venv
python3 -m venv aaiss-backend-venv
source ./aaiss-backend-venv/bin/activate
pip3 install -r requirements.txt
echo  "SECRET_KEY=(dosen't matter using development key for now)
EMAIL_HOST=none
EMAIL_PORT=0
EMAIL_HOST_USER=none
EMAIL_HOST_PASSWORD=none
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
MERCHANT_ID=none
BASE_URL=" >> ./aaiss_backend/.env
python3 manage.py migrate
echo "from backend_api.models import Account; Account.objects.create_superuser('$1', '$2')" | python manage.py shell
