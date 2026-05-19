## Day 59 — Practical Remote Deployment Flow from CI/CD to Linux VM (Part 6)

### Objective of Day-59 Part 6

Today I closed the Day-59 remote deployment topic by converting the full learning into a practical checklist. The purpose of this part was to clearly understand the responsibility boundary between CI/CD and the Linux VM, and to define what a strong remote deployment flow should look like from artifact approval to runtime verification and rollback.

This topic is important because remote deployment is not just “pipeline runs command on server.” A strong deployment must preserve exact artifact identity, use a clear deployment contract, run trusted VM-side procedure, verify real runtime behavior, and keep rollback exact.
---
### 1. Responsibility boundary between CI/CD and Linux VM

#### CI/CD should own:
- code validation  
- Docker image build  
- image push to registry  
- tag and digest capture  
- staging verification  
- production approval  
- exact artifact decision

#### Linux VM should own:
- consuming exact approved image  
- applying runtime config  
- updating service  
- verifying runtime behavior  
- checking public route, logs, health, and dependencies  
- executing rollback if needed

**CI/CD owns artifact decision and approval, while the VM owns runtime application, verification, and rollback execution.**
---
### 2. Strong remote deployment flow

A strong flow is:  
```
Code change
  ↓
CI/CD validation
  ↓
Build exact Docker image
  ↓
Push image to registry
  ↓
Capture tag and digest
  ↓
Verify staging
  ↓
Approve production
  ↓
Prepare deployment contract
  ↓
Trigger trusted VM deploy script
  ↓
VM pulls exact approved image
  ↓
VM applies runtime update
  ↓
VM verifies public route, logs, health, dependencies
  ↓
Release record OR rollback and rollback record
```

**A strong remote deployment flow connects artifact identity, deployment handoff, VM execution, verification, and rollback into one controlled system.**
---
### 3. Deployment contract

A strong deployment contract should contain:  
```
Environment: production
Service: myapp
Approved image: ghcr.io/sunil-9647/myapp:1.2.1
Digest: sha256:abc123...
Current image: ghcr.io/sunil-9647/myapp:1.2.0
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Verify route: http://localhost:8080
```

#### Why this matters

The contract removes guesswork before the VM changes production runtime.


**The deployment contract makes the image, environment, rollback target, and verification expectation explicit.**
---
### 4. VM-side deployment checklist

#### Before deployment
- confirm current image  
- confirm target image  
- confirm rollback target  
- confirm current service is stable  
- confirm config is ready  
- confirm proxy/public route to verify

#### During deployment
- update controlled runtime image reference  
- pull exact approved image  
- apply service update  
- avoid unrelated changes

#### After deployment
- verify service state  
- verify public proxy-facing route  
- check proxy logs  
- check app logs  
- check health endpoint  
- check dependency path  
- write release record if successful

#### If failed
- restore rollback image  
- reapply service update  
- verify recovery  
- write rollback record

**Remote deployment must include pre-checks, controlled update, post-verification, and rollback path.**
---
### 5. Weak deployment patterns to reject

Reject processes that rely on:  
- rebuilding on the VM  
- deploying `latest`  
- VM choosing artifact identity  
- missing rollback target  
- random manual commands  
- skipping verification  
- checking only `docker ps`  
- no release records  
- mixing release with cleanup/config/proxy changes

**A DevOps engineer must reject deployment processes that leave artifact identity, rollback, execution, or verification unclear.**
---
### 6. Final understanding statement for Day-59

Today I learned how a practical remote deployment from CI/CD to a Linux VM should work. A strong flow starts with CI/CD building, pushing, verifying, and approving an exact Docker artifact. CI/CD then sends a rollback-aware deployment contract to the VM and triggers trusted VM-side deployment logic. The VM applies the exact approved image, verifies the real public route and backend behavior, records success, or rolls back to the exact previous known-good image and verifies recovery. This is disciplined remote deployment.

---
