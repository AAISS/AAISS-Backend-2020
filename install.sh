python -m venv aaiss-backend-venv
source ./aaiss-backend-venv/bin/activate
pip install -r requirements.txt
echo  "SECRET_KEY=(dosen't matter using development key for now)
EMAIL_HOST=none
EMAIL_PORT=0
EMAIL_HOST_USER=none
EMAIL_HOST_PASSWORD=none
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
MERCHANT_ID=none
BASE_URL=" >> ./aaiss_backend/.env
python manage.py migrate
echo "from backend_api.models import Account; Account.objects.create_superuser('$1', '$2')" | python manage.py shell
