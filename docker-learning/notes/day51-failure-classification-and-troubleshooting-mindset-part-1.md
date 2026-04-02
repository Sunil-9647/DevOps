## Day 51 — Failure Scenarios, Troubleshooting, and Operational Recovery Mindset (Part 1)

### Objective of Day-51 Part 1

Today I started learning how to think when Docker-based systems fail. Until now, I learned how to build images, run containers, connect services, manage configuration, and tag images correctly. But real DevOps work is not judged when everything is normal. It is judged when something breaks.

The goal of this part was to understand that Docker failure handling is not about panic, random restarts, or deleting and recreating things blindly. It is about first classifying the type of failure, then collecting the correct evidence, and only after that choosing the right recovery action.

This is important because many engineers lose time by asking vague questions like:  
- “Docker is not working”  
- “Container failed somehow”  
- “Maybe network issue”  
- “Maybe image issue”

That kind of language is too weak for real troubleshooting. A good engineer must identify what type of failure happened and what layer of the system is actually broken.

---

### 1) Not all Docker failures are the same
One of the biggest lessons from today is that failures must be classified. If I do not classify the failure properly, then I may apply the wrong fix.

For example:  
- if the problem is wrong environment configuration, rebuilding the image may be useless  
- if the problem is a broken image `CMD`, restarting the container will not solve it  
- if the database is down, debugging only the API container will waste time  
- if a bind mount is hiding expected files, the image may be fine but the runtime path is wrong

So the first rule is:  

**Do not start with random fixes. Start with failure classification.**

---

### 2) Main failure categories in Docker environments
Today I learned that common Docker failures can be grouped into clear buckets.

#### A. Startup failure

This happens when the container never starts properly or exits immediately after starting.

Common reasons:  
- wrong command  
- missing executable  
- bad entrypoint  
- missing dependency  
- startup script failure  
- immediate crash in application startup

#### B. Runtime failure

This happens when the container starts successfully, but the application crashes later.

Common reasons:  
- app exception  
- runtime bug  
- memory issue  
- unexpected dependency behavior  
- long-running process failure

#### C. Health failure

This happens when the container is still running, but Docker marks it unhealthy.

Common reasons:  
- health check endpoint failing  
- application partially broken  
- startup not complete  
- dependency not available  
- process alive but service unusable

#### D. Connectivity failure

This happens when one service cannot reach another.

Common reasons:  
- wrong hostname  
- wrong port  
- wrong network membership  
- dependency not ready  
- `localhost` used incorrectly  
- target service not listening

#### E. Configuration failure

This happens when the application starts, but runtime values are wrong.

Common reasons:  
- wrong env vars  
- missing values  
- empty values  
- wrong DB host  
- wrong credentials  
- wrong mode such as dev vs prod

#### F. Storage or mount failure

This happens when files or data are missing, hidden, overwritten, or not persisted as expected.

Common reasons:  
- wrong bind mount path  
- named volume confusion  
- empty host path overlaying image content  
- permission mismatch  
- wrong persistence expectations

#### G. Resource failure

This happens when the host or runtime environment cannot provide enough system resources.

Common reasons:  
- memory pressure  
- disk full  
- CPU starvation  
- host-level resource exhaustion

**Main lesson**  
If I can identify which category the failure belongs to, then my troubleshooting becomes much faster and more accurate.

---

### 3) Container state is not the same as application state

This was one of the most important lessons of the day.

A Docker container has a state such as:  
- running  
- exited  
- restarting  
- unhealthy

But the application inside the container may be in a different practical condition.

For example:  
- the container can be `Up`, but the app endpoint may be failing  
- the process can still be alive, but the app may be stuck  
- the container can be running, but the DB connection may be broken  
- the health check may be failing even though Docker still shows the container as running

So the sentence:  
“**The container is running, therefore the app is fine**”  
is not reliable.

**Main lesson**  
Container state tells me something useful, but it does not fully describe application health.

---

### 4) Meaning of common Docker container states
Today I learned how to interpret common container states more carefully.

#### `Up`
This means the container’s main process is currently running.

It does not prove:  
- the application is ready  
- the endpoint is reachable  
- dependencies are connected  
- health checks are passing

#### `Exited`
This means the container stopped because its main process ended.

This can happen because:  
- the process crashed  
- the command completed  
- startup failed  
- configuration was wrong  
- a script exited

#### `Restarting`
This means the main process keeps failing and Docker is starting it again according to restart policy.

This usually suggests:  
- crash loop  
- startup failure  
- repeated runtime failure  
- unstable app state

It does not mean automatic recovery is actually working.

#### `Unhealthy`
This means the main process is running, but Docker’s health check logic is failing.

This often means:  
- app is partially broken  
- app is not yet ready  
- health endpoint is wrong  
- dependency is down  
- service is alive but not usable

**Main lesson**  
Each Docker state is a clue, but not the full diagnosis.

---

