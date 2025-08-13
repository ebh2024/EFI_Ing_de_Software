from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        self.stdout.write('Checking for superuser "admin"...')
        if not User.objects.filter(username='admin').exists():
            self.stdout.write('Superuser "admin" not found, creating...')
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Successfully created superuser "admin"'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser "admin" already exists.'))
