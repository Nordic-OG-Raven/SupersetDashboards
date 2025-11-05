# Supabase PostgreSQL Setup for Superset

## Quick Setup (Web Dashboard - Fastest)

1. **Create Supabase Project:**
   - Go to: https://supabase.com/dashboard
   - Click "New Project"
   - Name: `superset-db` (or any name)
   - Password: **Save this password!**
   - Region: Choose closest to you
   - Wait 2-3 minutes for setup

2. **Get Connection String:**
   - Go to: Settings → Database
   - Find "Connection string" → "URI"
   - Copy the connection string (format: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`)
   - **Important**: Change port from `6543` to `5432` for direct connection

3. **Set in Render:**
   - After deploying to Render, go to your service
   - Settings → Environment Variables
   - Add:
     - `DATABASE_URL` = your Supabase connection string
     - `SQLALCHEMY_DATABASE_URI` = same connection string

## Alternative: Supabase CLI

```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Login
supabase login

# Create project (requires web dashboard first)
# Then link:
supabase link --project-ref [your-project-ref]

# Get connection string
supabase db url
```

## Connection String Format

Supabase provides a connection string like:
```
postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

For Superset, use direct connection (port 5432):
```
postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

Or use the transaction pooler (port 6543) - both work:
```
postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

## After Setup

1. Deploy to Render (free tier web service)
2. Add Supabase connection strings as environment variables
3. Superset will connect to PostgreSQL automatically
4. Test embedding on `jonashaahr.com/novo-nordisk`

