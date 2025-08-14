web: gunicorn conf.wsgi --log-file - 
#or works good with external database
web: python manage.py migrate && gunicorn conf.wsgi