### 5) Why PID 1 matters
A very important operational principle from Docker is that the container lives as long as its main PID 1 process lives.

That means if PID 1:  
- exits normally  
- crashes  
- fails to start  
- finishes quickly

then the container will also stop.

This explains many cases where beginners say:  
- “Docker stopped my container.”

Usually, Docker did not randomly stop it.  
The main process inside the container ended.

**Main lesson**  
If a container exits immediately, I should first suspect that PID 1 ended, crashed, or failed during startup.

---

### 6) Immediate-exit failure pattern

A very common Docker failure scenario is:  
- container starts  
- container exits immediately

This usually means the main process did not stay alive.

Common causes include:  
- wrong command  
- app crash  
- command not found  
- bad script  
- missing file  
- incorrect entrypoint  
- configuration required at startup but not available

**Correct first checks**

If this happens, I should first use:  
- `docker ps -a`  
- `docker logs <container>`  
- `docker inspect <container>`

These usually tell me:  
- whether the container died quickly  
- what the app printed before exit  
- which command/entrypoint was used  
- what runtime configuration and mounts were active

**Main lesson**  
Immediate exit is not a mystery. It usually means the main startup process failed or finished.

---

### 7) Running container but unreachable application

Another common real-world scenario is:  
- Docker shows the container as running  
- but the endpoint is not reachable

Examples:  
- browser gets no response  
- `curl` fails  
- reverse proxy cannot reach the app  
- health check keeps failing

This means I must not stop at:  
- “container is Up”

Instead, I must ask:  
- is the app listening on the expected port?  
- is the right host port published?  
- is the app still initializing?  
- is the app bound to the right interface?  
- is the health endpoint failing?  
- is a dependency causing delayed readiness?

**Main lesson**  
“Running” is not the same as “serving traffic correctly.”

---

### 8) App-to-dependency failure pattern

One of the most common multi-container failures is when the application cannot reach a dependency such as a database.

Common reasons include:  
- wrong service name  
- wrong port  
- wrong environment values  
- missing shared network  
- DB not ready yet  
- wrong credentials  
- `localhost` misuse inside container

This is exactly why earlier days mattered:  
- Day-47 gave networking discipline  
- Day-48 gave configuration discipline

Now Day-51 uses both during failure handling.

#### Correct troubleshooting order for API-to-DB failure
1. Is the DB container running?  
2. Is it healthy or ready?  
3. Is `DB_HOST` correct?  
4. Is the port correct?  
5. Are both containers on the correct shared network?  
6. Can the hostname resolve?  
7. Only after basics, check credentials and deeper application logic.

**Main lesson**  
Do not blame “Docker networking” first when the real issue may simply be wrong hostname or readiness.

---

### 9) Health-check failures are more meaningful than “running”

Health-check failures are especially important because they expose a deeper truth:  
- the process is alive  
- but the service is not healthy enough to pass defined checks

This often happens when:  
- app is alive but endpoint fails  
- readiness is incomplete  
- dependency is not available  
- app is hanging internally  
- health command itself is wrong

**Main lesson**  
A container can be both:  
- running  
   and  
- unhealthy  

This is why health checks are operationally more useful than just “container is up.”

---

### 10) Configuration failures may not crash the container

This is dangerous because configuration failures can look invisible at first.

Examples:  
- wrong `DB_HOST`  
- wrong `APP_ENV`  
- empty required variable  
- wrong credentials  
- wrong API endpoint

Sometimes the container starts and stays alive, but the app behaves incorrectly.

That means:  
- startup success does not guarantee correct runtime configuration  
- “container did not crash” does not prove the service is valid

**Main lesson**  
Configuration failures can be silent and still break the application badly.

---

### 11) Mount and volume failures

Another major lesson today was that storage-related issues often look like app failures.

Examples:  
- file not found  
- config missing  
- app directory suddenly empty  
- data disappeared after recreation  
- app cannot write to mounted path

One especially dangerous bind-mount mistake is mounting a host path over a location that already contains files in the image.

Example idea:  
- image contains files at `/app`  
- a bind mount overlays `/app`  
- host path is empty

Now the original image files are hidden at runtime.

A beginner may say:  
- “Docker removed my files.”

That is wrong.

**Correct explanation**  
The mount overlaid the path and hid what was inside the image at that location.

**Main lesson**  
Mounts can hide image content without deleting it.

---

### 12) Restart loops do not automatically mean recovery

If a container is repeatedly restarting, a beginner may think:  
- “Docker is fixing the issue automatically.”

That is not safe thinking.

A restart loop often means:  
- the app is crashing repeatedly  
- Docker restart policy is just starting it again  
- the root cause is still unresolved

So repeated restarting is usually a **symptom**, not a recovery proof.

**Main lesson**  
A stable recovered service is not the same thing as a repeatedly restarting container.

---

### 13) Image problem vs container instance problem

