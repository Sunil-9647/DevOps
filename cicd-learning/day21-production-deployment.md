## Day 21 — Production Deployment, Promotion & Rollback (GitHub Actions)

### Core objective:
The goal of Day-21 is to design a **safe, traceable, and controlled production release flow** using GitHub Actions, focusing on:  
+ Artifact immutability  
+ Environment promotion  
+ Manual production release  
+ Reliable rollback

---

### Key Principle: Artifact Promotion (most important)

#### Promotion means transferring the same artifact across environments.
+ CI builds the artifact once  
+ The same artifact is deployed to:  
   - DEV  
   - STAGING  
   - PROD  
+ No rebuilds happen in CD workflows

This ensures:  
+ What is tested is exactly what is released  
+ Rollback is predictable  
+ No environment drift

---

### CI vs CD responsibility split
**CI (Technical Dependency)**  
CI is responsible for:  
+ Linting  
+ Building  
+ Testing  
+ Packaging  
+ Uploading the artifact  

CI pipeline stages:
```bash
lint → build → test → package → upload artifact
```
If any stage fails, the workflow stops immediately.

**CD (Release Decision Dependency)**
CD workflows are not a single pipeline.  
Each environment:  
+ DEV  
+ STAGING  
+ PROD

**independently depends on the CI artifact**, not on each other.  
This separation allows:  
+ Controlled promotion  
+ Manual approvals  
+ Flexible rollback

---

### Environment strategy used
**DEV**  
+ Fast feedback  
+ No approvals  
+ Can deploy many times a day  
+ Used for developer validation

**STAGING**  
+ Production-like environment  
+ Requires human approval  
+ Used to validate release readiness  
+ Uses artifact selected from CI

**PROD**  
+ Fully manual trigger  
+ Requires explicit version input  
+ High safety and control  
+ Supports rollback to known-good version

---

### Artifact naming & identity (clarified)

| **Term**         | **Meaning**                               |
| ---------------- | ----------------------------------------- |
| Artifact name    | Logical container name (`build-artifact`) |
| Artifact zip     | Actual file (`app-v-xxxxxxx.zip`)         |
| Artifact ID      | GitHub internal database ID               |
| Artifact version | Derived from commit SHA                   |

**Production deployment uses artifact version, not artifact ID**.

---

### Why `PROD` does not use “Latest”?
Using **latest** is unsafe because:  
+ It may not be tested  
+ It breaks traceability  
+ Rollback becomes guesswork  
+ PROD bugs appear without confidence

Instead:  
+ PROD deploys explicit version  
+ Example input: `app-v-bf577b7`

---

### Rollback strategy implemented
Rollback is:  
+ Manual  
+ Version-based  
+ Human-controlled

Why manual rollback:  
+ Rollback is a business decision  
+ Human chooses the safest known-good version  
+ Prevents automated rollback to wrong versions

Rollback uses the **same artifact mechanism** as deploy.

---

### Why rebuilds in `PROD` are dangerous?
Bad approach:
```
DEV → rebuild
STAGING → rebuild
PROD → rebuild
```
This causes:  
+ Different binaries in each environment  
+ STAGING tests one thing, PROD runs another  
+ Bugs appear only in production

Correct approach:
```
CI → build once → promote same artifact
```

---

### Production safety achieved
With the Day-21 setup:  
+ No rebuilds in PROD  
+ Clear version visibility  
+ Fast rollback  
+ Approval-based release  
+ Strong audit trail

---
