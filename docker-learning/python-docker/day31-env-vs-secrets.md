## Day 31 — `.env` vs Docker Compose `secrets` (Production Concept) Notes 03

### 0) Why we even discussed this (real DevOps reason)

In real production, the biggest repeated mistakes are:  
1. Developers store passwords inside code, Dockerfile, or `.env` and accidentally push to GitHub.  
2. Containers print environment variables in logs, and secrets leak.  
3. “It works on my laptop” config doesn’t map cleanly to staging/prod.

So Day-31 was focused on how to configure an app safely:  
+ Keep non-sensitive config in .env / environment variables  
+ Keep sensitive config as secrets (file-based injection, not plain env)

We did this with a practical lab: **FastAPI + Postgres using Compose**, with **dev/prod style separation**.

---

### 1) What `.env` is in Docker Compose (and what it is NOT)

**1.1 What `.env` is used for**

In Compose, a `.env` file is commonly used for:  
+ local development convenience  
+ parameterizing compose files (variable substitution like ${POSTGRES_USER})  
+ non-sensitive configs like:
  - app port  
  - database host name (inside compose network)  
  - database name  
  - feature flags (non-secret)  
  - logging level  

**1.2 What `.env` is NOT meant for (important)**

`.env` is not a secure secrets store.  
Even if you don’t commit it:  
+ it lives as plain text on disk  
+ people copy it into tickets/messages  
+ it often gets accidentally committed  
+ environment variables can leak through debugging (env, crash dumps, logs)

**1.3 How we handled `.env` correctly**

We used the pattern:  
+ ✅ Commit: `.env.example` (safe template)  
+ ❌ Do NOT commit: `.env` (real values)  
+ ❌ Do NOT store actual passwords inside `.env` in production

So `.env.example` becomes documentation for the team:
> “These variables exist, this is the format, fill your own values locally.”

---

### 2) What Docker Compose secrets are (production mindset)

**2.1 What secrets do differently**

Compose secrets are **mounted as files inside containers**, typically under:  
`/run/secrets/<secret_name>`

So the secret is:  
+ not printed by default in env  
+ not shown in compose config as plain value  
+ read only when needed by the process  

**2.2 Why file-based secrets are preferred in prod**

In production, env vars are easy to leak:  
+ `docker inspect` can show env  
+ debugging sessions often print env  
+ app exceptions may dump env

File secrets reduce casual leakage, and many production tools follow this pattern (Kubernetes Secrets, Docker Swarm Secrets, Vault agents, etc.)

---

### 3) What we implemented in our FastAPI + Postgres lab (Day-31)

**3.1 Folder structure we used (important for discipline)**

Inside our lab folder:  
`docker-learning/labs/python-fastapi-dockerfile/`

we created/used:  
+ `compose.yaml` (base)  
+ `compose.prod.yaml` (prod overrides)  
+ `.env.example` (committed template)  
+ `secrets/db_password.txt` (NOT committed)

This is the correct separation:  
+ config template is in Git  
+ real secrets are outside Git

**3.2 The secret we created**

We created a file-based secret:  
`secrets/db_password.txt`

Example content (don’t copy this into Git):

```Plain text
app
```

**3.3 How Postgres consumed the secret (proper pattern)**

Instead of:  
+ `POSTGRES_PASSWORD=app` (bad for production)

We used:  
+ `POSTGRES_PASSWORD_FILE=/run/secrets/db_password`  
So Postgres reads the password from a file.

That was done inside compose using:  
+ a `secrets:` definition  
+ a mount to `/run/secrets/db_password`  
+ setting `POSTGRES_PASSWORD_FILE` to that path  
This is clean and production-aligned.

**3.4 How the API consumed the DB credentials (no password env dump)**

We intentionally avoided putting the password directly in `DATABASE_URL` in compose, because that would expose password through env.

Instead, we used two layers:  

1. Provide non-secret DB settings as env:  
    - `POSTGRES_HOST=db`  
    - `POSTGRES_DB=appdb`  
    - `POSTGRES_USER=app`  
    - `POSTGRES_PORT=5432`

2. Provide password as a secret file:  
    - `/run/secrets/db_password`

Then the FastAPI app builds the full DB URL internally at runtime:  
+ reads password from file  
+ assembles the connection string safely  
+ avoids keeping raw password in logs  
This is exactly how production apps are expected to behave.

---

### 4) What we verified

**4.1 Secret is really mounted**

We verified from inside the API container:  
+ `/run/secrets/db_password` exists  
+ content is readable by the running user  
+ it is not shown in normal env dumps

Cross check:  
+ `ls -l /run/secrets`  
+ `cat /run/secrets/db_password`  
+ `env | grep POSTGRES_`

Important observation:  
+ password is in file, not environment

**4.2 API can still talk to DB**

We verified using endpoint:  
+ `curl http://localhost:8080/db-check`

Output showed:

```JSON
{"ok":true,"db":"postgres","select":1}
```
Meaning:  
+ DB connection works  
+ query works  
+ secret + env wiring works

**4.3 DB is not exposed in PROD**

In prod override we kept DB internal only, by making sure it does not publish host port 5432.

So even if someone is on the host machine:  
+ they cannot connect to Postgres via localhost:5432 in “prod mode”  
+ only the API container can reach DB on the internal compose network

This reduces attack surface.

---

### 5) Mistakes we faced on Day-31 (and what they taught)

**5.1 “Invalid interpolation format… You may need to escape any $ with another $”**

This happened because Docker Compose does variable interpolation with `$`.

If you write something like `${POSTGRES_USER}` inside certain YAML list formats or healthcheck strings, Compose may try to substitute and can break.

Lesson:  
+ For healthcheck commands, prefer `CMD-SHELL` carefully.  
+ If you need literal `$`, escape it as `$$` in Compose.

**5.2 Secret name spelling issue (`db_passward`)**

Compose is strict. If a service refers to a secret name that doesn’t exist, Compose fails to load project.

Lesson:  
+ keep secret names consistent across:  
    - `secrets:` definition (bottom)  
    - `services.<service>.secrets:` reference

**5.3 “DATABASE_URL not set” confusion**

We got this because:  
+ our app expected `DATABASE_URL`  
+ but our prod setup moved toward `POSTGRES_* + secret file`

Then we fixed it by building DB URL inside the app using:  
+ `POSTGRES_*` env  
+ password from `/run/secrets/db_password`

Lesson:  
+ In production, better to pass **components** and assemble sensitive strings inside app, rather than passing a full secret URL in env.

---

### 6) Final production rule from Day-31 (need to remember)

✅ Use `.env` for:  
+ local convenience  
+ non-sensitive configuration  
+ variable substitution in compose  
+ `.env.example` should be committed

✅ Use Compose secrets for:  
+ DB passwords  
+ API keys  
+ tokens  
+ anything that would be damaging if leaked

✅ Production principle:  
+ App should be deployable without changing image  
+ Config + secrets injected at runtime  
+ DB should not be exposed publicly  
+ Verify with actual commands (`curl`, `docker exec`, `healthcheck`), not assumptions

---

### 7) Commands we used often

From lab folder:

#### See the final combined config after overrides
`docker compose -f compose.yaml -f compose.prod.yaml config`

#### Start prod stack
`docker compose -f compose.yaml -f compose.prod.yaml up -d`

#### Check running containers
`docker compose -f compose.yaml -f compose.prod.yaml ps`

#### Verify API and DB
`curl -sS http://localhost:8080/db-check ; echo`

#### Inspect secrets inside container
`docker compose -f compose.yaml -f compose.prod.yaml exec api sh -c 'ls -l /run/secrets && cat /run/secrets/db_password'`

