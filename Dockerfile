# Use official Superset image - already has psycopg2 and all dependencies pre-installed
# This avoids all the build issues we've been having
FROM apache/superset:latest

# Copy our custom config file
COPY docker/pythonpath_dev/superset_config.py /app/pythonpath/superset_config.py

# The official image already has:
# - psycopg2-binary installed
# - All Python dependencies
# - docker-bootstrap.sh entrypoint
# - Proper USER superset setup
# - Everything else needed

# Keep the default CMD from official image (already set to docker-bootstrap.sh)
