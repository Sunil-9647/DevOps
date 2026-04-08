## Day-53 — Single-Host Deployment Workflow and Release Runbook (Part 2)

### Objective of Day-53 Part 2

In this part, I practiced writing a simple Docker release runbook for a single-host deployment. The goal was to turn Docker knowledge into operational deployment procedure.

The scenario used was:  
- a single-host stack with `proxy`, `api`, and `db`  
- only the `api` image was being updated  
- the database had to remain intact  
- the proxy had to continue routing correctly  
- the release needed both verification and rollback steps

This was important because a real deployment is not only about starting a new container. It is about changing a running service safely, verifying that it works, and recovering safely if it fails.

---

### 1) Release scenario used in the exercise

The scenario was:  
- single host  
- `proxy`, `api`, and `db` stack  
- only `api` service is updated  
- current known-good image: `ghcr.io/sunil-9647/myapi:1.2.0`  
- target image: `ghcr.io/sunil-9647/myapi:1.2.1`  
- rollback image: `ghcr.io/sunil-9647/myapi:1.2.0`

**Main lesson**

A release runbook should always be written around a clearly defined change scope.

---

### 2) Why exact image identity must be part of the runbook

One of the most important lessons was that the runbook must begin by identifying:  
- what exact image is currently running  
- what exact target image is about to be released  
- what exact previous image will be used for rollback if needed

#### Why this matters
Because safe release and safe rollback both depend on exact image identity.

If the team only says:  
- “deploy the newest one”  
- “use stable”  
- “roll back to latest”

then the procedure is weak and risky.

**Main lesson**

A release runbook must start with exact version awareness, not vague tag guessing.

---

### 3) Pre-deploy checks in the runbook

Before the release begins, the runbook should require these checks:  
1. confirm exact currently running image  
2. confirm exact target image  
3. confirm exact rollback image  
4. confirm proxy and DB are healthy before the change  
5. confirm runtime configuration is correct  
6. confirm DB persistence/volume is safe and unchanged  
7. confirm verification commands and endpoints are already known

#### Why this matters
A good release starts before the update itself.

If the surrounding environment is already broken, then deployment results become harder to interpret correctly.

**Main lesson**

Pre-deploy checks reduce risk by ensuring the change is happening in a known-good environment.

---

### 4) Deployment steps in the runbook

The runbook then defined a controlled update flow:  
1. pull or prepare the exact target image  
2. update or recreate only the `api` service  
3. do not disturb DB storage or unrelated services  
4. observe new container state immediately after update  
5. keep rollback identity ready until the release is proven stable

#### Why this matters
A release should have the smallest necessary blast radius.

In this scenario, only `api` should change. The DB and its persistence should not be touched carelessly.

**Main lesson**

A controlled deployment updates only what is intended and keeps recovery options ready.

---

### 5) Post-deploy verification in the runbook

The runbook included these post-deploy checks:  
1. container state  
2. logs  
3. health status  
4. proxy-to-api path  
5. api-to-db connectivity  
6. real user/API endpoint behavior

#### Why this matters
A release is not successful just because the container exists or is running.

The service must also:  
- become healthy  
- connect to dependencies  
- respond correctly through the real access path

**Main lesson**

Post-deploy verification must test actual service behavior, not only Docker liveness.

---

### 6) Rollback steps in the runbook

The runbook included these rollback steps:  
1. identify that deployment verification failed  
2. redeploy the exact previous known-good image  
3. verify rollback success using state, logs, health, and endpoint checks  
4. document what failed in the bad release before retrying later

#### Why this matters
Rollback must not be improvised under pressure.

The exact rollback image and rollback procedure should already be known before the deployment starts.

**Main lesson**

Rollback planning is part of the release plan, not an afterthought.

---

### 7) Operational discipline learned from the runbook exercise

This exercise taught me that a release runbook is not only a technical checklist. It is also an operational safety tool.

A weak release process looks like:  
- no exact image identity  
- no clear verification path  
- no rollback plan  
- changes made from memory  
- release considered successful only because the container started

A stronger release process includes:  
- exact image awareness  
- pre-checks  
- controlled update scope  
- real post-deploy verification  
- exact rollback procedure  
- release documentation

**Main lesson**

Operational safety comes from repeatable procedure, not from confidence alone.

---

### 8) Final understanding statement for Part 2

Today I practiced converting Docker knowledge into a release runbook. I learned that a good single-host deployment procedure must begin with exact image identity, continue with pre-deploy checks and controlled update steps, and end with real verification and documented rollback steps. This is how Docker usage becomes disciplined release operations instead of manual container replacement.

---
