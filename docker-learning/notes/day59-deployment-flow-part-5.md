## Day 59 — Practical Remote Deployment Flow from CI/CD to Linux VM (Part 5)

### Objective of Day-59 Part 5

Today I learned how to identify and reject weak remote deployment patterns like a real DevOps engineer. The purpose of this part was to understand that knowing the correct deployment flow is not enough. I must also be able to review bad deployment processes and clearly explain why they are unsafe.

A strong remote deployment flow should preserve exact artifact identity, use trusted deployment procedure, verify runtime behavior, and keep rollback clear before the release starts.

This topic is important because in real jobs, I may see weak practices such as:  
- rebuilding on the server  
- deploying `latest`  
- relying on manual commands  
- skipping verification  
- not knowing rollback target  
- mixing many unrelated changes together

A DevOps engineer should not blindly accept those patterns.
---
### 1. Weak pattern: copying source code to the VM and rebuilding there

A weak deployment process is:  
```
CI/CD passes
Developer copies source code to VM
VM rebuilds Docker image
VM deploys locally built image
```

This is weak because production may not run the same artifact that CI/CD tested and approved.

Possible differences can happen because of:  
- different build context  
- different local files  
- different dependency state  
- different build-time values  
- different environment assumptions

**Stronger pattern**  
```
CI/CD builds exact image
CI/CD pushes image to registry
VM pulls exact approved image
VM deploys that image
```


**The VM should consume the CI/CD-built artifact, not rebuild source code during deployment.**
---
### 2. Weak pattern: deploying latest

A weak deployment instruction is:  
```
Deploy latest to production
```

This is weak because latest is a moving label. It does not clearly identify:  
- exact image  
- exact commit  
- exact digest  
- exact staging-tested artifact  
- exact rollback relationship

**Stronger pattern**  
```
Deploy: ghcr.io/sunil-9647/myapp:1.2.1
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Digest: sha256:abc123...
```

**Production deployment should use exact image identity, not vague moving labels.**
---
### 3. Weak pattern: random manual commands instead of trusted scripts

A weak server deployment is:  
```
SSH into server
Type commands from memory
Edit .env manually
Run docker compose commands manually
Check something quickly
```

This is weak because manual commands can differ every time.

Risks include:  
- missing steps  
- editing wrong files  
- skipping verification  
- not recording rollback target  
- inconsistent behavior between deployments

**Stronger pattern**  

Use trusted scripts:  
```
/opt/myapp/scripts/deploy.sh 1.2.1
/opt/myapp/scripts/verify.sh
/opt/myapp/scripts/rollback.sh 1.2.0
```

**Remote deployment should use repeatable trusted procedure, not operator memory.**
---
### 4. Weak pattern: skipping runtime verification

A weak release process says:  
```
deploy.sh completed
deployment successful
```

This is wrong because command completion does not prove runtime success.

It does not prove:  
- container is healthy  
- proxy path works  
- logs are acceptable  
- app reaches DB  
- user-facing route is usable

**Stronger pattern**  
After deployment, verify:  
- state  
- logs  
- health  
- public route  
- dependency path

**Deployment is successful only after verified runtime behavior.**
---
### 5. Weak pattern: no rollback target before deployment

A weak release starts like:  
```
Deploy first
If it fails, we will figure rollback later
```

This is dangerous because rollback decisions made during failure are slower and less reliable.

**Stronger pattern**

Before deployment, record:  
```
Current image: ghcr.io/sunil-9647/myapp:1.2.0
New image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
```


**Rollback target must be known before deployment starts.**
---
### 6. Weak pattern: mixing release with cleanup, config, proxy, or permission changes

A weak operator may do this in one session:  
```
Deploy new app image
Clean old Docker images
Edit proxy config
Change .env values
Fix permissions
Delete old files
```

This is risky because if something fails, the cause becomes unclear.

Possible causes could be:  
- new image  
- cleanup  
- config edit  
- proxy change  
- permission change

**Stronger pattern**

Separate activities:  
- release image update = one event  
- cleanup = separate event  
- proxy config change = separate event  
- permission fix = separate event

**Strong operations keep change scope small and controlled.**
---
### 7. Weak pattern: VM decides what to deploy

A weak process is:  
```
VM pulls newest image
VM decides what version to run
Operator checks registry manually
```

This is weak because the VM should not invent release identity.

**Stronger pattern**

CI/CD sends deployment contract:  
```
Approved image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Verify route: http://localhost:8080
```

Then the VM applies that exact contract.


**The VM should execute approved release intent, not decide release identity.**
---
### 8. Weak pattern: no release or rollback records

A weak process says:  
```
Deployment worked. No need to record.
```

This is weak because later nobody can clearly know:  
- what image was deployed  
- what image was replaced  
- what verification was done  
- what rollback target was known  
- what failed if rollback happened

**Stronger pattern**

Write release records and rollback records.

A release record should include:  
- previous image  
- new image  
- rollback target  
- verification result  
- public route checked

**Release and rollback records preserve operational memory.**
---
### 9. Weak pattern: only checking docker ps

A weak verification process says:  
```
docker ps shows running
deployment is good
```

This is weak because docker ps only shows basic container state.

It does not prove:  
- app health  
- endpoint behavior  
- proxy forwarding  
- DB connectivity  
- user-facing success

**Stronger pattern**  

Check:  
- `docker compose ps`  
- logs  
- health endpoint  
- public proxy path  
- dependency path

**A running container is not the same as a working service.**
---
### 10. Professional rejection statement

A strong DevOps engineer should be able to say:  
```
I reject this deployment approach because it does not preserve exact artifact identity, does not provide rollback clarity, and does not prove runtime success.
```

Another strong version:  
```
I reject weak deployment processes that break artifact identity, use moving tags, skip rollback preparation, rely on ad hoc commands, or treat command completion as deployment success. A production deployment must use the exact approved artifact, have a known rollback target, run through trusted procedure, and prove success through runtime verification.
```

**A DevOps engineer should reject unsafe deployment patterns with clear technical reasoning.**
---
### 11. Practical review checklist for remote deployment

When reviewing any remote deployment process, ask:  
1. Is the image exact?  
2. Was it built by CI/CD?  
3. Was it pushed to registry?  
4. Was it approved/promoted properly?  
5. Does the VM receive exact artifact identity?  
6. Is rollback target known before deployment?  
7. Does the VM use trusted deploy scripts?  
8. Is runtime verification mandatory?  
9. Is public route checked?  
10. Are release and rollback records written?

If many answers are “no,” the deployment process is weak.
---
### 12. Final understanding statement for Part 5

Today I learned how to recognize and reject weak remote deployment patterns. A weak deployment process leaves artifact identity, rollback, execution, or verification unclear. A strong remote deployment uses the exact CI/CD-approved artifact, avoids moving tags like latest, triggers trusted VM-side scripts, verifies real runtime behavior, records release evidence, and keeps rollback target known before production changes begin.

---
