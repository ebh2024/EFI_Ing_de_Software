#!/bin/bash
# Compile translation messages
echo "Compiling translation messages..."
python manage.py compilemessages

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser 'admin' if it doesn't exist..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

# Start the Django development server
echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000
