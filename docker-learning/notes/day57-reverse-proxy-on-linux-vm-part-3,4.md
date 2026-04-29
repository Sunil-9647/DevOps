## Day 57 — Reverse Proxy and App Exposure Patterns on a Linux VM (Part 3)

### Objective of Day-57 Part 3

Today I learned a simple Nginx-style mental model for reverse proxy routing on a Linux VM. The goal was to understand the basic routing logic without getting lost in syntax. I learned how outside traffic reaches the host port, then the proxy container, and then the backend app service inside the Docker network.

This is important because many proxy issues happen not because Nginx is mysterious, but because names, ports, or network assumptions do not match correctly.

---

### 1. Three important port layers

In a simple proxy-based deployment, three different port layers may exist:  

**Host/public port**  
This is the VM port that the outside world reaches, for example:  
- `8080`

**Proxy container port**  
This is the port the proxy listens on inside its own container, for example:  
- `80`

**Backend app port**  
This is the internal port the app listens on inside its own container, for example:  
- `8000`

A simple model is:  
- client → VM:8080 → proxy:80 → app:8000

**Main lesson**

Host port, proxy port, and app port are different layers and should not be confused.

### 2. Basic Nginx-style routing idea

An Nginx-style reverse proxy usually:  
- listens for incoming requests  
- forwards matching requests to the backend app

A very simple mental model is:  
- listen on port 80  
- forward `/` to `api:8000`

**A reverse proxy listens on one port and forwards traffic to a backend service name and backend internal port.**

---

### 3. What must be correct for proxy routing to work

For routing to work properly:  
- proxy container must be running  
- proxy must be published correctly on the host  
- backend service name must be correct  
- backend port must be correct  
- proxy and app must share the correct Docker network  
- app must actually be healthy and listening

**Proxy routing depends on alignment between host mapping, proxy config, Docker networking, and backend health.**

---

### 4. Common mistakes

Common routing mistakes include:  
- wrong backend service name  
- wrong backend port  
- proxy and app not on same network  
- backend app unhealthy  
- confusing host-public port with backend internal port

**Many proxy failures come from mismatched names, ports, or network assumptions rather than from complex proxy theory.**

---

### 5. Calm troubleshooting order

When the public route breaks, a strong check order is:  
1. can client reach host-public port  
2. is proxy container running  
3. is proxy forwarding to correct backend target  
4. can proxy reach app on Docker network  
5. is app healthy and listening

**Proxy-aware troubleshooting should follow the request path layer by layer.**

---

### 6. Why public gateway errors can be misleading

Errors like:  
- 502  
- bad gateway  
- upstream timeout

do not automatically mean the app code is broken.

They can also mean:  
- wrong backend hostname  
- wrong backend port  
- network issue between proxy and app  
- backend app not reachable

**Public proxy errors often indicate a routing-path problem, not just an app bug.**

---

### 7. Why this matters during release verification

If a release changes:  
- proxy config  
- app port expectations  
- service names  
- Docker networking  
- backend app health

then the public route can break even if some containers still appear healthy.

**Proxy-based release verification must confirm the full request path, not just individual container status.**

---

### 8. Final understanding statement for Part 3

Today I learned a simple and practical reverse proxy routing model for single-host Docker deployments. A reverse proxy route works only when the host mapping, proxy listening port, backend service name, backend port, shared Docker network, and backend app health all match correctly. This helps me troubleshoot proxy-based release failures much more clearly.

---

## Day-57 — Reverse Proxy and App Exposure Patterns on a Linux VM (Part 4)

### Objective of Day-57 Part 4

Today I learned how to verify and troubleshoot a Dockerized application after a release when a reverse proxy sits in front of it on a Linux VM. The purpose of this part was to understand that in a proxy-based setup, release verification must follow the real user path, not just internal container state.

This is important because in real deployments, users usually do not connect directly to the application container. They connect to the reverse proxy first. That means a release can look healthy at backend container level but still be broken for users if the proxy layer is unhealthy, misconfigured, or unable to forward requests properly.

This part connects strongly to earlier learning:  
- Day-51 failure awareness and runtime truth  
- Day-53 release verification and rollback logic  
- Day-56 Linux VM operator verification discipline  
- Day-57 Part-1 and Part-2 proxy boundary and layered request flow  
- Day-57 Part-3 Nginx-style mental model

So this part is not isolated. It is where all that previous learning becomes practical troubleshooting discipline for a real user-facing app.

---

### 1) Why “release command finished” is still not enough in a proxy-based setup

A weak operator may think:  
- deployment command ran  
- containers are up  
- therefore release is fine

That is wrong.

In a proxy-based deployment, the user-facing request path is usually:  
- client  
- reverse proxy  
- app  
- dependency such as DB

So even if:  
- the app container is running  
- the app process is alive

the release can still be bad for users if:  
- the proxy is down  
- the proxy is not listening on the expected public port  
- the proxy is misconfigured  
- the proxy cannot reach the backend  
- the backend is reachable but returns bad responses through the proxy path

