## Day 56 — Practical Production-Style Deployment Patterns on a Linux VM (Part 5)

### Objective of Day-56 Part 5

Today I learned one full end-to-end operator story for releasing a Dockerized application on a Linux VM. The purpose of this part was to connect all the separate ideas from earlier days into one practical runtime flow.

Until now, I learned:  
- how Docker images are built and tagged  
- why CI/CD should build exact artifacts  
- why the VM should consume prebuilt images instead of rebuilding from source  
- how `compose.yaml`, `.env`, and helper scripts can be used on the server  
- how the operator should verify runtime behavior after release  
- why rollback must be exact and based on the previous known-good image

In this part, I connected all of these into one realistic server-side release story:  
- current image on the VM  
- target image to be released  
- controlled `.env` update  
- Compose update  
- runtime verification  
- rollback decision if needed  
- release record at the end

This is important because operations become strong only when all the individual concepts connect into one practical story.

---

### 1. Example release scenario used in this story

The VM has one application deployment directory, for example:  
```
/opt/myapp/
```

Inside it, the operator has:  
- `compose.yaml`  
- `.env`  
- `scripts/deploy.sh`  
- `scripts/rollback.sh`  
- `release-history/`

The application service is defined in Compose using a variable-driven image reference:  
```YAML
services:
  api:
    image: ghcr.io/sunil-9647/myapp:${APP_IMAGE_TAG}
```

And the current `.env` contains something like:  
```
APP_IMAGE_TAG=1.2.0
POSTGRES_DB=myapp
POSTGRES_USER=myappuser
POSTGRES_PASSWORD=change-me
```

The current running image is:  
```
ghcr.io/sunil-9647/myapp:1.2.0
```

The target release image is:  
```
ghcr.io/sunil-9647/myapp:1.2.1
```

So the release goal is very clear:  
- current version = `1.2.0`  
- target version = `1.2.1`

That is exactly how a controlled single-host release should begin: with exact current and target identity.

**A practical server-side release starts with exact current image identity and exact target image identity, not vague ideas like “some newer build.”**

---

### 2. What the operator must confirm before changing anything

Before touching `.env` or running any Compose update, the operator must first establish a known starting point.

The operator should confirm:  
1. the current running image is really `1.2.0`  
2. the new target image is really `1.2.1`  
3. the rollback target will be `1.2.0`  
4. the current service is already healthy and stable  
5. the `.env` file is correct and not already broken  
6. volumes and persistence are safe  
7. no unrelated incident is already happening on the server

#### Why this matters

If the service is already unhealthy before the release begins, then after the release it becomes very hard to know whether the new problems came from:  
- the new image  
    or  
- the old already-broken state

That makes:  
- debugging harder  
- release verification less trustworthy  
- rollback decisions more confusing

**A release should begin only from a known and stable runtime state, otherwise the operator loses clarity about cause and effect.**

---

### 3. The real runtime control point on the VM

In this deployment pattern, the key runtime release switch is:  
```
APP_IMAGE_TAG=1.2.0
```

That line in `.env` is what tells Compose which exact application image to use.

Before release:  
```
APP_IMAGE_TAG=1.2.0
```

After release:  
```
APP_IMAGE_TAG=1.2.1
```

This means the server-side release is often not a giant configuration rewrite.  
It is often one exact and controlled version change.

#### Why this is strong

Because the operator is not changing:  
- service topology  
- networks  
- volumes  
- many runtime settings  
- many unrelated deployment details

Instead, the operator is changing one exact value that points to one exact image.

That keeps the release focused.

**In a strong single-host Docker release pattern, `.env` often acts as the exact runtime switch for application image version.**

---

### 4. What changes during the release and what stays stable

This is one of the most important practical lessons.

#### What changes

Usually, only:  
- `APP_IMAGE_TAG`

changes from:  
- `1.2.0`  
    to  
- `1.2.1`

#### What stays stable

