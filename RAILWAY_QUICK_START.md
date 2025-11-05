# Railway Deployment - Quick Start

## Minimal Setup (Only 5 variables needed)

After adding PostgreSQL and Redis services in Railway dashboard:

**Only set these 5 variables manually:**

1. `SECRET_KEY` - Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
2. `DATABASE_DIALECT=postgresql`
3. `FEATURE_FLAGS={"EMBEDDED_SUPERSET": true}`
4. `WTF_CSRF_ENABLED=false`
5. `SUPERSET_ENV=production`

**Railway automatically injects these** (when services are connected):
- `DATABASE_USER=${{Postgres.PGUSER}}`
- `DATABASE_PASSWORD=${{Postgres.PGPASSWORD}}`
- `DATABASE_HOST=${{Postgres.PGHOST}}`
- `DATABASE_PORT=${{Postgres.PGPORT}}`
- `DATABASE_DB=${{Postgres.PGDATABASE}}`
- `REDIS_HOST=${{Redis.REDIS_HOST}}`
- `REDIS_PORT=${{Redis.REDIS_PORT}}`

## Security Notes

- `${{Postgres.*}}` syntax = Railway service reference (NOT a real password)
- Railway securely injects actual credentials at runtime
- Only `SECRET_KEY` is a real secret - generate a unique one!

## Fix Railway "Failed to create code snapshot"

Railway needs code in git. Options:

**Option A: Commit to git**
```bash
cd ~/superset
git add .
git commit -m "Deploy to Railway"
railway up
```

**Option B: Connect GitHub**
1. Push to GitHub repo
2. In Railway dashboard: Settings → Connect GitHub
3. Select your repo

## Deploy

```bash
cd ~/superset
railway up
```

After deployment, get URL:
```bash
railway domain
```

