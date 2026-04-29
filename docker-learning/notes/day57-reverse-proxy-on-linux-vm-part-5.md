## Day 57 — Reverse Proxy and App Exposure Patterns on a Linux VM (Part 5)

### Objective of Day-57 Part 5

Today I learned one complete end-to-end release story for a Dockerized application running behind a reverse proxy on a Linux VM. The purpose of this part was to connect all the earlier proxy-related ideas into one realistic operator flow.

Until now in Day-57, I learned:  
- why the reverse proxy is usually the only public service  
- why the app and database should usually stay internal  
- how request flow moves from client to proxy to app to dependency  
- why release verification must include the real public proxy path  
- how proxy-aware troubleshooting should follow the traffic path layer by layer  
- why user-facing success is more important than simply seeing containers alive

In this part, I connected those ideas into one full operational story:  
- what the stack looks like before release  
- what exactly changes during release  
- how the public path depends on the backend app  
- what the operator verifies after release  
- what a successful release looks like  
- what a failed release looks like  
- how rollback is decided and verified when the public proxy-facing route is broken

This is important because reverse-proxy-based deployments are very common in real-world single-host Docker environments. If I do not understand the full release story from the user-facing route inward, I will debug the wrong thing and make poor rollback decisions.

---

### 1) Example stack used in this release story

The example deployment stack contains three services:  
- `proxy`  
- `api`  
- `db`

This is a common single-host application pattern.

#### Exposure model

The stronger exposure model is:  
- `proxy` is public  
- `api` is internal  
- `db` is internal

That means:  
- users should enter through the reverse proxy  
- the application should usually not be directly exposed to the outside  
- the database should definitely remain internal in a normal setup

#### Public entry point

In this example, users reach the system through:  
```
http://localhost:8080
```

That public entry point maps to the reverse proxy container, which then forwards internally to the backend application.

#### Why this matters

This means the real user path is not:  
- user → api directly

It is:  
- user → proxy → api → db

That one idea is extremely important, because the success or failure of the release must be judged through that real path.

**Main lesson**

In a stronger Docker deployment on a Linux VM, the reverse proxy is the public gateway, while the backend app and database stay internal behind it.

---

### 2) Example Compose-style mental model

The stack can be mentally pictured like this:  
```YAML
services:
  proxy:
    image: nginx:alpine
    ports:
      - "8080:80"

  api:
    image: ghcr.io/sunil-9647/myapp:${APP_IMAGE_TAG}

  db:
    image: postgres:16
```

#### What this means
- the host exposes port `8080`  
- traffic reaches the proxy container on its internal listening port  
- the proxy forwards internally to the backend application service  
- the application service talks internally to the database if needed

The proxy conceptually forwards to something like:  
```
api:8000
```

This means:  
- backend service name = `api`  
- backend internal port = `8000`

#### Why this matters

Even if the proxy container itself does not change, the public service still depends on:  
- the backend service being reachable  
- the backend service listening correctly  
- the backend service responding properly

**Main lesson**

The reverse proxy is only the gateway. It still depends on a healthy and reachable backend app in order to serve users correctly.

---

### 3) Current state before the release begins

Before the release, the operator already knows the exact current backend image version.

For example:  
```
ghcr.io/sunil-9647/myapp:1.2.0
```

And the `.env` file contains:  
```
APP_IMAGE_TAG=1.2.0
```

The operator also knows the release target:  
```
ghcr.io/sunil-9647/myapp:1.2.1
```

So before any change is applied, the operator has three very important facts ready:  
- current backend image = `1.2.0`  
- target backend image = `1.2.1`  
- rollback target = `1.2.0`

#### Why this matters

A strong release never begins with vague ideas like:  
- “deploy the latest build”  
- “use whatever is newest”  
- “try the new one”

Instead, it begins with exact release identity.

**A strong proxy-based release begins with exact current image, exact target image, and exact rollback target already known.**

---

### 4) What actually changes during this release

This is one of the most important parts of the story.

The controlled server-side release change is simply:  

**Before release**  
```
APP_IMAGE_TAG=1.2.0
```

**After release**  
```
APP_IMAGE_TAG=1.2.1
```

That means the operator is only changing:  
- the backend app image version

#### What does not change

In this example, all of these remain stable:  
- proxy public exposure  
- proxy container image  
- proxy route intent  
- database service definition  
- general network structure  
- broad runtime architecture

#### Why this is strong

Because the release remains focused. The blast radius is smaller. If something breaks, there are fewer possible causes.

If instead the operator changed all of these in one release:  
- proxy mapping  
- app image  
- route config  
- DB settings  
- network structure

then debugging would become much more difficult.

