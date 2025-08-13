release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn your_project_name.wsgi:application --bind 0.0.0.0:$PORT