#### Why this matters

The user does not care that the app container exists.  
The user cares whether the application is actually reachable and usable through the real public route.

**In a proxy-based deployment, command completion and backend container liveness are not enough. The real public path must work correctly.**

---

### 2. Why public-path verification is mandatory after release

In earlier parts, you already learned that the reverse proxy is usually the only public service. That means the operator must verify the same path the user actually uses.

For example, if the service is exposed through:  
- `http://localhost:8080`  
    or
- a real domain routed through the proxy

then that path must be checked after release.

A weak verification style would be:  
- app container is running  
- app logs are fine  
- therefore success

A stronger verification style is:  
- public proxy path responds  
- proxy forwarding works  
- backend app behaves correctly  
- dependencies still work

#### Why this matters

Because a release may leave the app internally healthy but still break:  
- proxy routing  
- path handling  
- upstream connection  
- public usability

**If users normally enter through the proxy, then release verification must also enter through the proxy.**

---

### 3) Practical verification order after a release in a proxy-based deployment

A strong operator does not check things randomly.  
The checks should follow a structured order.

#### Step 1 — Check overall container or service state

The operator first checks:  
- is proxy running?  
- is app running?  
- is anything restarting?  
- did anything exit unexpectedly?

Typical examples:  
```bash
docker compose ps
docker ps
```

##### Why this is useful

This gives the first broad runtime signal.  
It helps the operator quickly see whether something is obviously dead or stuck in restart loops.

##### But important warning

This is still only the first check.  
It does not prove user-facing success.

#### Step 2 — Check the real public proxy-facing path

This is one of the most important checks.

The operator should test the actual route users use, for example:  
```bash
curl -I http://localhost:8080
curl http://localhost:8080/health
```

Or later:  
- real domain  
- real route path  
- real reverse proxy entry

##### Why this is useful

This is the fastest way to confirm whether the release worked from the outside-facing point of view.

**What this check can reveal**  
- proxy not reachable  
- public route broken  
- bad gateway behavior  
- timeout behavior  
- unexpected response codes

**The public proxy path is the most direct evidence of user-facing release success or failure.**

#### Step 3 — Check proxy logs

After checking the public path, the operator should inspect proxy logs.

Example:  
```bash
docker compose logs --tail=50 proxy
```

##### What to look for
- upstream connection failures  
- bad gateway style errors  
- timeout messages  
- configuration parse errors  
- startup issues  
- inability to resolve backend service

##### Why this matters

Proxy logs often show whether:  
- the request reached the proxy  
- the proxy tried to forward it  
- the forwarding failed before the app could serve anything

**Proxy logs are often the fastest evidence source when the public route is failing.**

#### Step 4 — Check app logs

Next, the operator should inspect the application logs.

Example:  
```bash
docker compose logs --tail=50 api
```

##### What to look for
- startup failure  
- missing environment variables  
- crash traces  
- runtime exceptions  
- dependency connection failures  
- unexpected internal errors

##### Why this matters
Sometimes the proxy is healthy and forwarding correctly, but the backend app itself is failing.

**Even in proxy-based troubleshooting, backend app evidence remains necessary.**

#### Step 5 — Check app health or internal readiness

If health checks exist, the operator should confirm:  
- app is healthy  
- app is not stuck unhealthy  
- app is not stuck starting forever

If there is an internal health route or readiness path, that also helps.

##### Why this matters
An app process can exist without actually being ready to serve real requests.

**Backend liveness is weaker than backend health or readiness.**

#### Step 6 — Check dependency connectivity

Finally, the operator should confirm that the app still reaches:  
- database  
- Redis  
- other backend services  
- any required integration paths

##### Why this matters
Some releases pass the container-level checks but still fail real behavior because the app cannot talk to the things it depends on.

**A release is not successful until the backend can still function through its dependency chain.**

---

### 4) How to separate proxy failure from backend app failure

This is one of the most important operator skills in a proxy-based deployment.

The user sees one symptom:  
- “site not working”

But the actual problem may belong to different layers.

#### Case A — Proxy/public entry problem

##### Typical symptoms
- public route does not respond at all  
- connection refused  
- no meaningful response from public endpoint  
- proxy container down

##### What this usually suggests

Start with:  
- proxy container issue  
- host-public exposure issue  
- wrong published port  
- proxy startup problem

**If the public path is not even reachable, start with proxy/public exposure, not app logic.**

#### Case B — Proxy reachable, but forwarding is broken

##### Typical symptoms
- 502  
- 504  
- bad gateway  
- upstream timeout

##### What this usually suggests

The proxy is alive, but the proxy-to-backend path is broken.

Possible causes:  
- wrong backend hostname  
- wrong backend service name  
- wrong backend port  
- proxy and app not on same network  
- app unreachable from proxy  
- app unhealthy/unready

**Gateway-style errors often indicate proxy-to-backend path failure, not just generic “site is down.”**

#### Case C — Proxy forwards correctly, but backend app is failing

