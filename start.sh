#!/usr/bin/env bash
set -e

python - <<PY
import os, time, sys
import psycopg2
url = os.environ.get("DATABASE_URL")
for i in range(30):
    try:
        if not url:
            raise Exception("DATABASE_URL not set")
        conn = psycopg2.connect(url)
        conn.close()
        print("Database ready")
        sys.exit(0)
    except Exception as e:
        print("Waiting for database...", e)
        time.sleep(1)
print("Database not available")
sys.exit(1)
PY

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000
