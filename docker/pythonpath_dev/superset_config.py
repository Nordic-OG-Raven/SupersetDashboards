# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
import secrets
import sys

# CRITICAL: Force database URI IMMEDIATELY, before ANY Superset imports
# This must be the absolute first thing after imports
_db_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
if _db_uri and "@" in _db_uri and "/" in _db_uri.split("@")[1]:
    # Force it at module level immediately
    SQLALCHEMY_DATABASE_URI = _db_uri.replace("postgres://", "postgresql://", 1)
    print(f"[CRITICAL] SQLALCHEMY_DATABASE_URI FORCED: {_db_uri[:50]}...", file=sys.stderr)
else:
    # Check DATABASE_URL as fallback
    _db_url = os.getenv("DATABASE_URL")
    if _db_url and "@" in _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url.replace("postgres://", "postgresql://", 1)
        print(f"[CRITICAL] Using DATABASE_URL: {_db_url[:50]}...", file=sys.stderr)
    else:
        SQLALCHEMY_DATABASE_URI = None
        print("[CRITICAL] WARNING: No database URI found! SQLALCHEMY_DATABASE_URI and DATABASE_URL both empty!", file=sys.stderr)
        print(f"[DEBUG] SQLALCHEMY_DATABASE_URI env var: {os.getenv('SQLALCHEMY_DATABASE_URI')}", file=sys.stderr)
        print(f"[DEBUG] DATABASE_URL env var: {os.getenv('DATABASE_URL')}", file=sys.stderr)

from celery.schedules import crontab
from flask_caching.backends.filesystemcache import FileSystemCache

logger = logging.getLogger()

# SUPERSET_HOME needed for SQLite fallback
SUPERSET_HOME = os.getenv("SUPERSET_HOME", "/app/superset_home")

# SECRET_KEY MUST be set at the very top, before any other imports that might trigger Superset init
# Railway injects SUPERSET_SECRET_KEY or SECRET_KEY at runtime
_secret_key = os.getenv("SUPERSET_SECRET_KEY") or os.getenv("SECRET_KEY")
if not _secret_key or _secret_key in ("CHANGE_ME_SECRET_KEY_PLEASE", "THISISINSECURE", "CHANGE_ME"):
    _secret_key = secrets.token_urlsafe(42)
# Set SECRET_KEY at module level - this happens BEFORE Superset's default config loads
SECRET_KEY = _secret_key

# Validate that SQLALCHEMY_DATABASE_URI is complete (not just "postgresql://")
# If it's incomplete, build from individual variables instead
if SQLALCHEMY_DATABASE_URI and "@" in SQLALCHEMY_DATABASE_URI and "/" in SQLALCHEMY_DATABASE_URI.split("@")[1]:
    # Valid complete connection string
    logger.info(f"Using SQLALCHEMY_DATABASE_URI from environment: {SQLALCHEMY_DATABASE_URI[:30]}...")
else:
    # Not set or incomplete, build from components
    if SQLALCHEMY_DATABASE_URI:
        logger.warning(f"SQLALCHEMY_DATABASE_URI is incomplete: '{SQLALCHEMY_DATABASE_URI}', building from components instead")
    SQLALCHEMY_DATABASE_URI = None

if not SQLALCHEMY_DATABASE_URI:
    # Railway auto-injects PostgreSQL variables with PG* prefix
    # Also check for DATABASE_* and direct DATABASE_URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        # Use DATABASE_URL if provided (Railway sometimes uses this)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        logger.info(f"Using DATABASE_URL for database connection")
    else:
        # Build from components - Railway uses PG* variables OR DATABASE_* variables
        DATABASE_DIALECT = os.getenv("DATABASE_DIALECT") or "postgresql"
        DATABASE_USER = os.getenv("DATABASE_USER") or os.getenv("PGUSER")
        DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD") or os.getenv("PGPASSWORD")
        DATABASE_HOST = os.getenv("DATABASE_HOST") or os.getenv("PGHOST")
        DATABASE_PORT = os.getenv("DATABASE_PORT") or os.getenv("PGPORT", "5432")
        DATABASE_DB = os.getenv("DATABASE_DB") or os.getenv("PGDATABASE")
        
        # Debug logging
        logger.info(f"Database config: USER={DATABASE_USER[:3] if DATABASE_USER else None}..., HOST={DATABASE_HOST}, DB={DATABASE_DB}, PORT={DATABASE_PORT}")
        
        if DATABASE_USER and DATABASE_PASSWORD and DATABASE_HOST and DATABASE_DB:
            SQLALCHEMY_DATABASE_URI = (
                f"{DATABASE_DIALECT}://"
                f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
                f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
            )
            logger.info(f"Using PostgreSQL: {DATABASE_DIALECT}://{DATABASE_USER}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}")
        else:
            # Fallback to SQLite if no database configured (shouldn't happen in Railway)
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SUPERSET_HOME, "superset.db")
            logger.warning(f"FALLING BACK TO SQLITE! Missing: USER={not DATABASE_USER}, PASS={not DATABASE_PASSWORD}, HOST={not DATABASE_HOST}, DB={not DATABASE_DB}")

