# Using Neon PostgreSQL Database with Render

This guide explains how to use your Neon database with the Django application deployed on Render.

## What is Neon?

[Neon](https://neon.tech) is a serverless PostgreSQL platform that offers:
- Generous free tier (3 projects, 10 GB storage)
- Auto-scaling and auto-suspend for cost efficiency
- Branching for development/staging
- Built-in backups
- Low latency across regions

## Your Neon Setup

**Database URL:**
```
postgresql://neondb_owner:npg_UZ1TYhP5Gnqp@ep-dawn-butterfly-a55qwb1z-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Components:**
- **User:** `neondb_owner`
- **Host:** `ep-dawn-butterfly-a55qwb1z-pooler.us-east-2.aws.neon.tech` (us-east-2 region)
- **Database:** `neondb`
- **Security:** SSL required + channel binding

## Local Development

### 1. Set DATABASE_URL in .env

```bash
# .env
DATABASE_URL=postgresql://neondb_owner:npg_UZ1TYhP5Gnqp@ep-dawn-butterfly-a55qwb1z-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 2. Run Migrations Locally

```bash
python manage.py migrate
```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

### 4. Start Development Server

```bash
python manage.py runserver
```

**Note:** Make sure `DEBUG=True` in your .env for local development.

## Deployment on Render

### Step 1: Add Neon DATABASE_URL to Render Environment

1. Go to Render Dashboard
2. Select your `gia-hajj-api` service
3. Go to **Environment** tab
4. Add new environment variable:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste your full Neon connection string)

### Step 2: Important Settings

Make sure these are set:

| Variable | Value |
|----------|-------|
| `DEBUG` | `False` |
| `DATABASE_URL` | Your Neon connection string |
| `SECRET_KEY` | Generate a strong key |
| `ALLOWED_HOSTS` | `*.onrender.com,gia-hajj-api.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://kanb-seven.vercel.app,https://iga-blush.vercel.app` |

### Step 3: Deploy

Render will automatically:
1. Install dependencies
2. Run migrations against Neon database
3. Collect static files
4. Start gunicorn server

## Verify Connection

### Via Django Shell

```bash
python manage.py shell
```

```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
```

### Via psql CLI

```bash
psql postgresql://neondb_owner:npg_UZ1TYhP5Gnqp@ep-dawn-butterfly-a55qwb1z-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
```

## Managing Neon Database

### Accessing Neon Console

1. Go to https://console.neon.tech
2. Log in to your account
3. Select your project
4. Manage databases, users, and backups

### Common Tasks

#### Create a new user
```sql
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE neondb TO app_user;
```

#### View database size
```sql
SELECT pg_size_pretty(pg_database_size('neondb'));
```

#### Check active connections
```sql
SELECT usename, count(*) FROM pg_stat_activity GROUP BY usename;
```

## Performance & Cost Optimization

### Connection Pooling
Neon provides connection pooling. Use the pooler endpoint in CONNECTION_STRING.

### Query Optimization
- Use `select_related()` and `prefetch_related()` in Django ORM
- Add database indexes for frequently queried fields
- Monitor slow queries in Neon console

### Monitoring

Track in Neon Console:
- Active connections
- Query latency
- Storage usage
- CPU usage

## Troubleshooting

### Error: "too many connections"
Solution: Neon free tier has connection limits. Use connection pooling:
```
# Already included in your connection string:
?channel_binding=require
```

### Error: "sslmode=require failed"
Ensure your connection string includes:
```
?sslmode=require&channel_binding=require
```

### Slow Queries from Render
- Neon is in `us-east-2`, Render should also be in `us-east-2` for low latency
- Check Neon console for slow queries
- Add indexes to frequently accessed fields

### Connection Timeout
- Check if Neon compute is suspended (free tier auto-suspends)
- Activate via Neon console
- Consider upgrading for dedicated compute

## Backup & Recovery

### Automatic Backups
Neon provides automatic daily backups for 7 days.

### Manual Export
```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore from Backup
```bash
psql $DATABASE_URL < backup.sql
```

## Scaling Your Database

When you outgrow the free tier:

| Plan | Storage | Compute | Cost |
|------|---------|---------|------|
| Free | 3 GB (shared) | Free tier | Free |
| Pro | 10 GB | Shared | $14/month |
| Enterprise | Unlimited | Dedicated | Custom |

Upgrade in Neon console → Project Settings → Billing.

## Security Best Practices

✅ **Already Done:**
- SSL/TLS encryption (`sslmode=require`)
- Password authentication
- Channel binding enabled

✅ **Recommended:**
- Rotate credentials periodically
- Use separate credentials for production
- Enable two-factor auth on Neon account
- Regular backups
- Monitor access logs

## Useful Links

- [Neon Documentation](https://neon.tech/docs/introduction)
- [Django + PostgreSQL Guide](https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql)
- [Connection Pooling in Neon](https://neon.tech/docs/connect/connection-pooling)
- [Neon API Reference](https://api-docs.neon.tech)

## Support

- **Neon Issues:** https://neon.tech/support
- **Django Issues:** https://docs.djangoproject.com
- **This Project:** See RENDER_DEPLOYMENT.md
