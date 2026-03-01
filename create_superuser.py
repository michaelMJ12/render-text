import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Atendance.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email="rotimimichaeljames@gmail.com").exists():
    User.objects.create_superuser(
        email="rotimimichaeljames@gmail.com",
        password="admin"
    )