source ./aaiss-backend-env/bin/activate
PORT=${1:-8000}
python3 manage.py runserver localhost:$PORT