Usually all of these stay the same:  
- compose.yaml  
- service wiring  
- network layout  
- volume definitions  
- DB settings unless intentionally changed  
- reverse proxy structure  
- runtime architecture

**Why this is safer**

Because if only one controlled thing changes, then:  
- the blast radius is smaller  
- debugging is easier  
- rollback is clearer  
- the release cause is easier to identify

If many runtime details are changed at the same time, then failure analysis becomes harder because too many possible causes were introduced in one step.

**A safer release keeps the deployment structure stable and changes only the exact image identity that needs to be updated.**

---

### 5. How the release is applied through Compose

Once `.env` has the new tag, the operator applies the release using a common Compose pattern:  
```bash
docker compose --env-file .env pull api
docker compose --env-file .env up -d api
```

#### Meaning of the first command

`pull api` tells Docker to fetch the exact app image now configured in `.env`.  

So if `.env` now says:  
- `APP_IMAGE_TAG=1.2.1`

then Docker will pull:  
- `ghcr.io/sunil-9647/myapp:1.2.1`

#### Meaning of the second command

`up -d api` tells Compose to update or recreate only that service using the configured image.

This is a very common and realistic single-host deployment pattern.

**Why this matters**

It proves again that:  
- the VM is consuming an exact prepared image  
- the VM is not rebuilding source code  
- the release is a controlled exact-image update event

**A practical Compose-based release often means: update exact image version in config, then pull and reapply the service cleanly.**

---

### 6. Why the release is still not finished after the update command

A weak operator may think:  
- the command ran successfully  
- therefore the release is complete

That is wrong.

After `docker compose up -d api`, the operator still does not know whether:  
- the app really started correctly  
- config is correct  
- health is good  
- endpoint works  
- dependency path still works

So the release command only changes runtime state.  
It does not prove release success.

**The release is not complete when the update command finishes. It is complete only after runtime behavior is verified.**

---

### 7. Operator verification after the release

After applying the new image, the operator should verify in a structured order.

#### 1-State

The operator checks:  
- is the service running?  
- is it restarting?  
- did it exit?  
- does it look unhealthy?

Typical commands:  
```bash
docker compose ps
docker ps
```

This gives the first runtime signal.

#### 2-Logs

The operator then checks:  
- startup logs  
- config errors  
- missing variable errors  
- dependency connection failures  
- crash traces  
- suspicious warnings

Typical command:  
```bash
docker compose logs --tail=50 api
```

Logs often explain why a new image is not behaving correctly.

#### 3-Health

If health checks exist, the operator confirms:  
- healthy  
- not stuck unhealthy  
- not stuck starting forever

This is stronger than merely seeing a running process.

#### 4-Endpoint behavior

The operator tests:  
- real service endpoint  
- maybe `/health`  
- maybe reverse-proxy path  
- maybe expected API response

Typical examples:  
```bash
curl -I http://localhost:8080
curl http://localhost:8080/health
```

This proves that the service is actually usable.

#### 5-Dependency connectivity

The operator also confirms:  
- API can still reach DB  
- runtime dependency behavior still works  
- no broken environment wiring happened

**Why this full order matters**

Because a service may:  
- be running  
- but still be unhealthy  
- or be healthy by process definition but still broken at endpoint level  
- or respond on endpoint but still fail when hitting dependencies

**A strong operator verifies state, logs, health, endpoint, and dependency behavior before calling the release successful.**

---

### 8. Successful release path in this story

Suppose all checks pass.

The operator sees:  
- the container is running  
- logs look normal  
- health is good  
- endpoint is responding correctly  
- dependency connectivity is fine

Now the release can be considered successful.

At that point, the operator should write a release record such as:  
```
Date: 2026-04-23 21:10
Environment: production
Previous image: ghcr.io/sunil-9647/myapp:1.2.0
New image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Verification: passed
Notes: config unchanged, endpoint and health verified
```

**Why this matters**

Because this record tells the future operator:  
- what changed  
- when it changed  
- what image was running before  
- what the rollback target is  
- whether verification passed

