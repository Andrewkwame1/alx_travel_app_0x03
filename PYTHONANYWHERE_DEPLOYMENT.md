# 🚀 PythonAnywhere Deployment - Fresh Start Guide

## Overview
This guide will walk you through deploying the ALX Travel App to PythonAnywhere from scratch.

---

## PART 1: Initial Setup on PythonAnywhere

### Step 1: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/
2. Sign up with your email
3. You get a free account with limited features

### Step 2: Open a Bash Console
1. Log in to PythonAnywhere
2. Click **Consoles** (top menu)
3. Click **Bash** - a new terminal will open

---

## PART 2: Clone Your Repository

### Step 3: Clone the Project
In the bash console, run:

```bash
cd ~
git clone https://github.com/Andrewkwame1/alx_travel_app_0x03.git
cd alx_travel_app_0x03
ls -la
```

You should see:
```
alx_travel_app/
docs/
README.md
requirements.txt
.gitignore
```

---

## PART 3: Set Up Python Virtual Environment

### Step 4: Create Virtual Environment with Python 3.10
```bash
# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 travel-env

# Verify it's activated (should show travel-env in prompt)
which python
```

Should output:
```
/home/Andrewkwame/.virtualenvs/travel-env/bin/python
```

---

## PART 4: Install Dependencies

### Step 5: Install Python Packages
```bash
cd ~/alx_travel_app_0x03

# Install all requirements
pip install -r requirements.txt
```

This will take 2-3 minutes. When done, you should see:
```
Successfully installed Django-5.2.7 celery-5.3.4 ...
```

---

## PART 5: Configure Django

### Step 6: Create .env File
Navigate to the correct directory:

```bash
cd ~/alx_travel_app_0x03/alx_travel_app
```

Create the `.env` file:

```bash
cat > .env << 'EOF'
SECRET_KEY=django-insecure-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
DEBUG=False
ALLOWED_HOSTS=Andrewkwame.pythonanywhere.com
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EOF
```

Verify it was created:
```bash
cat .env
```

### Step 7: Run Database Migrations
```bash
python manage.py migrate
```

You should see output like:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying listings.0002_payment... OK
```

If you get an error, make sure you're in the right directory: `~/alx_travel_app_0x03/alx_travel_app`

### Step 8: Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

When prompted:
- **Username:** `admin`
- **Email:** Your email
- **Password:** Something secure (remember this!)

Example:
```
Username: admin
Email address: your-email@example.com
Password: YourSecurePassword123!
Password (again): YourSecurePassword123!
Superuser created successfully.
```

### Step 9: Collect Static Files
This is important for Swagger UI and admin panel to work:

```bash
python manage.py collectstatic --noinput
```

You should see:
```
123 static files copied to '/home/Andrewkwame/alx_travel_app_0x03/alx_travel_app/staticfiles'
```

---

## PART 6: Configure PythonAnywhere Web App

### Step 10: Go to Web Configuration
1. Click **Web** (top menu)
2. Click **Add a new web app**
3. Select **Manual configuration**
4. Select **Python 3.10**

### Step 11: Configure WSGI File
1. Under "Code" section, click the WSGI configuration file link
2. Delete all existing content
3. Paste this:

```python
import os
import sys

# Add your project to the Python path
path = '/home/Andrewkwame/alx_travel_app_0x03'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'alx_travel_app.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. Click **Save**

### Step 12: Configure Virtual Environment
1. Back to Web tab
2. Scroll down to **Virtualenv** section
3. In the text field, paste: `/home/Andrewkwame/.virtualenvs/travel-env`
4. Press Enter or Tab

### Step 13: Configure Static Files
1. In the Web tab, scroll to **Static files** section
2. Add a new URL: `/static/`
3. Map to directory: `/home/Andrewkwame/alx_travel_app_0x03/alx_travel_app/staticfiles`

### Step 14: Reload Your Web App
1. At the top of Web tab, click the big green **Reload** button
2. Wait 5-10 seconds for the app to load

---

## PART 7: Verify Deployment

### Step 15: Visit Your Live Site
Open browser and go to:
```
https://Andrewkwame.pythonanywhere.com/
```

You should see your Django app running!

### Step 16: Access Admin Panel
Go to:
```
https://Andrewkwame.pythonanywhere.com/admin/
```

Log in with:
- Username: `admin`
- Password: (the one you created in Step 8)

### Step 17: Access Swagger API Documentation
Go to:
```
https://Andrewkwame.pythonanywhere.com/swagger/
```

