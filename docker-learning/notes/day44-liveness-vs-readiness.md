## Day44 — Healthchecks: Liveness vs Readiness

### Goal of Day-44
Understand why a container can be:  
+ Up  
+ healthy  
+ but still not ready to handle real traffic

And learn how to design better health endpoints.

---

### 1) Problem from Day-43

We observed:  
+ API container was Up and healthy  
+ DB container was Up and healthy  
+ `/` endpoint worked  
+ `/db-check` failed

This showed:  
> A service can appear healthy while a dependency path is broken.

---

### 2) Why the existing healthcheck failed to detect it

Current Docker healthcheck:  
```text
GET /
```

This checks only:  
+ app process is running  
+ server responds

It does NOT check:  
+ database connectivity  
+ dependency readiness

So Docker correctly reported "healthy", but the system was not fully ready.

---

### 3) Types of health checks

#### A) Liveness (shallow)

Purpose:  
+ Is the app alive?

Example:  
`GET /`

Checks:  
+ process is running  
+ app responds

Pros:  
+ fast  
+ stable  
+ low risk of false failures

Cons:  
+ does not detect dependency issues

#### B) Readiness (deep)

Purpose:  
+ Is the app ready to handle real traffic?

Example:  
`GET /ready`

Checks:  
+ app is running  
+ DB is reachable  
+ dependencies are working

Pros:  
+ reflects real system readiness

Cons:  
+ can fail due to temporary dependency issues  
+ may cause noisy or unstable health status

---

###4) Endpoints implemented
`/`

```JSON
{"status":"ok"}
```

+ liveness-style endpoint  
+ confirms app is running

`/ready`

```JSON
{"ok":true,"ready":true}
```

+ checks DB connectivity  
+ confirms app is ready for real traffic

`/db-check`

```JSON
{"ok":true,"db":"postgres","select":1}
```

+ diagnostic endpoint  
+ returns detailed DB check result  
+ useful for debugging, not ideal for healthcheck

---

### 5) Why we did NOT change Docker healthcheck yet

Even though `/ready` is more accurate, we kept Docker healthcheck on `/`.

Reason:  
+ `/ready` depends on DB  
+ temporary DB issues would mark container unhealthy  
+ this can cause unnecessary restarts or instability

So:  
> Docker healthcheck should remain stable and lightweight unless you intentionally want dependency-aware behavior.

---

### 6) Practical strategy

A good pattern is:  
+ `/` → liveness (Docker healthcheck)  
+ `/ready` → readiness (operator / load balancer)  
+ `/db-check` → debugging

---

### 7) Key lessons

#### Lesson 1

"Healthy" does not mean "fully functional".

#### Lesson 2

Healthchecks must match their purpose:  
+ liveness → process check  
+ readiness → dependency check

#### Lesson 3

Deeper checks are more accurate but less stable.

#### Lesson 4

Do not blindly make healthchecks deep. Design them intentionally.

---

### 8) Final takeaway
> A well-designed system separates liveness, readiness, and debugging checks.

This allows:  
+ stable containers  
+ accurate readiness signals  
+ easier debugging during incidents

---
