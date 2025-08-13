release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn conf.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --log-file -