You should see the interactive Swagger documentation with all your API endpoints!

---

## PART 8: Set Up Celery (Optional - Advanced)

Celery requires RabbitMQ which is not available on free PythonAnywhere. For now, the email backend is set to console mode, so emails will print to logs instead of actually sending.

If you need background tasks in production, you have options:
1. Use a paid PythonAnywhere plan with additional services
2. Use a different hosting platform that supports RabbitMQ
3. Use Celery with Redis-only setup (still requires Redis service)

For development purposes, the current setup works fine.

---

## TROUBLESHOOTING

### Issue: "DisallowedHost at /" error

**Cause:** ALLOWED_HOSTS not configured

**Fix:**
1. Edit `.env` file:
   ```bash
   cd ~/alx_travel_app_0x03/alx_travel_app
   nano .env
   ```
2. Make sure `ALLOWED_HOSTS=Andrewkwame.pythonanywhere.com`
3. Save and reload web app

### Issue: Swagger not showing

**Cause:** Static files not collected

**Fix:**
```bash
cd ~/alx_travel_app_0x03/alx_travel_app
python manage.py collectstatic --noinput
```

Then reload web app.

### Issue: 404 errors on API endpoints

**Cause:** Database migrations not run

**Fix:**
```bash
cd ~/alx_travel_app_0x03/alx_travel_app
python manage.py migrate
```

Then reload web app.

### Issue: "ModuleNotFoundError" when loading app

**Cause:** Virtual environment not configured correctly

**Fix:**
1. Go to Web tab
2. Check Virtualenv path: `/home/Andrewkwame/.virtualenvs/travel-env`
3. Verify with bash:
   ```bash
   ls -la ~/.virtualenvs/travel-env/bin/python
   ```
4. Reload web app

### Issue: Still getting errors?

**Check error logs:**
1. Go to Web tab
2. Scroll down to **Log files**
3. Click **Error log** to see detailed errors
4. Look for the specific error message

---

## SUCCESS CHECKLIST

✅ Check these to verify deployment is complete:

```bash
# In PythonAnywhere bash console:
cd ~/alx_travel_app_0x03/alx_travel_app

# 1. Check migrations are done
python manage.py showmigrations | grep "\[X\]"
# Should show all migrations marked with [X]

# 2. Check superuser exists
python manage.py shell
from django.contrib.auth.models import User
print(User.objects.filter(username='admin').exists())  # Should print True
exit()

# 3. Check static files collected
ls -la staticfiles/ | head -20
# Should show files like admin, rest_framework, drf_yasg, etc.

# 4. Check .env file exists
cat .env
# Should show all environment variables
```

---

## LIVE ENDPOINTS

Your application is now live! Here are your endpoints:

| Feature | URL |
|---------|-----|
| **Main App** | https://Andrewkwame.pythonanywhere.com/ |
| **Admin Panel** | https://Andrewkwame.pythonanywhere.com/admin/ |
| **Swagger API** | https://Andrewkwame.pythonanywhere.com/swagger/ |
| **API Root** | https://Andrewkwame.pythonanywhere.com/api/ |
| **Bookings API** | https://Andrewkwame.pythonanywhere.com/api/bookings/ |
| **Listings API** | https://Andrewkwame.pythonanywhere.com/api/listings/ |
| **Payments API** | https://Andrewkwame.pythonanywhere.com/api/payments/ |

---

## NEXT STEPS

1. **Test the API:** Use Swagger UI to create bookings and test endpoints
2. **Test Admin:** Log into admin panel to manage data
3. **Monitor:** Check error logs regularly for issues
4. **Update:** To deploy code changes, go to bash and run:
   ```bash
   cd ~/alx_travel_app_0x03
   git pull origin main
   cd alx_travel_app
   python manage.py migrate  # If migrations changed
   python manage.py collectstatic --noinput  # If static files changed
   ```
5. **Reload:** After changes, reload web app from Web tab

---

## SUPPORT

If you encounter issues:

1. **Check error logs:** Web tab → Error log
2. **Check bash console:** Run commands to verify setup
3. **Review this guide:** Common issues are in Troubleshooting section
4. **Django docs:** https://docs.djangoproject.com/en/5.2/
5. **DRF Swagger:** https://drf-yasg.readthedocs.io/

---

**Your deployment is complete! 🎉**

Your ALX Travel App is now live on PythonAnywhere with full API documentation available at the Swagger endpoint.
