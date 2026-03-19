import os
from urllib.parse import quote_plus
from fastapi import FastAPI

app = FastAPI()

def get_database_url() -> str:
    # 1) Prefer explicit DATABASE_URL if present
    direct = os.getenv("DATABASE_URL", "").strip()
    if direct:
        return direct

    # 2) Otherwise build from POSTGRES_* variables + password from file
    user = os.getenv("POSTGRES_USER", "").strip()
    db = os.getenv("POSTGRES_DB", "").strip()
    host = os.getenv("POSTGRES_HOST", "db").strip()
    port = os.getenv("POSTGRES_PORT", "5432").strip()

    password = os.getenv("POSTGRES_PASSWORD", "").strip()
    pw_file = os.getenv("POSTGRES_PASSWORD_FILE", "").strip()

    if not password and pw_file:
        try:
            with open(pw_file, "r", encoding="utf-8") as f:
                password = f.read().strip()
        except Exception:
            password = ""

    if not (user and db and host and port and password):
        return ""

    # URL-encode password for safety (special chars)
    return f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{db}"

@app.get("/")
def root():
    return {"status":"ok","message":"Hello v2 from container"}


@app.get("/ready")
def ready():
    db_url = get_database_url()
    if not db_url:
        return {"ok": False, "ready": False, "error": "DATABASE_URL not set"}

    try:
        import psycopg
        with psycopg.connect(db_url, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return {"ok": True, "ready": True}
    except Exception as e:
        return {"ok": False, "ready": False, "error": str(e)}

@app.get("/db-check")
def db_check():
    db_url = get_database_url()
    if not db_url:
        return {"ok": False, "error": "DATABASE_URL not set (and cannot build from POSTGRES_* vars)"}

    try:
        import psycopg
        # short timeout so it doesn't hang forever
        with psycopg.connect(db_url, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                val = cur.fetchone()[0]
        return {"ok": True, "db": "postgres", "select": val}
    except Exception as e:
        return {"ok": False, "error": str(e)}