**A stronger release changes only the intended backend image while keeping the exposure model and runtime architecture stable.**

---

### 5) How the release is applied on the VM

After updating `.env`, the operator uses the Compose-based update pattern:  
```bash
docker compose --env-file .env pull api
docker compose --env-file .env up -d api
```

**Meaning of the first command**  
`pull api` fetches the new exact backend image now selected in `.env`.

**Meaning of the second command**  
`up -d api` updates or recreates only the `api` service using the exact configured new image.

#### What remains the same
- proxy container remains in place  
- database remains in place  
- proxy still receives public traffic  
- proxy still tries to forward internally to the backend

#### Why this matters

Even though only the backend app image changed, the public path can still break if the new backend does not behave correctly.

**In a proxy-based deployment, changing the backend image alone can still affect the full public user path.**

---

### 6) What the operator must verify after the release

This is where many operators become weak if they think only about container status.

A weak operator may only check:  
- `api` container is running

**That is not enough.**

A stronger operator must verify the release in layers.

#### Layer 1 — Overall container or service state

The operator first checks whether:  
- proxy is running  
- api is running  
- db is running  
- any service is restarting or exited unexpectedly

Example:  
```bash
docker compose ps
```

##### Why this matters

This gives the first broad runtime signal.

But it is still only the beginning.

A running backend container does not prove that the real public route is working.

**Main lesson**

Container state is useful, but it is only the first layer of verification.


#### Layer 2 — Real public proxy-facing path

The operator now checks the real user-facing path.

For example:  
```bash
curl -I http://localhost:8080
curl http://localhost:8080/health
```

##### Why this matters

This is one of the most important checks, because users do not care whether the internal `api` container is alive. They care whether the application works through the public route.

##### What this reveals

This check can reveal:  
- public route unavailable  
- gateway errors  
- upstream timeout  
- wrong response  
- service unusable from the outside-facing point of view

**Main lesson**

The real public proxy path is one of the strongest proofs of release success or failure.

#### Layer 3 — Proxy logs

Now the operator checks proxy logs:  
```bash
docker compose logs --tail=50 proxy
```

##### What to look for
- bad gateway type messages  
- upstream connection failures  
- timeout messages  
- proxy configuration startup issues  
- backend resolution failures

##### Why this matters

Proxy logs often explain whether:  
- the request reached the proxy  
- the proxy attempted upstream forwarding  
- the forwarding failed before the app could respond properly

**Main lesson**

Proxy logs are often the fastest and most useful evidence source when the public route fails.


#### Layer 4 — App logs

The operator also checks backend app logs:  
```bash
docker compose logs --tail=50 api
```

##### What to look for
- startup failure  
- missing env variables  
- crash traces  
- dependency connection errors  
- runtime exceptions  
- unexpected request-handling failures

##### Why this matters

Sometimes the proxy is doing its job correctly, but the backend app itself is broken.

**Main lesson**

Proxy-aware release verification must still include backend app evidence, not just proxy evidence.


#### Layer 5 — Dependency path

The operator should also confirm:  
- app still reaches DB  
- app still behaves correctly when requests require backend data  
- no dependency-related regression was introduced by the release

##### Why this matters

A release may pass:  
- container state check  
- public proxy check

but still fail during real business behavior because the backend app cannot reach its dependencies correctly.

**Main lesson**

A release is not truly healthy until the backend can still function through its dependency chain.

---

### 7) What a successful release path looks like

Now let us follow the happy path.

Suppose the operator sees:  
- proxy running  
- api running  
- db running  
- public path responds correctly  
- proxy logs are clean  
- app logs are clean  
- dependency path works  
- no user-facing regression appears

Now the release can be considered successful.

#### Example release-history record

A useful record may look like this:  
```
Date: 2026-04-24 10:20
Environment: production
Proxy path checked: http://localhost:8080
Previous image: ghcr.io/sunil-9647/myapp:1.2.0
New image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Verification: passed
Notes: proxy path and backend logs verified
```

#### Why this matters

This record tells the future operator:  
- what changed  
- when it changed  
- what the rollback target is  
- what public path was verified  
- whether verification passed

**Main lesson**

A successful proxy-based release should leave behind exact user-facing release evidence, not just a memory that “it seemed okay.”

---

### 8) Failed release path example 1 — proxy is up, but public route returns 502

This is a very realistic failure pattern.

Suppose after release:  
- proxy container is running  
- api container is running  
- but `curl http://localhost:8080` returns `502`

This is important because a beginner may wrongly assume:  
- both containers are alive  
- therefore release should be mostly fine

That is wrong.

#### What 502 usually suggests

In a proxy-based setup, a 502 usually means:  
- the proxy is alive  
- but the proxy-to-backend path is broken

