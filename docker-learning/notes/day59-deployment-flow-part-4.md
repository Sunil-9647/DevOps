## Day 59 — Practical Remote Deployment Flow from CI/CD to Linux VM (Part 4)

### Objective of Day-59 Part 4

Today I learned one full end-to-end remote deployment story from CI/CD approval to Linux VM runtime verification and rollback. The purpose of this part was to connect all Day-59 concepts into one complete operational flow.

Earlier in Day-59, I learned:  
- CI/CD should build and approve the exact Docker artifact  
- the Linux VM should consume the exact artifact, not rebuild from source  
- the handoff from CI/CD to the VM should behave like a small deployment contract  
- CI/CD should trigger trusted VM-side deployment logic  
- the VM still owns runtime verification and rollback execution

In this part, I connected all of those ideas into one story:  
- current production image  
- new approved image  
- deployment contract  
- trusted VM-side script  
- runtime update  
- proxy/user-facing verification  
- rollback if verification fails  
- release or rollback record

This is important because a real remote deployment is not finished when the pipeline sends a command. It is finished only when the target VM proves that the new release works correctly in the real runtime environment, or when rollback restores service safely.
---
### 1. Starting condition before remote deployment

In the example story, the application is already running on a Linux VM.

The current production state is:  
```
Service: myapp
Environment: production
Current image: ghcr.io/sunil-9647/myapp:1.2.0
Public route: http://localhost:8080
```

The VM has a production-style deployment layout:  
```
/opt/myapp/
├── compose.yaml
├── .env
├── scripts/
│   ├── deploy.sh
│   ├── verify.sh
│   └── rollback.sh
├── release-history/
└── rollback-history/
```

The current `.env` contains:  
```
APP_IMAGE_TAG=1.2.0
```

#### Why this matters

Before changing anything, the operator or deployment system must know the current runtime state. If the current state is unclear, rollback and verification become weaker.


**A strong deployment begins with knowing the current production image, active runtime config, public route, and rollback baseline.**
---
### 2. CI/CD builds and approves the new artifact

A new commit enters the pipeline.

CI/CD performs the release preparation work:  
1. validates the code  
2. builds the Docker image once  
3. pushes the image to the registry  
4. records the image tag and digest  
5. deploys or verifies the artifact in staging  
6. receives production approval

The approved production image becomes:  
```
ghcr.io/sunil-9647/myapp:1.2.1
```

Optional digest:  
```
sha256:abc123...
```

#### Important rule

The Linux VM does **not** rebuild this image.

The VM will only **consume the exact image** that CI/CD already built and approved.

#### Why this matters

This preserves:  
- build-once discipline  
- artifact traceability  
- staging-to-production confidence  
- rollback clarity


**CI/CD creates and approves the exact artifact; the VM consumes that artifact instead of recreating it.**
---
### 3. CI/CD prepares a deployment contract

Before CI/CD triggers the VM, it should have a clear and exact deployment contract.

Example:  
```
Environment: production
Service: myapp
Approved image: ghcr.io/sunil-9647/myapp:1.2.1
Digest: sha256:abc123...
Current production image: ghcr.io/sunil-9647/myapp:1.2.0
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Verify route: http://localhost:8080
```

#### Why this is strong

This contract tells the VM:  
- what exact image to deploy  
- which environment is targeted  
- what image is being replaced  
- what rollback target matters  
- which public route must be verified

#### Weak alternative

A weak handoff would say:  
- deploy latest  
- update the app  
- run the newest build

That is not enough because it does not provide exact deployment or rollback identity.


**A deployment contract removes guesswork before the VM touches production.**
---
### 4. CI/CD triggers trusted deployment logic on the VM

After the deployment contract is prepared, CI/CD causes the VM to run the official deployment procedure.

Conceptually, the VM may run something like:  
```
/opt/myapp/scripts/deploy.sh 1.2.1
```

