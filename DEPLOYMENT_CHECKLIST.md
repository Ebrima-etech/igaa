# Render Deployment Checklist

## Pre-Deployment: Local Testing

- [ ] Run `python manage.py test` to verify all tests pass
- [ ] Run `python check_production.py` to verify production settings
- [ ] Test with PostgreSQL locally:
  ```bash
  # Create a .env.local with: DATABASE_URL=postgresql://...
  python manage.py migrate
  python manage.py runserver
  ```
- [ ] Verify static files work:
  ```bash
  python manage.py collectstatic --noinput
  ```
- [ ] All git changes committed and pushed to GitHub

## Render Preparation

- [ ] Create Render account at https://render.com
- [ ] Connect GitHub repository to Render
- [ ] Create PostgreSQL instance:
  - [ ] Database name: `gia-postgresql`
  - [ ] Region: Select appropriate region
  - [ ] Copy connection string
  
## Environment Variables to Set on Render

### Required
- [ ] `DEBUG` = `False`
- [ ] `SECRET_KEY` = Generate new secret key (see below)
- [ ] `DATABASE_URL` = PostgreSQL connection string from Render
- [ ] `ALLOWED_HOSTS` = `*.onrender.com,gia-hajj-api.onrender.com`
- [ ] `CORS_ALLOWED_ORIGINS` = Frontend URLs

### Optional but Recommended
- [ ] `JWT_SECRET` = Generate new JWT secret
- [ ] `EMAIL_BACKEND` = For production emails

## Generate Secure Keys

### Generate Django SECRET_KEY
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Generate JWT Secret
```python
import secrets
print(secrets.token_urlsafe(32))
```

## Deployment Steps

1. **Create Web Service on Render**
   - [ ] Repository: Select your GitHub repo
   - [ ] Branch: `main`
   - [ ] Name: `gia-hajj-api`
   - [ ] Environment: `Python`
   - [ ] Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - [ ] Start Command: `gunicorn igaa_project.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 120`
   - [ ] Python Version: `3.11.6`

2. **Configure Environment Variables**
   - [ ] Set all required variables (see above)

3. **Deploy**
   - [ ] Click "Create Web Service"
   - [ ] Monitor logs for build success

## Post-Deployment

- [ ] Service is running (check status on Render dashboard)
- [ ] Test API endpoint: `https://gia-hajj-api.onrender.com/`
- [ ] Check admin panel: `https://gia-hajj-api.onrender.com/admin/`
- [ ] Create superuser:
  ```bash
  render run python manage.py createsuperuser
  ```
- [ ] Update frontend CORS_ALLOWED_ORIGINS if needed
- [ ] Test API calls from frontend
- [ ] Verify static files load correctly

## Common Issues & Fixes

### Issue: 502 Bad Gateway
- [ ] Check service logs for errors
- [ ] Verify `DATABASE_URL` is set correctly
- [ ] Ensure migrations ran successfully

### Issue: Static files returning 404
- [ ] Run: `python manage.py collectstatic --noinput`
- [ ] Check WhiteNoise is in MIDDLEWARE
- [ ] Verify `STATIC_ROOT` directory exists

### Issue: CORS errors from frontend
- [ ] Check `CORS_ALLOWED_ORIGINS` environment variable
- [ ] Ensure frontend URL is included (with `https://`)
- [ ] Restart service after changing CORS

### Issue: Migrations failing
- [ ] Check PostgreSQL is running and accessible
- [ ] View specific migration status: `python manage.py showmigrations`
- [ ] Run migrations manually: `render run python manage.py migrate`

## Monitoring & Maintenance

- [ ] Set up alerts for service down (Render dashboard)
- [ ] Monitor logs regularly for errors
- [ ] Check database size/usage
- [ ] Review slow query logs if available
- [ ] Update dependencies monthly
- [ ] Back up database regularly

## Important Notes

- Render free tier has limited resources; upgrade if needed
- Auto-deploy from GitHub: changes push → auto rebuild
- Static files served by WhiteNoise (no extra CDN needed)
- Database backups should be configured
- Consider adding error tracking (Sentry, etc.)

## Support & Documentation

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- WhiteNoise: http://whitenoise.evans.io/
- This project: RENDER_DEPLOYMENT.md
