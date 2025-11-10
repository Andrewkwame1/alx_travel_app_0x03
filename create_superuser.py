#!/usr/bin/env python
"""
Auto-create superuser for Django app on deployment
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@alxtravelapp.com', 'admin123')
    print("✓ Superuser created successfully!")
    print("  Username: admin")
    print("  Password: admin123")
    print("  Email: admin@alxtravelapp.com")
else:
    print("✓ Superuser already exists!")