EXAMPLES_USER = os.getenv("EXAMPLES_USER")
EXAMPLES_PASSWORD = os.getenv("EXAMPLES_PASSWORD")
EXAMPLES_HOST = os.getenv("EXAMPLES_HOST")
EXAMPLES_PORT = os.getenv("EXAMPLES_PORT")
EXAMPLES_DB = os.getenv("EXAMPLES_DB")

# Use environment variable if set, otherwise construct from components
# This MUST take precedence over any other configuration
SQLALCHEMY_EXAMPLES_URI = os.getenv(
    "SUPERSET__SQLALCHEMY_EXAMPLES_URI",
    (
        f"{DATABASE_DIALECT}://"
        f"{EXAMPLES_USER}:{EXAMPLES_PASSWORD}@"
        f"{EXAMPLES_HOST}:{EXAMPLES_PORT}/{EXAMPLES_DB}"
    ),
)


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

# SECRET_KEY is already set at the top of this file (before any other config)
# This ensures it's available before Superset's validation check

FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "EMBEDDED_SUPERSET": True
}

# Disable CSRF for guest token API (required for embedding)
WTF_CSRF_ENABLED = False

# Allow iframe embedding (disable X-Frame-Options)
# Superset sets X-Frame-Options in initialization, override it
OVERRIDE_HTTP_HEADERS = {
    'X-Frame-Options': 'ALLOWALL'  # This will be ignored/invalid, effectively removing it
}

# Enable CORS for embedded dashboards
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': {'*': {'origins': ['*']}},
    'origins': ['http://localhost:3000', 'http://localhost:3001', 'https://*.vercel.app', 'https://jonashaahr.com']
}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = f"http://superset_app{os.environ.get('SUPERSET_APP_ROOT', '/')}/"  # When using docker compose baseurl should be http://superset_nginx{ENV{BASEPATH}}/  # noqa: E501
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = (
    f"http://localhost:8888/{os.environ.get('SUPERSET_APP_ROOT', '/')}/"
)
SQLLAB_CTAS_NO_LIMIT = True

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)

if os.getenv("CYPRESS_CONFIG") == "true":
    # When running the service as a cypress backend, we need to import the config
    # located @ tests/integration_tests/superset_test_config.py
    base_dir = os.path.dirname(__file__)
    module_folder = os.path.abspath(
        os.path.join(base_dir, "../../tests/integration_tests/")
    )
    sys.path.insert(0, module_folder)
    from superset_test_config import *  # noqa

    sys.path.pop(0)

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa: F403

    logger.info(
        "Loaded your Docker configuration at [%s]", superset_config_docker.__file__
    )
except ImportError:
    logger.info("Using default Docker config...")

# Hook into Flask app to remove X-Frame-Options after initialization
# This runs after the app is created
def configure_embedding(app):
    @app.after_request
    def remove_xframe_options(response):
        response.headers.pop('X-Frame-Options', None)
        return response
    return app

# CRITICAL: Force SQLALCHEMY_DATABASE_URI at the VERY END to override any defaults
# This must be the last thing set in this file
# Render provides DATABASE_URL which we need to convert to SQLALCHEMY_DATABASE_URI
_force_db_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
if _force_db_uri and "@" in _force_db_uri and "/" in _force_db_uri.split("@")[1]:
    SQLALCHEMY_DATABASE_URI = _force_db_uri.replace("postgres://", "postgresql://", 1)
    print(f"[FORCE] SQLALCHEMY_DATABASE_URI set to: {_force_db_uri[:50]}...", file=sys.stderr)
elif not _force_db_uri:
    # Check for Render's DATABASE_URL (highest priority after SQLALCHEMY_DATABASE_URI)
    _render_db_url = os.getenv("DATABASE_URL")
    if _render_db_url and "@" in _render_db_url:
        SQLALCHEMY_DATABASE_URI = _render_db_url.replace("postgres://", "postgresql://", 1)
        print(f"[FORCE] Using DATABASE_URL from Render: {_render_db_url[:50]}...", file=sys.stderr)
    else:
        # Build from components as fallback
        _db_user = os.getenv("DATABASE_USER") or os.getenv("PGUSER")
        _db_pass = os.getenv("DATABASE_PASSWORD") or os.getenv("PGPASSWORD")
        _db_host = os.getenv("DATABASE_HOST") or os.getenv("PGHOST")
        _db_port = os.getenv("DATABASE_PORT") or os.getenv("PGPORT", "5432")
        _db_name = os.getenv("DATABASE_DB") or os.getenv("PGDATABASE")
        if _db_user and _db_pass and _db_host and _db_name:
            SQLALCHEMY_DATABASE_URI = f"postgresql://{_db_user}:{_db_pass}@{_db_host}:{_db_port}/{_db_name}"
            print(f"[FORCE] SQLALCHEMY_DATABASE_URI built from components: postgresql://{_db_user}@{_db_host}:{_db_port}/{_db_name}", file=sys.stderr)
