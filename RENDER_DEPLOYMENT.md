# 🚀 Render Deployment Guide - ALX Travel App

## Overview
Render is a modern cloud platform with a free tier. This guide will deploy your Django app to Render in minutes.

---

## Step 1: Create Render Account

1. Go to https://render.com/
2. Sign up with GitHub (easiest option)
3. Connect your GitHub account

---

## Step 2: Create `render.yaml` Configuration File

In your project root (`~/alx_travel_app_0x03/`), create a file called `render.yaml`:

```yaml
services:
  - type: web
    name: alx-travel-app
    env: python
    plan: free
    buildCommand: >
      pip install -r requirements.txt &&
      python alx_travel_app/manage.py migrate &&
      python alx_travel_app/manage.py collectstatic --noinput
    startCommand: gunicorn alx_travel_app.wsgi:application
    envVars:
      - key: DEBUG
        value: false
      - key: SECRET_KEY
        generateValue: true
      - key: ALLOWED_HOSTS
        value: "*"
      - key: DATABASE_URL
        fromDatabase:
          name: alx-travel-db
          property: connectionString
    healthCheckPath: /
databases:
  - name: alx-travel-db
    plan: free
```

Add this file to git:

```bash
cd ~/alx_travel_app_0x03
git add render.yaml
git commit -m "feat: Add Render deployment configuration"
git push origin main
```

---

## Step 3: Install Gunicorn

Gunicorn is the production server. Add it to requirements.txt:

```bash
cd ~/alx_travel_app_0x03
echo "gunicorn==21.2.0" >> requirements.txt
git add requirements.txt
git commit -m "feat: Add gunicorn for production deployment"
git push origin main
```

---

## Step 4: Create Web Service on Render

1. **Go to https://dashboard.render.com/**
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub repository**
   - Select your GitHub account
   - Search for `alx_travel_app_0x03`
   - Click "Connect"
4. **Configure Service:**
   - **Name:** `alx-travel-app`
   - **Region:** Choose closest to you (e.g., `us-east-1`)
   - **Branch:** `main`
   - **Root Directory:** Leave blank
   - **Build Command:** (auto-detected from render.yaml)
   - **Start Command:** (auto-detected from render.yaml)
   - **Plan:** Free
5. **Click "Create Web Service"**

Render will now:
- Deploy your code
- Create a PostgreSQL database
- Run migrations automatically
- Collect static files
- Start your app

This takes 3-5 minutes. You'll see deployment logs.

---

## Step 5: Wait for Deployment

Monitor the deployment:
- Green checkmark = Success ✅
- Red X = Failed ❌

If it fails, check the logs:
1. Click on your service
2. Scroll to "Logs" section
3. Look for error messages

---

## Step 6: Access Your Live App

Once deployed, you'll get a URL like:
```
https://alx-travel-app.onrender.com/
```

Visit these endpoints:

| Feature | URL |
|---------|-----|
| **Main App** | https://alx-travel-app.onrender.com/ |
| **Admin Panel** | https://alx-travel-app.onrender.com/admin/ |
| **Swagger API** | https://alx-travel-app.onrender.com/swagger/ |
| **API Root** | https://alx-travel-app.onrender.com/api/ |

---

## Step 7: Create Superuser on Render

Since you can't access bash directly on free Render, you need to create a superuser script.

Create `create_superuser.py` in project root:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created!")
else:
    print("Superuser already exists!")
```

Update `render.yaml` buildCommand:

```yaml
buildCommand: >
  pip install -r requirements.txt &&
  python alx_travel_app/manage.py migrate &&
  python create_superuser.py &&
  python alx_travel_app/manage.py collectstatic --noinput
```

Commit and push:

```bash
cd ~/alx_travel_app_0x03
git add create_superuser.py render.yaml
git commit -m "feat: Auto-create superuser on deployment"
git push origin main
```

Render will auto-redeploy!

---

## Step 8: Access Admin Panel

1. Go to: `https://alx-travel-app.onrender.com/admin/`
2. Login with:
   - **Username:** `admin`
   - **Password:** `admin123` (or change in script)

---

## Step 9: Test Swagger API

1. Go to: `https://alx-travel-app.onrender.com/swagger/`
2. You should see interactive API documentation
3. Try creating a booking or listing

---

## Troubleshooting

### Issue: "Build failed" or "Deployment failed"

**Check logs:**
1. Go to your service on Render dashboard
2. Click on **"Logs"** tab
3. Look for error messages

**Common issues:**
- Missing dependencies: Add to `requirements.txt`
- Wrong directory: Check `render.yaml` paths
- Database error: Check database connection in logs

### Issue: 503 Service Unavailable

**Likely cause:** Free tier is overloaded

**Solution:**
- Render free tier has limitations
- Wait 5-10 minutes
- Try again

### Issue: Admin login doesn't work

**Solution:**
1. Update superuser password in `create_superuser.py`
2. Commit and push
3. Render will redeploy
4. Login with new credentials

### Issue: Static files not loading

**Check:**
1. Logs show "collectstatic... OK"?
2. `STATIC_ROOT` is set in settings.py
3. Swagger/admin CSS is broken? Refresh page

---

## Environment Variables on Render

Render automatically sets from `render.yaml`:
- `SECRET_KEY` - Generated randomly
- `DATABASE_URL` - PostgreSQL connection string
- `DEBUG` - Set to `false`
- `ALLOWED_HOSTS` - Set to `*`

To add more:
1. Go to your service
2. Click **"Environment"**
3. Add new variables
4. Service auto-redeploys

---

## Updating Your App

To deploy code changes:

```bash
cd ~/alx_travel_app_0x03
git add -A
git commit -m "feat: Your changes"
git push origin main
```

Render automatically redeploys from GitHub!

---

## Making It Permanent (Optional Paid Upgrades)

- **Free tier** works but may spin down after 15 minutes
- **Paid tier** ($7/month+) keeps it always running
- Upgrade anytime from Render dashboard

---

## Live Deployment Complete! 🎉

Your ALX Travel App is now live on Render with:
- ✅ PostgreSQL database
- ✅ Django REST API
- ✅ Swagger documentation
- ✅ Admin panel
- ✅ Static files served
- ✅ HTTPS/SSL included

**Next Steps:**
1. Test all API endpoints via Swagger
2. Create test bookings and listings
3. Verify emails work
4. Monitor performance
5. Upgrade to paid tier if needed

---

## Support

- **Render Docs:** https://render.com/docs
- **Django Docs:** https://docs.djangoproject.com/
- **DRF Swagger:** https://drf-yasg.readthedocs.io/

**Your deployment is complete!** 🚀
