## Day 42 — Container Observability Basics (Logs, Health, and Debugging Signals)

### Goal of Day-42
The goal of this day was to understand the first level of observability in containerized applications:

+ how to read logs  
+ how to interpret health status  
+ how to combine multiple signals  
+ how to debug issues in a structured way

This is the foundation before using advanced monitoring tools.

---

### 1) What observability means at this stage
Observability means:  
> Understanding what the container is doing, whether it is working, and where failures are happening.

At Docker/Compose level, the main signals are:  
1. container status (`Up`)  
2. health status (`healthy`)  
3. container logs  
4. service response (curl)  
5. inspect output  

---

### 2) Difference between Up and Healthy

#### Up
+ container process is running  
+ PID 1 is alive  
+ does NOT guarantee app is working

#### Healthy
+ healthcheck is passing  
+ confirms service is responding to defined checks  
+ closer to real readiness

So:  
> Up = process started  
> Healthy = service is working (based on healthcheck)

---

### 3) Logs — the behavior signal

Logs show:  
+ requests handled by the app  
+ startup messages  
+ errors and failures  
+ runtime behavior

Example API logs:  
`GET / HTTP/1.1 200 OK`

This confirms:  
+ request reached app  
+ response was successful

But logs must be interpreted carefully:  
+ many logs may be from healthchecks, not real users  
+ repeated logs do not always mean real traffic

---

### 4) Healthcheck vs Logs

#### Healthcheck
+ gives pass/fail signal  
+ used by Docker  
+ structured and automated

#### Logs
+ give detailed behavior  
+ used by humans for debugging  
+ show what actually happened

Both are required for full understanding.

---

### 5) DB logs vs API logs (important comparison)

#### API logs showed:
+ repeated `200 OK`  
+ successful responses  
+ mostly healthcheck traffic

#### DB logs showed:
+ startup sequence  
+ shutdown/restart events  
+ readiness message:  
     `database system is ready to accept connections`  
+ persistence reuse:  
     `Skipping initialization`

This shows:  
> Observability requires reading logs from multiple services, not just one.

---

### 6) Healthcheck output differences

#### DB healthcheck
`pg_isready`

Output:  
`accepting connections`

+ human-readable  
+ clearly shows DB state

#### API healthcheck
`urllib.request.urlopen(...)`

Output:  
`(empty)`

+ only exit code matters  
+ less useful for humans

---

### 7) Important Docker layering insight (from previous days)
Even if files are deleted later, earlier layers still exist.

This affects:  
+ image size  
+ observability of build results

---

### 8) Correct debugging order (very important)
When something fails, follow this order:  
1. Check container status  
```bash
docker compose ps
```

2. Test actual user path  
```bash
curl http://localhost:8080/
```

3. Check logs  
```bash
docker compose logs api
docker compose logs db
```

4. Check health details  
```bash
docker inspect <container> .State.Health
```

This avoids random guessing.

---

### 9) Day-42 learnings

1. Logs are behavior signals, not the full truth  
2. Healthchecks give structured pass/fail signals  
3. Not all healthchecks are equally human-readable  
4. Multiple services must be observed together  
5. Debugging must follow a fixed order, not guesswork

---

### 10) Final takeaway

A container can be:  
+ Up  
+ Healthy  
+ but still have issues

So always combine:  
+ status  
+ health  
+ logs  
+ real request testing

This is the foundation of real-world container debugging.

---
