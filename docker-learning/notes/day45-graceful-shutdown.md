## Day 45 — Graceful Shutdown and In-Flight Requests

### Goal of Day-45
The goal of this day was to understand how containers stop, what graceful shutdown really means, and why it matters for reliability and user experience.

We tested what happens when a running request is in progress while the container is being stopped.

---

### 1) Why graceful shutdown matters
A container stopping is not automatically a problem.  
What matters is **how** it stops.

If a process is stopped abruptly:  
- requests can get cut off  
- users can get incomplete responses  
- database connections may close badly  
- cleanup may not happen correctly  

A graceful shutdown gives the application time to:  
- finish in-flight work  
- close resources  
- exit in an orderly way

This improves both reliability and user experience.

---

### 2) What Docker does during `docker stop`
When we run:  
```bash
docker stop <container>
```

Docker does not immediately kill the container.

It does this in order:  
1. sends `SIGTERM`  
2. waits for a grace period  
3. if the process still does not exit, sends `SIGKILL`

This means the application has a chance to shut down cleanly before Docker force-stops it.

---

### 3) What the application must do

Docker only sends the signal.  
The application is responsible for reacting properly.

In our FastAPI/Uvicorn container, graceful shutdown behavior included:  
- receiving the termination signal  
- stopping in an orderly way  
- completing shutdown before the process exits

This is application-level behavior, not Docker magic.

---

### 4) What we observed in logs during shutdown

When we stopped the container, logs showed:  
```bash
INFO: Shutting down
INFO: Waiting for application shutdown.
INFO: Application shutdown complete.
INFO: Finished server process [1]
```
This is the expected graceful shutdown sequence.

It proved:  
- the app received the stop signal  
- it began shutdown properly  
- it exited in an orderly way

---

### 5) Testing graceful shutdown with a slow endpoint

To make the shutdown test realistic, we added a temporary endpoint:  
```python
@app.get("/slow")
def slow():
    time.sleep(8)
    return {"ok": True, "message": "slow response complete"}
```

This endpoint intentionally delayed the response so we could test what happens if the container is stopped while a request is still running.

---

### 6) What happened during the real test

We did this sequence:  

1. started a slow request:  
```bash
curl -i http://localhost:8080/slow
```

2. while the request was still processing, we stopped the container:  
```bash
docker stop api-day45
```

**Result**

The request still completed successfully:  
```bash
HTTP/1.1 200 OK
{"ok":true,"message":"slow response complete"}
```

Then the shutdown logs appeared.

This proved an important production behavior:  
> Uvicorn allowed the in-flight request to complete before finishing shutdown.

---

### 7) Why this is important

This is exactly why graceful shutdown matters.

Without graceful shutdown:  
- the slow request could have been cut off  
- the client might receive an error or broken connection  
- user experience would suffer

With graceful shutdown:  
- the active request finished  
- shutdown happened only afterward  
- the system behaved predictably

---

### 8) Observability detail we learned

In logs, we noticed different client IP patterns:  
- `127.0.0.1` → usually internal healthcheck traffic  
- `172.x.x.x` → request coming through Docker networking / host path

This helps distinguish:  
- internal probe traffic  
- real request traffic

This is useful when reading logs in containerized systems.

---

### 9) Cleanup decision after the experiment

After the Day-45 test:  

**Keep**

- `/ready` endpoint
    Because it is a useful readiness-style endpoint.

**Remove**

- `/slow` endpoint
    Because it was only for the shutdown experiment.

**Remove test container**

- `api-day45` should be deleted  
- it was only a temporary learning container, not part of the real stack

This keeps the project clean and avoids operational confusion later.

---

### 10) Main takeaways

1. Docker sends `SIGTERM` first, not immediate kill.  
2. Applications must handle shutdown properly.  
3. Graceful shutdown protects in-flight requests.  
4. Clean shutdown behavior can be verified from logs.  
5. Temporary test containers and artificial endpoints should be cleaned up after experiments.

---

### Commands used

**Watch logs**  
```bash
docker logs -f api-day45
```

**Stop container**  
```bash
docker stop api-day45
```

**Test slow endpoint**  
```bash
curl -i http://localhost:8080/slow
```

**Cleanup test container**  
```bash
docker rm -f api-day45
```

---

### Final takeaway

Graceful shutdown is important because it allows the application to finish active work and close cleanly before exiting. This prevents interrupted user requests and makes container behavior safer and more predictable in real systems.
