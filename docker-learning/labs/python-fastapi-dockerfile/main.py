import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Hello v2 from container"}

@app.get("/db-check")
def db_check():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return {"ok": False, "error": "DATABASE_URL not set"}

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
