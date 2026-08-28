# Django Deployment on Render

This Django application is configured for deployment on [Render](https://render.com).

## Prerequisites

1. Render account (free or paid plan)
2. GitHub repository with the code
3. PostgreSQL database instance on Render

## Deployment Steps

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "PostgreSQL"
3. Name it: `gia-postgresql`
4. Choose appropriate plan and region
5. Click "Create Database"
6. Copy the connection string (you'll need it)

### 3. Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `gia-hajj-api`
   - **Environment**: `Python`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```
     gunicorn igaa_project.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 120
     ```
   - **Python Version**: `3.11.6`

### 4. Set Environment Variables

In Render dashboard, add these environment variables to your web service:

| Variable | Value | Notes |
|----------|-------|-------|
| `DEBUG` | `False` | Always False in production |
| `SECRET_KEY` | Generate a strong key | Or Render can generate one |
| `DATABASE_URL` | PostgreSQL connection string | From step 2 |
| `ALLOWED_HOSTS` | `*.onrender.com,gia-hajj-api.onrender.com` | Update with your domain |
| `CORS_ALLOWED_ORIGINS` | `https://kanb-seven.vercel.app,https://iga-blush.vercel.app` | Add your frontend URLs |

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Run migrations
   - Collect static files
   - Start the gunicorn server

Monitor the deployment in the **Logs** tab.

## After Deployment

### Access Your API

```
https://gia-hajj-api.onrender.com/
```

### Common URLs

- Admin: `https://gia-hajj-api.onrender.com/admin/`
- API Docs: `https://gia-hajj-api.onrender.com/api/` (if configured)
- Pilgrims: `https://gia-hajj-api.onrender.com/api/v1/pilgrims/`
- Payments: `https://gia-hajj-api.onrender.com/api/v1/payments/`

### Create Superuser

After first deployment, run:

```bash
# Via Render Shell
python manage.py createsuperuser

# Or via SSH (if available)
ssh your-service@your-service.onrender.com
python manage.py createsuperuser
```

## Troubleshooting

### Static Files Not Loading

Render uses WhiteNoise to serve static files. Make sure:
- `whitenoise` is in `requirements.txt` ✓
- `WhiteNoiseMiddleware` is in MIDDLEWARE ✓
- Run `python manage.py collectstatic --noinput`

### Database Connection Issues

Check that:
- `DATABASE_URL` environment variable is set correctly
- PostgreSQL instance is running
- Connection string format: `postgresql://user:password@host:port/database`

### CORS Errors

Ensure your frontend URLs are in `CORS_ALLOWED_ORIGINS`:
- `https://kanb-seven.vercel.app`
- `https://iga-blush.vercel.app`
- Any other frontend domains

### Migrations Failed

1. Check logs: `python manage.py showmigrations`
2. Run manually: `python manage.py migrate --plan`

## Performance Tips

### Workers
Current config uses 4 workers. For higher traffic:
```
--workers 6 or 8
```

### Connection Pooling
Add to settings.py for PostgreSQL:
```python
DATABASES['default']['CONN_MAX_AGE'] = 600
```

### Caching (Optional)
Use Render's Redis instance for caching:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
    }
}
```

## Environment Variables Reference

**Critical for Production:**
- `SECRET_KEY` - Django secret key (generate one!)
- `DEBUG` - Must be `False`
- `DATABASE_URL` - PostgreSQL connection string
- `ALLOWED_HOSTS` - Your domain(s)
- `CORS_ALLOWED_ORIGINS` - Frontend domain(s)

**Optional:**
- `JWT_SECRET` - JWT signing key
- `EMAIL_BACKEND` - Email configuration
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `CELERY_BROKER_URL` - For async tasks (if using Celery)

## Useful Render Commands

```bash
# View logs
render logs --service gia-hajj-api

# Restart service
render restart --service gia-hajj-api

# Open shell to service
render shell --service gia-hajj-api
```

## Additional Resources

- [Render Django Guide](https://render.com/docs/deploy-django)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [dj-database-url](https://github.com/jacobian/dj-database-url)
