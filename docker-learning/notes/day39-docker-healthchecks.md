## Day 39 — Docker Healthchecks and Dependency Control

### Goal
Understand the difference between a container being "running" and a service being "ready", and how Docker healthchecks help manage reliable service startup.

---

### 1) Container state vs service readiness
When Docker shows `Up`:  
it only means the container process (PID 1) started successfully.

This does NOT guarantee that:  
+ the application finished booting  
+ the service is ready  
+ the service accepts connections

Example:  
A database container may be running but still initializing its internal state.

---

### 2) What a healthcheck does
A healthcheck is a command that Docker runs periodically inside the container to verify that the service is actually working.

Example healthchecks:  
API:  
```bash
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')"
```

Database:  
```bash
pg_isready -U app -d appdb
```

If the command succeeds repeatedly, Docker marks the container as:  
`healthy`

If it fails repeatedly, the container becomes:  
`unhealthy`

---

### 3) Healthcheck parameters
Typical healthcheck configuration includes:  

interval  
timeout  
retries  
start_period

Example behavior:  
+ interval: how often the check runs  
+ timeout: maximum time allowed for the check  
+ retries: failures allowed before marking unhealthy  
+ start_period: grace period during startup

These parameters help avoid false failures during startup.

---

### 4) Why startup ordering matters
In multi-service systems like API + database:

1. DB container starts  
2. API container starts immediately  
3. API attempts DB connection  
4. DB still initializing  
5. API fails  

This happens because **container start ≠ service readiness**.

---

### 5) Basic dependency control
Compose supports dependency ordering:  
```bash
depends_on:
db
```

This only guarantees that the DB container starts before the API container.  
It does NOT guarantee that the DB is ready for connections.

---

### 6) Strong dependency control
A better approach uses service health:  
```bash
depends_on:
db:
condition: service_healthy
```

This means:  
Compose will start the API container **only after the DB healthcheck reports healthy**.

This prevents most startup race conditions.

---

### 7) Inspecting healthchecks
Health configuration can be inspected using:  
```bash
docker inspect <container> --format '{{json .Config.Healthcheck}}'`
```

Health status history:  
```bash
docker inspect <container> --format '{{json .State.Health}}'
```

This shows:  
+ health status  
+ failure streak  
+ timestamps  
+ command output  

These logs are useful during troubleshooting.

---

### 8) Practical takeaway

+ A container being "Up" does not guarantee the service is ready.  
+ Healthchecks verify that the application is responding correctly.  
+ Dependency conditions based on health improve reliability during startup.  
+ Healthcheck logs help diagnose service readiness issues.  

---
