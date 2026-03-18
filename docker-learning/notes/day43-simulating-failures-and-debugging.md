## Day43 — Simulating Failures and Debugging Like a Real Incident

### Goal of Day-43
The goal of this day was to simulate a realistic containerized application failure and debug it step by step using the correct incident workflow.

The main idea was:  
+ do not guess  
+ do not jump straight to code changes

Instead, use structured signals to identify:  
+ what is failing  
+ which layer is affected  
+ what the real root cause is

---

### 1) Failure layers in container incidents
A containerized application can fail at different layers:

#### A) Container / process layer
+ container exited  
+ PID 1 crashed  
+ restart loop

#### B) Health layer
+ container is running  
+ but healthcheck fails  
+ service is not actually ready

#### C) Network / dependency layer
+ app cannot resolve or reach another service  
+ wrong hostname  
+ wrong network  
+ dependency unavailable

#### D) Application layer
+ route returns 500  
+ logic is broken  
+ user path fails even though container is alive

This day focused on a **dependency configuration failure**.

---

### 2) Controlled failure we injected
We intentionally broke the API-to-database configuration by changing:  
```yaml
POSTGRES_HOST: db
```

to an invalid hostname:  
```bash
POSTGRES_HOST: dbworng
```

This created a realistic service-discovery/config error.

Important:  
+ we did NOT change code logic  
+ we did NOT stop the DB  
+ we only changed the dependency hostname

This was a clean and controlled failure.

---

### 3) Symptom observed
After applying the wrong configuration, the endpoint:  
```bash
curl -sS http://localhost:8080/db-check ; echo
```

returned:  
```bash
{"ok":false,"error":"failed to resolve host ... Name or service not known"}
```

This immediately suggested:  
+ API route executed  
+ app tried to use DB  
+ hostname resolution failed

So the issue was likely in:  
+ DNS / service discovery  
+ environment configuration

not in:  
+ app process startup  
+ DB process crash  
+ route definition itself

---

### 4) Incident debugging workflow we followed

#### Step 1 — Check container state
```bash
docker compose -f compose.yaml -f compose.prod.yaml ps
```

Result:  
+ API was still `Up (healthy)`  
+ DB was still `Up (healthy)`

This proved:  
+ containers were running  
+ healthchecks were still passing  
+ the incident was not a container/process failure

#### Step 2 — Check real user/dependency path
```bash
curl -sS http://localhost:8080/db-check ; echo
```

Result:  
+ DB-dependent endpoint failed

This showed:  
+ the app was alive  
+ but one dependency path was broken

#### Step 3 — Check API logs
```bash
docker compose -f compose.yaml -f compose.prod.yaml logs --tail=20 api
```

Result:  
+ repeated `GET /` requests returned `200 OK`

This was important because it showed:  
+ API healthcheck path `/` was still fine  
+ app was not generally dead  
+ failure was narrower than “API down”

This is a key real-world lesson:  
> A service can look healthy on one route and still fail on another path.

#### Step 4 — Check DNS/service discovery directly

Inside the API container:  
```bash
docker compose -f compose.yaml -f compose.prod.yaml exec api sh -c 'getent hosts dbworng || echo "hostname not resolvable"'
```

Result:  
`hostname not resolvable`

This was the strongest root-cause signal.

It proved:  
+ Docker DNS had no record for the configured hostname  
+ the issue was not database shutdown  
+ the issue was not application crash  
+ the issue was a wrong dependency hostname

---

### 5) Why the API still showed healthy

This was a very important observability lesson.

The API healthcheck only tested:  
`GET /`

So Docker reported API as healthy because `/` still returned `200`.  
But `/db-check` failed because that path depends on the database.

This means:  
> Healthcheck scope matters.

A shallow healthcheck can say “healthy” while a dependency-based feature is still broken.

This is not incorrect behavior — it simply means the healthcheck is checking only one narrow part of the app.

---

### 6) Root cause
The root cause was:  
+ incorrect value of `POSTGRES_HOST`  
+ Docker DNS inside the container could not resolve that hostname  
+ API could not connect to the database dependency

So the real classification of the incident is:  
> dependency configuration / service-discovery failure

---

### 7) Fix
We corrected the configuration back to:  
```YAML
POSTGRES_HOST: db
```

Then reapplied the Compose stack and verified both:  
```bash
curl -sS http://localhost:8080/db-check ; echo
docker compose -f compose.yaml -f compose.prod.yaml exec api sh -c 'getent hosts db || echo "hostname not resolvable"'
```

Results:  
+ `/db-check` returned success  
+ `db` resolved correctly again

This closed the incident cleanly.

---

### 8) Main lessons from Day-43

#### Lesson 1
A service can be:  
+ Up  
+ healthy  
+ still broken on a dependency path

#### Lesson 2
Do not trust a single signal.

Use:  
+ container status  
+ real endpoint test  
+ logs  
+ DNS check  
+ health details

#### Lesson 3
`getent hosts <name>` is a very useful debugging command for service discovery problems inside containers.

#### Lesson 4

A typo in hostname/environment configuration can break the application even when all containers are running fine.

---

### 9) Incident ladder used
The correct order we followed was:  
1. `docker compose ps`  
2. test the failing path (`curl`)  
3. read logs  
4. inspect dependency resolution (getent hosts)  
5. fix configuration  
6. verify recovery

This is the right professional workflow.

---

### 10) Final takeaway

The most important learning from Day-43 is:  
> In container incidents, do not assume “healthy” means every feature is working.

A service can pass its healthcheck and still fail on a dependency-specific route.

The correct debugging approach is to follow signals in order and isolate whether the issue is:  
+ process  
+ health  
+ network  
+ dependency  
+ or application logic

---
