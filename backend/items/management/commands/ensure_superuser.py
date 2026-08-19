import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create a Django superuser from environment variables if one does not "
        "already exist. Idempotent and safe to run on every deploy. Reads "
        "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and "
        "DJANGO_SUPERUSER_PASSWORD."
    )

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write(
                'ensure_superuser: DJANGO_SUPERUSER_USERNAME and '
                'DJANGO_SUPERUSER_PASSWORD are not both set; skipping.'
            )
            return

        user = User.objects.filter(username=username).first()

        if user is None:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'ensure_superuser: created superuser "{username}".'
                )
            )
            return

        # Promote an existing account to admin if needed, but never overwrite
        # an existing password automatically.
        if not (user.is_staff and user.is_superuser):
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=['is_staff', 'is_superuser'])
            self.stdout.write(
                self.style.SUCCESS(
                    f'ensure_superuser: promoted existing user "{username}" '
                    'to superuser.'
                )
            )
        else:
            self.stdout.write(
                f'ensure_superuser: superuser "{username}" already exists; '
                'no change.'
            )
