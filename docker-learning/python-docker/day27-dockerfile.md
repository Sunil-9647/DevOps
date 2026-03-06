## Day 27 — Dockerfile Notes 01 — Python FastAPI Container (Build → Run → Health)

### 1) What problem Dockerfile solves (real meaning)
A Dockerfile is a recipe to create a Docker **image**.  
That image becomes a consistent runtime package: same OS base, same libraries, same app code, same start command.  
This removes “works on my machine” problems because the runtime is packaged and repeatable.

---

### 2) Image vs Container (short but correct)
- **Image**: Read-only template made of layers. It is not running.  
- **Container**: Running instance of an image. Docker adds a thin **writable layer** on top.  
So: image = blueprint, container = live process.

---

### 3) Build context and why `.dockerignore` is mandatory
When we run:  
`docker build -t py-api:1 .`

The `.` means Docker takes the current folder as the **build context** and sends it to Docker engine.  
If this folder contains junk (`.git`, `venv`, logs), build becomes slower and may leak sensitive files into the image.

That is why `.dockerignore` is important: it prevents unwanted files from entering the build context.

---

### 4) Dockerfile used for Python FastAPI (explained line-by-line)

#### Base image
`FROM python:3.12-slim`  
We choose slim to reduce image size while still having Debian-based compatibility.

#### Container runtime environment settings
`ENV PYTHONDONTWRITEBYTECODE=1`  
Prevents Python from writing `.pyc` files inside container (cleaner).  
`ENV PYTHONUNBUFFERED=1`  
Makes logs print immediately (important for container logs).

#### Working directory
`WORKDIR /app`  
Sets the default folder inside image. It is like doing `cd /app`.

#### Caching strategy (very important)
We do:  
`COPY requirements.txt .`  
then:  
`RUN pip install --no-cache-dir -r requirements.txt`

This is done **before** copying the full code.  
Reason: dependency installation is the slow part. If code changes but requirements don't, Docker cache reuses the dependency layer and rebuild becomes fast.

#### Copy application code
`COPY . .`  
Copies application code into `/app`.

#### Security hygiene (non-root user)
`RUN useradd -m appuser && chown -R appuser:appuser /app`  
`USER appuser`  
Running as non-root reduces risk. Real production teams avoid root unless required.

#### Port documentation
`EXPOSE 8000`  
This is documentation only. It does not publish the port.

#### Runtime start command
`CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`

Important: `--host 0.0.0.0` is mandatory inside containers.  
If the app binds only to `127.0.0.1`, the container port may not be reachable from outside even when we publish the port.

---

### 5) RUN vs CMD (common interview trap)
- `RUN` happens at **build time** → it creates image layers (example: installing dependencies).  
- `CMD` happens at **run time** → starts when container starts (example: starting uvicorn).  

So:  
- RUN changes the image.  
- CMD starts the container process.

---

### 6) Port publishing: host vs container port
We ran:  
`docker run -d --name pyapi -p 8080:8000 py-api:1`

Meaning:  
- Host port **8080** forwards to container port **8000**  
- Host side: `http://localhost:8080`  
- Container side: app listens on `8000`  

So: `8080 (host) → 8000 (container)`.

---

### 7) HEALTHCHECK (production thinking)
We added a Docker HEALTHCHECK to verify the app is responding, not just “container is up”.

Why it matters:  
- A container can show “Up” even if the app inside is broken or stuck.  
- HEALTHCHECK changes status to:  
  - `(healthy)` when checks succeed  
  - `(unhealthy)` when checks fail repeatedly

We verified with:  
`docker ps` showing `Up ... (healthy)`.

---

### 8) Reproducible builds: pin dependency versions
If requirements contain only package names, pip may install newer versions later.  
This can break builds without changing code.

So we pin versions like:  
`fastapi==0.129.0`  
`uvicorn[standard]==0.41.0`

This ensures repeatable builds.

---

### 9) Commands we used (must remember)
Build:  
- `docker build -t py-api:1 .`

Run:  
- `docker run -d --name pyapi -p 8080:8000 py-api:1`

Check:  
- `docker ps`  
- `curl http://localhost:8080/`

Logs:  
- `docker logs pyapi`

Exec:  
- `docker exec -it pyapi sh`

Inspect health:  
- `docker inspect --format='{{.State.Health.Status}}' pyapi`

---