**A successful release should leave behind a short factual record, not just a memory in the operator’s head.**

---

### 9. Failed release path in this story

Now let us take the other path.

Suppose after the release the operator sees:  
- the container is running  
- but health fails  
- logs show DB connection problems  
- endpoint returns 502 or another bad response

This is where discipline matters.

A weak operator may:  
- try random quick fixes  
- edit config blindly  
- make many changes under pressure  
- hope it resolves itself

A stronger operator asks:  
- is rollback the safer action now?

If the previous image `1.2.0` is known-good and the new release clearly reduced service safety, then rollback is often the correct response.

**When the new release is clearly making the service less safe, rollback is often safer than improvising many live fixes.**

---

### 10. What rollback looks like in the same VM story

Because rollback target was already known, the operator does not have to guess.

The operator restores `.env` back to:  
```
APP_IMAGE_TAG=1.2.0
POSTGRES_DB=myapp
POSTGRES_USER=myappuser
POSTGRES_PASSWORD=change-me
```

Then applies the same Compose pattern again:  
```bash
docker compose --env-file .env pull api
docker compose --env-file .env up -d api
```

Why this is strong

Because rollback is:  
- exact  
- controlled  
- based on known-good artifact  
- using the same stable deployment mechanism  
- not depending on vague ideas like “something stable”

**Rollback on the VM should be the controlled reverse of the release: restore the previous exact image and reapply the service.**

---

### 11. Rollback is not successful until recovery is verified

A weak operator may think:  
- old version was re-applied  
- rollback is done

That is incomplete.

After rollback, the operator must again verify:  
1. state  
2. logs  
3. health  
4. endpoint behavior  
5. dependency connectivity

Only if those are good again can rollback be considered successful.

**Why this matters**

Because rollback is a recovery action, and recovery is only real when service behavior is restored.

**Main lesson**

Rollback is only complete after verified recovery, not just after re-running an old image.

---

### 12. What rollback record should be written

If rollback happens, a small rollback record should be written, for example:  
```
Date: 2026-04-23 21:18
Environment: production
Failed image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback image: ghcr.io/sunil-9647/myapp:1.2.0
Reason: health failed and endpoint returned 502
Rollback verification: passed
```

#### Why this is useful

Because later, the team can quickly understand:  
- what failed  
- what recovered the service  
- whether rollback verification passed  
- which image should be investigated

**Rollback records are incident evidence, not unnecessary paperwork.**

---

### 13. What this full operator story teaches

This end-to-end VM story teaches several connected truths:

#### A. A Linux VM release is often an exact-image switch

The release is often just:  
- `1.2.0` → `1.2.1`

not a rebuild of source code on the server.

#### B. `.env` can act as a controlled release switch

One exact version variable can control which image runs.

#### C. Compose applies the selected runtime state

The server consumes the chosen image identity.

#### D. Verification is mandatory after release

Not optional. Not assumed.

#### E. Rollback must be pre-known and exact

Not guessed during panic.

#### F. Records matter

Because incidents and audits happen later, not only during the happy release path.

**A strong single-host Docker release on a Linux VM is not only about changing the image version. It is about changing it in a controlled way, verifying the result, and keeping rollback exact and documented.**

---

### 14. Biggest lessons from Day-56 Part 5

The biggest things I learned are:  
- a practical VM release starts with exact current and target image identity  
- `.env` can control the exact app version on the server  
- Compose pulls and applies the configured image  
- release success must be verified through runtime checks  
- failures should trigger exact rollback thinking, not random experimentation  
- rollback should restore the previous exact known-good image  
- both release and rollback should leave behind short factual records

---

### 15. Final understanding statement for Part 5

Today I learned the full operator story of a Dockerized release on a Linux VM. A strong server-side release begins with exact current and target image identity, applies a controlled image-version change through stable runtime files, verifies runtime behavior after the update, and if needed, rolls back to the exact previous known-good image and verifies recovery. This is the practical operational form of Docker release discipline on a single host.

---

