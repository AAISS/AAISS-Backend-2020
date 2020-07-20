source ./aaiss-backend-env/bin/activate
python3 manage.py migrate
PORT=${1:-8000}
python3 manage.py runserver localhost:$PORT