##### Typical symptoms
- request reaches app  
- app returns 500 or functional error  
- app logs show startup or processing issue  
- DB connectivity problems appear

##### What this usually suggests

The proxy layer is probably okay, but the app or its dependencies are not behaving correctly.

**Do not blame the proxy automatically if the real issue is deeper in backend behavior.**

---

### 5) Why a 502 can happen even when the proxy container is running

This was your earlier checkpoint, and it is a very important lesson.

A running proxy container only proves:  
- the proxy process exists  
- the container is alive

It does not prove:  
- the proxy can reach the backend  
- the backend hostname is correct  
- the backend port is correct  
- the backend service is healthy  
- the backend network path works

So a **502** or similar gateway error can still happen because:  
- proxy points to wrong backend hostname  
- proxy points to wrong backend port  
- backend container is unhealthy  
- backend is not listening on expected port  
- proxy and backend are not on the same Docker network  
- backend times out when proxy tries to connect

**“Proxy is running” is only a liveness signal. It does not guarantee that proxy-to-backend forwarding is healthy.**

---

### 6) Why app container liveness is still a weak success signal

Another very important correction is this:  

Even if the backend app container is running, the release can still be bad for users.

Why?

Because the real user path is:  
- user → proxy → app

not:  
- user → app directly

So the operator must not conclude success just because:  
- app container exists  
- app process is alive

The release may still be bad because:  
- proxy is unhealthy  
- proxy is misconfigured  
- proxy cannot reach app  
- public route breaks  
- upstream path is wrong

**In a proxy-based deployment, backend container liveness alone is too weak to prove release success.**

---

### 7) Practical layered troubleshooting model after release

A strong operator should ask troubleshooting questions in the same order that real traffic flows.

#### Question 1
Can I reach the public proxy-facing endpoint?

If no:  
- public entry issue  
- proxy issue  
- host exposure issue

#### Question 2
Is the proxy container healthy and running?

If no:  
- proxy runtime problem

#### Question 3
Is the proxy forwarding to the correct backend service name and port?

If no:  
- upstream routing problem

#### Question 4
Is the app healthy and listening internally?

If no:  
- backend issue

#### Question 5
Is the app still reaching DB or other dependencies?

If no:  
- dependency path issue

#### Why this order is strong
Because it follows the real user request path instead of jumping randomly between logs and containers.

**A strong operator troubleshoots in the same order that traffic flows through the system.**

---

### 8) Why proxy logs and app logs must both be checked

A common beginner mistake is to choose only one layer.

#### Weak habit 1
Only check app logs and ignore proxy

#### Weak habit 2
Only check proxy logs and ignore backend

Both are incomplete.

#### Why proxy logs matter

They tell you:  
- whether request hit proxy  
- whether proxy tried to forward  
- whether upstream failed  

#### Why app logs matter

They tell you:  
- whether backend actually started  
- whether app crashed  
- whether dependencies failed  
- whether request processing broke

**Proxy-aware troubleshooting needs both proxy evidence and app evidence.**

---

### 9) When rollback should be considered in proxy-based release failures

Rollback should be considered when:  
- the public proxy-facing route is clearly broken after release  
- verification fails  
- user-facing service becomes unusable  
- previous exact version is known-good  
- recovery is more important than experimenting further in live production

#### Important point

Rollback decision should not be based only on:  
- whether a container is running

It should be based on:  
- actual user-facing service safety

So even if the app container is up, rollback may still be the correct choice if:  
- public route is failing  
- proxy forwarding is broken  
- service is effectively down for users

**In proxy-based systems, rollback decisions should be made using user-facing truth, not only container liveness.**

---

### 10) Example practical verification sequence after a release

A practical operator may do something like:  

1. `docker compose ps`  
2. `curl http://localhost:8080`  
3. `docker compose logs --tail=50 proxy`  
4. `docker compose logs --tail=50 api`  
5. check internal health if available  
6. confirm dependency connectivity

#### Why this is strong

Because it checks:  
- general state  
- real public path  
- proxy evidence  
- app evidence  
- internal health  
- backend function

This is a realistic release verification flow.

**A good operator checks both user-facing path and internal evidence after every proxy-based release.**

---

### 11) Biggest lessons from Day-57 Part 4

The most important things I learned are:  
- public-path verification is mandatory in proxy-based deployments  
- backend app liveness alone is not enough  
- a running proxy container does not guarantee working upstream forwarding  
- gateway errors often point to proxy-to-backend path problems  
- troubleshooting should follow the real request path  
- proxy logs and app logs both matter  
- rollback may be justified even when the app container is still running, if the real public route is broken

---

### 12) Final understanding statement for Part 4

Today I learned how to verify and troubleshoot a reverse-proxy-based Docker deployment after a release on a Linux VM. A strong operator must verify the real public proxy path, then inspect proxy behavior, backend app behavior, and dependency health in sequence. This layered approach prevents blind debugging and leads to better rollback decisions when user-facing routes break after a release.

---

