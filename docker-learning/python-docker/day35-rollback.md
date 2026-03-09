## Day 35 — Rollback Drill: GHCR + Docker Compose PROD

### Goal
Practice a real incident workflow:  
- Deploy from registry (GHCR) using immutable tags  
- Detect breakage (HTTP 500)  
- Roll back fast to last known-good image  
- Confirm recovery with evidence

---

### Setup

- App image is published to GHCR as:  
    - `ghcr.io/sunil-9647/devops-py-api:sha-<shortsha>`  
    - ghcr.io/sunil-9647/devops-py-api:latest  
- PROD deployment is controlled by `compose.prod.yaml` using `image:` (not `build:`)

#### Why DB `ports: []` in PROD
- DB should not be exposed to host in production  
- Only the API service should access DB over Docker internal network  
- Reduced attack surface

#### Incident Simulation
1. PROD was updated to a newer image tag (`sha-777a7b7`)  
2. Symptom:  
    - `curl -i http://localhost:8080/` returned `HTTP 500`  
3. DB status:  
    - `curl http://localhost:8080/db-check` returned OK (`select=1`)  
4. Conclusion:  
    - App regression on `/` endpoint (customer-facing failure), DB fine

---

### Rollback Action
1. Change `compose.prod.yaml`:  
    - from `sha-777a7b7` → to stable `sha-87378c3`  

2. Apply:  
    - `docker compose -f compose.yaml -f compose.prod.yaml pull`  
    - `docker compose -f compose.yaml -f compose.prod.yaml up -d`

3. Evidence:  
    - `/` returned `HTTP 200 OK`  
    - API container shows image `sha-87378c3`  
    - Services healthy  

#### Why immutable tags are critical
- `latest` is a moving pointer and not safe for rollback under pressure  
- `sha-xxxxxxx` is deterministic and maps to exact code revision  
- Rollback becomes “change one line” instead of rebuilding/debugging

#### Post-Incident: Prevention
- Publishing workflow must not push broken images to GHCR  
- Add pipeline gate:  
    - build locally  
    - run smoke test (`curl -f /`)  
    - only then push to GHCR

**Important:**
1. **latest danger** — right, but remember the key phrase: **moving pointer**.  
2. **incident order** — correct: **restore first**, then fix.  
3. **source of truth** — correct: `compose.prod.yaml` for “what is running”.

---