The exact remote trigger method can vary, but the principle is the same:  

CI/CD should trigger:  
- trusted deployment logic  
- with exact target input  
- in the correct environment

It should not trigger:  
- random command sequences  
- shell-history improvisation  
- vague “deploy latest” commands  
- source-code rebuild on the VM

#### Why this matters

Trusted scripts make deployment more repeatable and safer. They reduce dependency on memory and prevent the VM from becoming a place where release behavior is invented each time.


**Remote deployment should trigger trusted VM-side procedure, not random commands or server-side improvisation.**
---
### 5. What deploy.sh does on the VM

A good `deploy.sh` script behaves predictably.

It may perform steps such as:  

1. read the current tag from `.env`  
2. store current tag as rollback target  
3. update `.env` to the new target tag  
4. pull the exact approved image  
5. apply the Compose update  
6. call verification logic  
7. write a release record if successful  
8. stop or trigger rollback path if verification fails

Before deployment:  
```
APP_IMAGE_TAG=1.2.0
```

After deployment:  
```
APP_IMAGE_TAG=1.2.1
```

The script understands:  
```
Current tag: 1.2.0
New tag: 1.2.1
Rollback target: 1.2.0
```

#### Why this matters

The script applies one controlled runtime change: the backend image version. It does not randomly modify config, proxy, database, or storage.


**The VM-side deploy script applies the exact approved artifact and preserves rollback awareness before changing runtime state.**
---
### 6. What changes in runtime

After deployment, the backend app service changes from:  
```
ghcr.io/sunil-9647/myapp:1.2.0
```

to:  
```
ghcr.io/sunil-9647/myapp:1.2.1
```

But important parts of the runtime should remain stable:  
- proxy route  
- DB volume  
- Compose structure  
- official scripts  
- rollback target record  
- release-history structure

#### Why this matters

A strong release changes only the intended thing. If the operator changes many unrelated runtime details at the same time, debugging and rollback become harder.


**A strong remote deployment updates the intended app artifact while keeping the rest of the runtime structure stable.**
---
### 7. VM verification after deployment

Deployment is not complete when deploy.sh finishes applying the update.

The VM must verify runtime truth.

A trusted verify.sh or operator checklist should check:  
1. service/container state  
2. public proxy route  
3. proxy logs  
4. app logs  
5. health endpoint  
6. dependency path

Example checks may include:  
```bash
docker compose ps
curl -f http://localhost:8080/health
docker compose logs --tail=50 proxy
docker compose logs --tail=50 api
```

#### Why this matters

CI/CD approval proves the artifact passed earlier stages.  
VM verification proves the artifact works in this actual runtime environment.

A release can still fail on the VM because of:  
- runtime config problem  
- proxy path problem  
- dependency issue  
- container startup issue  
- environment-specific behavior


**Remote deployment succeeds only after the VM verifies real runtime behavior.**
---
### 8. Successful deployment path

If verification passes, the deployment can be considered successful.

Successful signs include:  
- service is running  
- public route works  
- logs are acceptable  
- health endpoint passes  
- dependency path works  
- proxy route is healthy

Then the VM should write a release record.

Example:  
```
Date: 2026-04-24 18:00
Environment: production
Service: myapp
Previous image: ghcr.io/sunil-9647/myapp:1.2.0
New image: ghcr.io/sunil-9647/myapp:1.2.1
Digest: sha256:abc123...
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Verification: passed
Public route: http://localhost:8080
```

#### Why this matters

This record becomes operational evidence. Later, during debugging or audit, the team can see exactly what changed and what was verified.


**A successful remote deployment should leave behind exact release evidence.**
---
### 9. Failed deployment path

If verification fails, the VM should not pretend the release succeeded.

Failure symptoms may include:  
- public route returns 502  
- health check fails  
- app logs show missing config  
- dependency path is broken  
- proxy cannot reach backend  
- app is restarting or unhealthy

