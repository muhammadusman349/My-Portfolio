release: python manage.py migrate
web: gunicorn conf.asgi:application --bind 0.0.0.0:$PORT