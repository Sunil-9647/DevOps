## Day 34 Notes 06 — Deploy from Registry (GHCR) using Docker Compose

### 0) Goal of Day-34 (what we achieved)
Today we moved from “building images locally” to a real production habit:  
> Build & publish image in CI → store in registry (GHCR) → deploy by pulling that exact image tag using Docker Compose.

This is a core DevOps pattern:  
- CI builds once  
- CD/deploy pulls and runs the same artifact  
- rollback becomes changing the tag back (no rebuild, no guessing)

---

### 1) What “Deploy from Registry” means (real meaning)

#### Wrong approach
- Go to server  
- Run `docker build` on server  
- Run container

This is not production-grade because:  
- Server builds can differ (cache, base image updates, missing dependencies)  
- No clean audit trail (“which exact image is running?”)  
- Rollback is messy  

#### Correct approach
- CI builds the image in a controlled environment  
- CI tags it with an immutable identifier (commit SHA)  
- CI pushes it to a registry (GHCR)  
- Server/Compose **pulls** and runs that exact tag  

So production servers become **runtime only**, not build machines.

---

### 2) Registry used: GHCR (GitHub Container Registry)
We published our FastAPI production image to GHCR:

**Image format:**  
`ghcr.io/<owner>/<image-name>:<tag>`

Our chosen naming for this lab:  
- `ghcr.io/sunil-9647/devops-py-api:<tag>`

**Important rule:** GHCR image names should be lowercase to avoid headaches.

#### Tag strategy (what we used)
We used two tags:  
- `sha-<shortsha>`  → safest, traceable (production tag)  
- `latest`          → convenience pointer (not ideal for real production)

Example tag seen in our deployment:  
- `ghcr.io/sunil-9647/devops-py-api:sha-87378c3`

---

### 3) Why SHA tags are better than `latest` (non-negotiable)

#### `latest` is dangerous because:
- it changes over time  
- rollback is unclear under pressure  
- “latest” does not tell you which code is running  

#### `sha-87378c3` (or any sha tag) is better because:
- ties directly to a Git commit  
- deterministic: same tag always points to the same built image  
- rollback is as simple as: “use older sha tag”  

---

### 4) Two different workflows ran — why that happened

We saw multiple workflow runs because different workflows have different purposes:  
- **CI workflow** runs tests/build checks  
- **Publish workflow** builds and pushes the image to GHCR  

This is normal. To reduce noise and cost, we applied discipline:  
- build/test on PR  
- publish on push to main  

This prevents duplicate builds.

---

### 5) GHCR “Versions” showing extra untagged items (what it means)
In GHCR package versions, we saw:  
- tagged versions (`latest`, `sha-...`)  
- untagged `sha256:...` entries  

This is normal for modern build pipelines:  
- tags are pointers  
- digests/manifests/attestations may appear as separate entries (sometimes “unknown/unknown”)  

Key point:  
- We deploy using the **tag we control**, not by clicking random digests.

---

### 6) Docker Compose design for production deployment
We already had a Compose setup with:  
- `compose.yaml` (base)  
- `compose.dev.yaml` (dev overrides)  
- `compose.prod.yaml` (prod overrides)  

#### Production principle
In PROD, Compose should use **image pulled from registry**, not `build`.

So we updated **only** `compose.prod.yaml` to run the API from GHCR:  
```yaml
services:
  api:
    image: ghcr.io/sunil-9647/devops-py-api:sha-87378c3
    pull_policy: always
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    restart: unless-stopped

  db:
    restart: unless-stopped
    ports: []
```

#### Why we did NOT remove `command` and `restart`
- `command`: makes runtime behavior explicit (exact process we want in prod)  
- `restart`: unless-stopped: basic resilience (crash/reboot recovery)

These are normal production settings.

---

### 7) Why `db` should not be exposed in production
We used:  
```yaml
db:
  ports: []
```

Meaning:  
- Postgres runs internally (Compose network)  
- Not published to the host network

This reduces attack surface:  
- only the app talks to DB internally  
- outsiders cannot hit port 5432 on the machine  

In prod you expose only what is required (API), not DB.

---

### 8) Actual deployment commands we executed (the real “deploy”)
From lab folder:  
```bash
cd ~/DevOps/linux-learning/docker-learning/labs/python-fastapi-dockerfile

docker compose -f compose.yaml -f compose.prod.yaml down
docker compose -f compose.yaml -f compose.prod.yaml pull
docker compose -f compose.yaml -f compose.prod.yaml up -d

curl -sS http://localhost:8080/db-check ; echo
docker compose -f compose.yaml -f compose.prod.yaml ps
```

**What we verified**  

- `/db-check` returned:  
   `{"ok":true,"db":"postgres","select":1}`  
- `docker compose ps` showed API image as:  
   `ghcr.io/sunil-9647/devops-py-api:sha-87378c3`  
- DB showed only `5432/tcp` (internal only), not `0.0.0.0:5432->5432`

This is real deployment proof, not theory.

---

### 9) GHCR authentication (common real issue)
If the image is private, `docker pull` may fail.  

Two correct ways:  
1. Make the package public (simple for learning)  
2. Login to GHCR from the machine:  
```bash
docker login ghcr.io
```
For PAT-based login, token must have:  
- `read:packages` (pull)  
- `write:packages` (push, only needed in CI)

**Important**:  
Never paste tokens into chat or commit them.

---

### 10) Rollback mindset (this is why registry deploy is powerful)
Rollback becomes **changing one line**:  
From:  
`sha-87378c3`

To:  
`sha-<older>`

Then:  
```bash
docker compose -f compose.yaml -f compose.prod.yaml pull
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

No rebuild. No panic. No “works on my machine”.

---

### 11) What files changed today (implementation summary)
- `.github/workflows/publish-py-api-ghcr.yml` (build & push to GHCR)  
- `.github/workflows/docker-image-ci.yml` (moved to PR-only to avoid duplicate builds)  
- `.github/workflows/ci.yml` (restricted using paths correctly)  
- `docker-learning/labs/python-fastapi-dockerfile/compose.prod.yaml` (use GHCR image)  
- (GHCR package created) `devops-py-api` with tags `latest` and `sha-...`  

---

### 12) Common mistakes and how to debug

#### Mistake A: “DB port still exposed in prod”
Fix:  
- ensure DB port mapping exists only in dev override  
- in prod override: `ports: []`

#### Mistake B: “Compose still builds locally”
Fix:  
- prod override must specify `image: ghcr.io/...`  
- run `docker compose ... pull` to force registry fetch

#### Mistake C: “Pull permission denied”
Fix:  
- login to GHCR OR make package public  
- confirm repo Settings → Actions permissions are correct (for pushing from CI)

#### Mistake D: “Workflow runs too many times”
Fix:  
- apply `paths:` and event discipline:  
   - PR → build/test  
   - main → publish  

---