A very important troubleshooting distinction is whether the issue is:  
- in the running container instance  
   or  
- in the image itself  

#### Image-level problems

Examples:  
- broken `CMD`  
- missing dependency inside image  
- wrong files copied during build  
- broken entrypoint  
- bad permissions inside image

If the image is broken, then:  
- recreating the same container from the same image will reproduce the same problem

#### Container-instance problems

Examples:  
- wrong runtime env values  
- wrong mount  
- wrong network attachment  
- temporary state issue

In these cases, recreate or re-run may help if the underlying image is good.

**Main lesson**  
Do not confuse “broken container instance” with “broken image.”

---

### 14) First troubleshooting tools and why they matter

The first tools I should think of are:  
`docker ps -a`

To check:  
- running  
- exited  
- restarting  
- unhealthy

`docker logs <container>`

To check:  
- startup errors  
- crash messages  
- stack traces  
- missing env/config  
- missing files  
- dependency failures

`docker inspect <container>`

To check:  
- entrypoint and command  
- env vars  
- health status  
- mounts  
- network attachments  
- restart policy

`docker exec -it <container> sh`

To inspect inside the container if it is running:  
- files  
- environment  
- network reachability  
- application behavior from inside

**Main lesson**  
Good troubleshooting starts with observation commands, not random fixes.

---

### 15) Safe troubleshooting order

The safe order I learned today is:  
1. Observe container state  
2. Read logs  
3. Inspect container config, mounts, and networks  
4. Check health status  
5. If the container is running, inspect inside  
6. Check dependency reachability if needed  
7. Only then choose a recovery action

**Why this order matters**

Because it preserves evidence and reduces guessing.

If I start with random restart, rebuild, delete, or prune actions, I may destroy useful clues and make the investigation worse.

---

### 16) What not to do in panic

When something fails, a weak troubleshooting reaction is:  
- restart everything  
- rebuild immediately  
- delete containers  
- prune all images  
- change multiple variables at once  
- blame Docker without evidence

This is bad because:  
- evidence gets lost  
- root cause becomes harder to identify  
- many changes happen at once  
- if the service recovers, I may still not know why

**Main lesson**  
Do not panic-debug. Observe first, then act deliberately.

---

### 17) Recovery actions are not the same thing

Another very important lesson is that these actions are different:  
- restart  
- recreate  
- rebuild  
- rollback  
- fix runtime config  
- fix dependency service  
- fix mounts/volumes

They are not interchangeable.

**Restart may help when:**  
- the issue is temporary or transient

**Recreate may help when:**  
- runtime config or mounts must be reapplied to a fresh instance

**Rebuild is needed when:**  
- the image itself is bad

**Rollback is safer when:**  
- the current image version is broken and a known-good version exists

**Config fix is the real answer when:**  
- env values are wrong

**Dependency recovery is the real answer when:**  
- the app is fine but the DB or another dependency is down

**Main lesson**  
Correct recovery depends on correct classification of the failure.

---

### 18) Why rollback is often safer than blind rebuild during incidents

In a production incident, the fastest safe path is often to:  
- restore a known-good image  
- restore a known-good configuration  
- bring service back quickly  
- then analyze the root cause

Blind rebuild under pressure is risky because:  
- the new rebuild may introduce another unknown  
- there may not be time to validate properly  
- recovery becomes less predictable

**Main lesson**  
Known-good rollback is often safer than improvising a new fix during active incident pressure.

---

### 19) Good incident language

Instead of vague statements like:  
- “Docker is broken”  
- “Container not working”  
- “Maybe network issue”

I should use precise language such as:  
- container is restarting because PID 1 exits after startup  
- container is running but unhealthy because the health endpoint fails  
- API cannot reach DB because hostname is wrong  
- bind mount is hiding expected image files  
- image has broken `CMD`, so recreating the same container will not help

**Main lesson**  
Precise language improves precise troubleshooting.

---

### 20) Biggest lessons from Day-51 Part 1

The key things I learned today are:  
- not all Docker failures are the same  
- failure must be classified before choosing a fix  
- container state is not the same as application state  
- running does not guarantee healthy application behavior  
- immediate exit usually means PID 1 ended  
- restart loops often mean crash loops, not recovery  
- app-to-DB failures should first check hostname, port, network, and readiness  
- bind mounts can hide image files without deleting them  
- broken images cannot be fixed by recreating the same bad container  
- safe troubleshooting starts with state, logs, inspect, and evidence collection  
- panic actions often destroy useful clues  
- rollback is often safer than blind rebuild during active incidents

---

### 21) Final understanding statement for Part 1
Today I learned that Docker troubleshooting is not about guessing or trying random commands until something works. It is about first understanding what layer of the system failed, then collecting the right evidence, then choosing the correct recovery action. I also learned that container state and application state are different, and that failures can come from the image, runtime config, dependencies, networking, mounts, or health logic. This mindset is essential for real production incident handling.

---
