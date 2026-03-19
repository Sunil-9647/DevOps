## Day 46 — Restart Policies and Failure Recovery

### Goal of Day-46
The goal of this day was to understand what Docker does when a container stops unexpectedly, how restart policies behave, and why restart behavior is different for crashes versus intentional operator stops.

This is very important for production systems because services should recover from accidental failure, but operators must still remain in control.

---

### 1) Why restart policies matter
Containers can stop for many reasons:  
+ application crash  
+ bad config  
+ machine reboot  
+ dependency failure  
+ operator action

If no restart policy is defined, a failed service may simply stay down until someone restarts it manually.

That is risky for production workloads.

A restart policy tells Docker what to do when the container stops.

---

### 2) Restart policy types
Docker supports common restart policy behaviors:

#### `no`
- do nothing  
- stopped container stays stopped

#### `on-failure`
- restart only when the process exits with failure  
- useful for crash recovery  
- does not behave the same as always/on operator stops

#### `always`
- always restart when stopped  
- also restarts after daemon/host restart  
- can be too aggressive in some situations

#### `unless-stopped`
- restart automatically unless the container was intentionally stopped by the operator  
- very practical for long-running services

---

### 3) Policy used in our project
We inspected the API and DB containers and confirmed both were using:

```text
unless-stopped
```

This means:  
- unexpected stop → Docker should restart automatically  
- intentional operator stop → Docker should respect it and keep it stopped

---

### 4) Baseline before testing

Before failure injection we checked:  
- API container ID  
- DB container ID  
- both containers were healthy

Example:  
- API container ID stayed the same during the exercise

This was important because we wanted to observe:  
- whether Docker recreates a new container  
- or restarts the same container

---

### 5) Simulating an unexpected process failure

We simulated a crash by killing PID 1 inside the API container:  
```bash
docker exec python-fastapi-dockerfile-api-1 sh -c 'kill 1'
```
This is different from `docker stop`.  
This simulates the application process dying unexpectedly.

**Result**

After a short wait, `docker ps` showed the API container as:  
- Up again  
- healthy again  
- same container ID  
- fresh uptime

This proved:  
> Docker automatically restarted the same container after the unexpected process exit.

So `unless-stopped` successfully handled crash recovery.

---

### 6) Simulating an intentional operator stop

Next, we intentionally stopped the API container:  
```bash
docker stop python-fastapi-dockerfile-api-1
```

Then we checked with:  
```bash
docker ps -a ...
```

**Result**

The container showed:  
`Exited (0)`

and it did not restart automatically.

This is the key behavior of `unless-stopped`:  
> Docker respects an intentional operator stop and does not fight the operator.

---

### 7) Starting the container again

We then brought the API back intentionally using:  
```bash
docker start python-fastapi-dockerfile-api-1
```

The container returned to:  
- Up  
- healthy

This confirmed:  
- manual recovery still works normally  
- restart policy did not corrupt container state

### 8) Important distinction: crash vs manual stop

#### Crash / unexpected process exit
- restart policy applies  
- Docker may restart container automatically

#### Manual stop
- operator action  
- Docker respects the stop  
- container stays stopped

This distinction is extremely important for real operations.

---

### 9) Important learning about immutable prod images

During verification, we tried checking `/ready` on the restarted compose API container and got:  
```bash
{"detail":"Not Found"}
```
This happened because the compose production container was running a **digest-pinned GHCR image**, which did not include the newer local `/ready` code change.

This reinforced an important DevOps rule:  
> Restarting a prod container does not inject local source-code changes. A pinned artifact remains the same immutable image.

So the restart-policy test was still valid, but `/ready` was not the correct validation path for that pinned image.

---

### 10) Main takeaways

#### Lesson 1

Restart policies help with automatic recovery from unexpected process failure.

#### Lesson 2

`unless-stopped` is a practical balance:  
- restart on crash  
- do not restart after intentional operator stop

#### Lesson 3

Restart policies do not fix bad code or bad configuration.  
If the app is broken, restart policies may only create restart loops.

#### Lesson 4

Pinned production images remain immutable.  
Restarting a container does not update it with local code changes.

---

### 11) Commands used

**Check restart policy**  
```bash
docker inspect python-fastapi-dockerfile-api-1 --format '{{.HostConfig.RestartPolicy.Name}}'
docker inspect python-fastapi-dockerfile-db-1 --format '{{.HostConfig.RestartPolicy.Name}}'
```

**Check running containers**  
```bash
docker ps --filter name=python-fastapi-dockerfile-api-1 --format 'table {{.Names}}\t{{.ID}}\t{{.Status}}'
docker ps --filter name=python-fastapi-dockerfile-db-1 --format 'table {{.Names}}\t{{.ID}}\t{{.Status}}'
```

**Simulate crash**  
```bash
docker exec python-fastapi-dockerfile-api-1 sh -c 'kill 1'
```

**Simulate intentional stop**  
```bash
docker stop python-fastapi-dockerfile-api-1
```

**Start again**  
```bash
docker start python-fastapi-dockerfile-api-1
```

---

###Final takeaway

A restart policy is not just about restarting containers. It is about defining the correct failure-recovery behavior. In our project, `unless-stopped` proved to be a useful policy because it automatically recovered from an unexpected process crash while still respecting intentional operator stops.

---

