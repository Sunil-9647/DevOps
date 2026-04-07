## Day 53 — Single-Host Deployment Workflow and Release Runbook (Part 1)

### Objective of Day-53 Part 1

Today I learned how to think about releasing and updating a Dockerized service on a single host in a disciplined way. The goal was not just to “run a new container,” but to understand what must be checked before deployment, what should be verified after deployment, and why rollback planning must exist before the release starts.

This topic is important because many Docker users can start containers, but real DevOps work requires repeatable release procedures, not memory-based updates.

---

### 1) What a release runbook is

A release runbook is a documented step-by-step procedure for deploying or updating a service. It should define:  
- what to check before release  
- what exact image is being deployed  
- what commands or actions are needed  
- what success looks like  
- how to verify the service after release  
- what to do if rollback is needed

**Main lesson**

Without a runbook, releases become inconsistent, person-dependent, and risky.

---

### 2) Why single-host release discipline still matters

Even on a single Docker host, a bad release can cause:  
- downtime  
- wrong image deployment  
- config mistakes  
- persistence problems  
- unclear rollback  
- confusing troubleshooting

**Main lesson**

Single-host Docker still needs release discipline. It is not safe to rely only on memory or quick manual restarts.

---

### 3) First question before any release

The first release question must be:

**What exact image am I deploying?**

That means:  
- current running image should be known  
- target image should be known  
- rollback image should be known  
- exact version tag and preferably digest should be identified

**Main lesson**

Release and rollback both depend on exact image identity.

---

### 4) Pre-deploy checklist
Before updating a service, I should check:

#### A. Exact image identity
- what is running now?  
- what exact image will replace it?  
- what previous image can be rolled back to?

#### B. Scope of change
- image-only change?  
- config change?  
- mount/volume change?  
- network change?  
- schema/data change?

#### C. Runtime configuration
- required env vars present?  
- no empty required values?  
- config still correct?

#### D. Persistence safety
- volumes correct?  
- important data safe?  
- no accidental bind-mount risk?

#### E. Dependency readiness
- DB healthy?  
- proxy healthy?  
- dependent services stable?

#### F. Observability readiness
- know which logs to check  
- know which health endpoint to test  
- know which service endpoint to verify

#### G. Rollback readiness
- exact previous version known  
- rollback action clear  
- compatibility concerns considered

**Main lesson**

A safe release starts before the update, not after failure.

---

### 5) Safe update flow

A disciplined single-host update flow is:  
1. identify current and target image  
2. confirm config and persistence state  
3. pull or prepare the exact target image  
4. update the service in a controlled way  
5. check container state  
6. check logs  
7. check health  
8. verify actual service behavior  
9. verify dependency connectivity  
10. keep rollback ready until release is proven stable

**Main lesson**

A release is not complete when the container starts. It is complete when the service is verified.

---

### 6) Post-deploy verification checklist

After deployment, I should verify:  
- container state  
- logs  
- health status  
- actual application endpoint  
- dependency connectivity  
- expected mounted files/data visibility

**Main lesson**

“Container is running” is not enough to declare release success.

---

### 7) Why post-deploy verification must include real behavior

A service can be:  
- `Up`  
- but unhealthy  
- or misconfigured  
- or unable to reach DB  
- or failing behind proxy

So real verification must include:  
- actual endpoint checks  
- health checks  
- dependency path checks

**Main lesson**

Service behavior matters more than container liveness alone.

---

### 8) Rollback procedure mindset

Rollback planning must already exist before release starts.

A rollback runbook should define:  
- failed image identity  
- previous known-good image identity  
- config compatibility  
- rollback procedure  
- rollback verification steps

**Main lesson**

Rollback without exact image identity is weak and unreliable.

---

### 9) When rollback is safer than fixing forward

During a bad release, rollback is often safer when:  
- previous version is known-good  
- new version is clearly broken  
- root cause is not yet fully understood  
- service restoration matters more than experimenting live

**Main lesson**

Rollback is often safer than blind fix-forward during incident pressure.

---

### 10) Release documentation discipline

Each release should leave behind a small record containing:  
- date/time  
- service name  
- old image  
- new image  
- config changes if any  
- verification result  
- rollback target

**Main lesson**

Good release operations depend on written evidence, not memory.

---

### 11) Final understanding statement for Part 1

Today I learned that Docker deployment is not just about replacing containers. A real single-host deployment must begin with exact image identity, configuration and persistence checks, and rollback readiness. After deployment, success must be verified through logs, health, endpoint behavior, and dependency connectivity. This is how Docker usage becomes operational release discipline.

---