At that point, the operator or script should ask:  
```
Is rollback safer than experimenting in production?
```

If the previous image `1.2.0` was known-good, rollback may be the safest action.

#### Why this matters

A deployment failure should quickly move into controlled recovery thinking. Random fixes in production can make the incident worse.


**Failed VM verification should immediately trigger rollback thinking.**
---
### 10. Rollback execution on the VM

Rollback restores the exact previous known-good image.

The `.env` changes from:  
```
APP_IMAGE_TAG=1.2.1
```

back to:  
```
APP_IMAGE_TAG=1.2.0
```

The VM may conceptually run:  
```
/opt/myapp/scripts/rollback.sh 1.2.0
```

After rollback, verification must run again:  
- state  
- public route  
- logs  
- health  
- dependencies

#### Important correction

Rollback is not complete just because the old tag was restored.

Rollback is complete only when recovery is verified.


**Rollback is not just restoring the old image tag; rollback is verified recovery of the service.**
---
### 11. Rollback record

If rollback happens, the VM should write a rollback record.

Example:  
```
Date: 2026-04-24 18:12
Environment: production
Service: myapp
Failed image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback image: ghcr.io/sunil-9647/myapp:1.2.0
Reason: public route returned 502 after deployment
Rollback verification: passed
Public route: http://localhost:8080
```

#### Why this matters

This record explains:  
- what failed  
- what was restored  
- why rollback happened  
- whether recovery was verified

This helps future investigation and prevents the team from depending only on memory.


**Rollback records turn recovery actions into useful operational evidence.**
---
### 12. Full end-to-end remote deployment flow

The complete story is:  
```
Code change
  ↓
CI/CD validation
  ↓
Build exact Docker image
  ↓
Push to registry
  ↓
Capture tag and digest
  ↓
Verify staging
  ↓
Approve production
  ↓
Prepare deployment contract
  ↓
Trigger trusted deploy script on VM
  ↓
VM updates exact runtime image
  ↓
VM verifies public route and backend behavior
  ↓
Success record OR rollback and rollback record
```

#### Why this is strong

Because every stage has a clear responsibility:  
- CI/CD creates and approves the exact artifact  
- deployment contract communicates exact intent  
- VM applies the runtime change  
- verification proves runtime truth  
- rollback restores service if needed


**A strong remote deployment flow connects artifact identity, deployment handoff, VM execution, verification, and rollback into one disciplined system.**
---
### 13. Why deployment is not successful immediately after triggering deploy.sh

This was the checkpoint and it is very important.

Triggering `deploy.sh` only means:  
- the deployment process has started  
- the VM attempted to apply the runtime update

It does not prove:  
- the new image started correctly  
- the proxy route works  
- health checks pass  
- logs are clean  
- dependencies are reachable  
- users can use the service


**A deployment is successful only after verified runtime behavior, not immediately after the deployment command is triggered.**
---
### 14. Biggest lessons from Day-59 Part 4

The most important things I learned are:  
- CI/CD creates and approves the exact artifact  
- the VM should not rebuild the artifact  
- the deployment contract should include image, digest, rollback target, and verification route  
- CI/CD should trigger trusted VM-side scripts  
- `deploy.sh` should preserve rollback awareness before changing runtime state  
- runtime success must be verified on the VM  
- failed verification should trigger rollback thinking  
- rollback must restore the exact previous known-good image and verify recovery  
- release and rollback records are important operational evidence
---
### 15. Final understanding statement for Part 4

Today I learned one full end-to-end remote deployment story from CI/CD to Linux VM. A strong flow starts with CI/CD building and approving the exact Docker artifact, then preparing a precise deployment contract for the VM. The VM runs trusted deployment logic, updates the runtime image reference, verifies the public route and backend behavior, and writes a release record if successful. If verification fails, the VM rolls back to the exact previous known-good image and verifies recovery. This is how remote deployment becomes disciplined, traceable, and rollback-safe.

---
