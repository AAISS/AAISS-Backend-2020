source ./aaiss-backend-env/bin/activate
PORT=${1:-8000}
python manage.py runserver localhost:$PORT
