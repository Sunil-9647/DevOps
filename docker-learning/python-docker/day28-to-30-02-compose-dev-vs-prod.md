## Day 28 to 30 — Docker Compose Notes 02 — FastAPI + Postgres (Dev vs Prod)

### What we built (high-level)
We containerized a simple FastAPI service and connected it to PostgreSQL using Docker Compose.  
The API exposes:  
- `/` → returns a JSON message  
- `/db-check` → connects to Postgres using `DATABASE_URL`, runs `SELECT 1`, and returns `{ "ok": true, ... }` if DB is reachable

This lab is important because real-world systems are not “one container”.  
You always have at least:  
- API/service container  
- DB container  
- network connectivity between services  
- persistence for DB  
- configuration (env vars/secrets)  
- health checks and startup ordering  

---

### Why Docker Compose (why not `docker run` only?)
Using `docker run` is okay for one container, but breaks down fast for multi-service apps.  

Compose gives us:  
1. **Repeatability**: anyone can bring up the whole stack using one command.  
2. **Service discovery**: Compose provides internal DNS so `api` can reach `db` by service name.  
3. **Clean configuration**: ports, env vars, volumes, healthchecks are defined in one place.  
4. **Correct startup order**: API should wait until DB is actually ready.  

---

### Core mental model: Dockerfile → Image Layers → Cache
Docker builds images in layers. Each Dockerfile instruction produces (or reuses) a layer.  
Caching is based on checksums of inputs.

#### What we proved in practice (this is not theory)
- If only `main.py` changes:  
  - dependency install layer (`pip install`) stays cached  
  - rebuild is fast  
- If `requirements*.txt` changes:  
  - cache breaks at `COPY requirements...`  
  - `pip install` runs again  
  - rebuild is slow (this is expected and correct)  

**Reason:** The `pip install` step depends on the previous layer that contains the requirements file.  
When the requirements file changes, Docker must re-run that step.

---

### Dependency design: PROD vs DEV
We created two dependency profiles:  

#### PROD (`requirements-prod.txt`)
- Uses lean dependencies (example: `uvicorn==...`)  
- Goal: smaller image, fewer packages, fewer vulnerabilities, less operational risk

#### DEV (`requirements-dev.txt`)
- Uses developer convenience extras (example: `uvicorn[standard]==...`)  
- Goal: better dev experience (reload watchers, websockets support, etc.)

We select the profile using Docker build-arg:  
- `TARGET=prod` → install `requirements-prod.txt`  
- `TARGET=dev`  → install `requirements-dev.txt`

#### Evidence from our builds (real numbers from our machine)
- `py-api:prod` ≈ 199MB  
- `py-api:dev`  ≈ 231MB  

The dev image is bigger because `uvicorn[standard]` pulls extra packages such as:  
- `uvloop`, `httptools` (performance)  
- `watchfiles` (dev reload)  
- `websockets`  
- `python-dotenv`, `pyyaml`  
More packages = more size + more patching surface.

---

### Why we pin dependency versions (reproducible builds)
We pinned versions for FastAPI, Uvicorn, and psycopg.

Example:  
- `psycopg[binary]==3.3.3`

#### Why pinning matters in CI/CD
If we don’t pin, `pip` can install a newer version later even if our code didn’t change.  
This causes:  
- “same code, different build output”  
- random CI failures over time  
- hard debugging because environment silently changed  
- rollback/rebuild uncertainty

Pinning gives predictability:  
- same Docker build tomorrow  
- same dependencies in DEV/STAGING/PROD  
- easier rollback and incident handling

---

### Compose architecture (what is connected to what)

#### Services
- `db`: PostgreSQL 16 (alpine)  
- `api`: FastAPI container built from our Dockerfile

#### Networking (service discovery)
Compose creates an internal network.  
Inside that network:  
- API reaches DB using hostname `db` (service name), not an IP  
- DB listens on `5432` inside the network

That is why the connection string is like:  
`postgresql://user:pass@db:5432/dbname`

---

### Persistence: why we used a named volume for Postgres
DB data must survive container recreation.  
Containers are disposable by design.

We used:  
- named volume `pgdata:/var/lib/postgresql/data`  

So even if the DB container is deleted/recreated, the DB data remains.

---

### Health checks and startup ordering (production-grade concept)

#### DB healthcheck
We used `pg_isready` to confirm DB is actually ready (not just “container is running”).

#### API healthcheck
We used an HTTP check inside the container to confirm the API responds.

#### `depends_on` with `service_healthy`
API should start only after DB becomes healthy.  
This avoids early failures like:  
- API booting before DB is ready → connection errors → noisy logs/retries  

---

### DEV vs PROD Compose separation
We used 3 files:

#### 1) `compose.yaml` (base / common)
Contains only the shared configuration:  
- services definitions  
- healthchecks  
- volumes  
- env variables  
- API port mapping (8080 → 8000)  

Base should be safe for production defaults.

#### 2) `compose.dev.yaml` (dev overrides)
Dev-only behavior:  
- enable `--reload`  
- bind mount `main.py` for live changes  
- expose DB port `5432` to host so local tools can connect  

#### 3) `compose.prod.yaml` (prod overrides)
Prod-only behavior:  
- no reload  
- no bind mounts  
- restart policy enabled  
- DB port must NOT be published to host (DB stays private)  

#### Why DB ports must not be published in production
We keep DB private so only the application can reach it on the internal network.  
Publishing `5432:5432` in PROD increases attack surface and is an unnecessary risk.  

---

### `.env` and `.env.example`
We used:  
- `.env` → local-only values, never commit  
- `.env.example` → committed template showing required variables  
- `.gitignore` includes `.env`  

This builds the habit:  
- configuration exists outside code  
- secrets are not committed  

---

### Debugging / Troubleshooting
Common checks:

#### See running services
- `docker compose ps`

#### See logs
- `docker compose logs -f api`  
- `docker compose logs -f db`  

#### Inspect final merged config (very useful)
- `docker compose -f compose.yaml -f compose.prod.yaml config`  

#### Exec into container
- `docker compose exec api sh`  
- `docker compose exec db sh`  

#### Validate DB connectivity via API
- `curl -i http://localhost:8080/db-check`

If `/db-check` fails, typical causes:  
- wrong `DATABASE_URL`  
- DB not healthy yet (startup ordering)  
- DB credentials mismatch  
- ports/network misconfiguration  

---

### Commands we used (quick reference)

#### DEV stack
`docker compose -f compose.yaml -f compose.dev.yaml up -d --build`

#### PROD-style stack
`docker compose -f compose.yaml -f compose.prod.yaml up -d --build`

#### Shut down
`docker compose down`

#### Verify DB check
`curl -sS http://localhost:8080/db-check ; echo`

#### Inspect merged compose config (debugging)
`docker compose -f compose.yaml -f compose.prod.yaml config`

---
