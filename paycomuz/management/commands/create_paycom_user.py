# Django
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

# Settings check
assert settings.PAYCOM_SETTINGS.get('SECRET_KEY') != None

# User model
user_model = get_user_model()


class Command(BaseCommand):
    help = 'Create User for PaycomUz'
    username = 'Paycom'
    password = settings.PAYCOM_SETTINGS['SECRET_KEY']
    username_key = user_model.USERNAME_FIELD

    def handle(self, *args, **options):
        try:
            user, _ = user_model.objects.update_or_create(**{self.username_key: self.username})
            user.set_password(self.password)
            user.save()
            self.stdout.write(self.style.SUCCESS('Success created user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
