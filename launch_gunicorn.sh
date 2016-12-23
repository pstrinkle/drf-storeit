#!/bin/bash

# Sleep because it will start running this once db is up and running which doesn't yet signal that it's ready for
# connections.
sleep 10

# Apply database migrations
python manage.py migrate --settings image_app.settings.prod
# harmless if this runs every time.
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'fake@example.com', 'password123', first_name='admin', last_name='name')" | python manage.py shell --settings image_app.settings.prod

# If I just kept the static files separate for development then I couldn't run the server via manage.py;
# I'd always need to run nginx
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
touch /tmp/gunicorn.log
touch /tmp/access.log
tail -n 0 -f /tmp/*.log &

# Start Gunicorn processes (production mode!)
echo Starting Gunicorn.
exec gunicorn wsgi:application \
    --name api_django \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=info \
    --log-file=/tmp/gunicorn.log \
    --access-logfile=/tmp/access.log \
    "$@"

