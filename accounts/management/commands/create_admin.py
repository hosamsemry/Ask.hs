from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import dotenv
import os
dotenv.load_dotenv()
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(f'admin', {os.getenv('ADMIN_EMAIL')},{os.getenv('ADMIN_PASSWORD')})
            self.stdout.write(self.style.SUCCESS("Superuser created!"))
