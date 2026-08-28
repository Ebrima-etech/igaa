release: python manage.py migrate
web: gunicorn igaa_project.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 120