Possible causes include:  
- backend app not listening on expected port  
- app unhealthy after startup  
- proxy pointing to wrong backend name or port  
- app failing immediately when requests arrive  
- app reachable at container level but broken in serving requests

#### Why this matters

This proves that:  
- proxy liveness is not enough  
- backend liveness is not enough  
- the actual user-facing route is what matters

**A release may need rollback even when both proxy and app containers are running, if the real public route is still failing.**

---

### 9) Failed release path example 2 — public route responds, but backend behavior is bad

Another realistic failure pattern is this:  
- public path responds  
- no obvious gateway error  
- but the app returns 500  
- or the app fails functionally  
- or app logs show DB/auth/config problems

In this case:  
- the proxy is probably fine  
- the routing path is probably fine  
- but backend app behavior is still broken for users

This is important because not every failed release in a proxy-based system is a proxy routing problem.

Sometimes the request reaches the backend successfully, but the backend fails deeper in application logic or dependency access.

**User-facing success requires both correct routing and correct backend behavior.**

---

### 10) Why rollback may be required even when the proxy container was unchanged

This is one of the biggest lessons from this story.

A fresher may think:  
- the proxy container was not changed  
- so if something breaks, it cannot be the release

That is wrong.

Even if the proxy container was unchanged, the release may still have broken the user-facing route because the proxy depends on a healthy backend.

For example:  
- proxy still forwards to `api:8000`  
- but the new backend image no longer responds correctly  
- or the backend image fails under real request load  
- or the backend cannot reach the DB anymore  
- or the backend returns unhealthy responses to the proxy path

So the public service can still become unusable.

**An unchanged proxy can still surface a broken release if the new backend image breaks the proxy-to-backend path or backend behavior.**

---

### 11) How rollback happens in this same story

Suppose the operator decides rollback is safer.

The rollback target is already known:  
```
ghcr.io/sunil-9647/myapp:1.2.0
```

So the operator restores `.env` from:  
```
APP_IMAGE_TAG=1.2.1
```

back to:  
```
APP_IMAGE_TAG=1.2.0
```

Then the same Compose update pattern is applied:  
```bash
docker compose --env-file .env pull api
docker compose --env-file .env up -d api
```

#### Why this is strong

Because rollback is:  
- exact  
- controlled  
- based on the previous known-good backend image  
- using the same deployment mechanism as the release itself

#### What does not change
- proxy remains the same  
- DB remains the same  
- exposure model remains the same

Only the backend app artifact is restored to the previous known-good version.

**A strong rollback in a proxy-based release usually restores the exact previous backend image while keeping the rest of the stack stable.**

---

### 12) What must be verified after rollback

Rollback is not complete just because the old backend image was reapplied.

After rollback, the operator must verify again:  
1. overall state  
2. public proxy-facing path  
3. proxy logs  
4. app logs  
5. dependency connectivity

#### Why this matters

Because rollback is a recovery action, and recovery is only real when the public user-facing route works again.

For example:  
- `curl http://localhost:8080` should work again  
- proxy should no longer show upstream failures  
- app logs should return to normal  
- dependency path should behave correctly

**Rollback is only successful when both the public proxy path and backend behavior are restored.**

---

### 13) What rollback record should be written

After rollback, a short factual rollback record should be written.

For example:  
```
Date: 2026-04-24 10:33
Environment: production
Failed image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback image: ghcr.io/sunil-9647/myapp:1.2.0
Public symptom: 502 through proxy path
Rollback verification: passed
Notes: proxy recovered after backend rollback
```

#### Why this matters

This tells the future team:  
- what failed  
- what users saw  
- what restored service  
- whether the rollback was verified

**Rollback records in proxy-based systems should capture both the failed backend image and the user-facing symptom.**

---

### 14) Biggest lessons from this full operator story

The most important things I learned from this full proxy-based release story are:  
- the real user path is through the reverse proxy, not directly to the backend app  
- a backend app image release can still break the public route even when the proxy container did not change  
- user-facing success must be verified through the real proxy path  
- 502-like failures often indicate proxy-to-backend path problems  
- public route success requires both correct proxy forwarding and healthy backend behavior  
- rollback may be necessary even when some containers still look alive  
- release and rollback should both leave behind short factual records

---

### 15) Final understanding statement for Part 5

Today I learned one full end-to-end operator story for a reverse-proxy-based Docker deployment on a Linux VM. A strong release begins with exact backend image identity, applies a controlled backend update, verifies the real user-facing proxy path along with backend and dependency health, and if needed rolls back to the exact previous backend image and verifies recovery again. This is the practical operational form of reverse-proxy-aware release discipline.

---

