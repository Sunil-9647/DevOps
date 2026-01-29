## Day 17 — Rollbacks, Versioning & Release Strategy

### 1. What is a Rollback and why it exists?  
A rollback means restoring the system to a previously known stable state when a deployment causes issues.  

Rollback exists because:  
+ Production failures are inevitable  
+ Fixing code during an outage is risky  
+ Business impact increases every minute  

In production, speed and predictability matter more than correctness.

So the first goal during an incident is:  
> Stabilize the system, not fix the bug

Rollback achieves this by reverting to a version that is already proven to work.

---

### 2. Rollback vs Hot-Fix (very important difference)  

**Hot-Fix (Not preferred during incidents)**  
+ Developer writes new code  
+ Code is rebuilt  
+ New artifact is generated  
+ New risks are introduced  
+ Takes time under pressure

**Rollback (Preferred)**  
+ Redeploy an already tested artifact  
+ No code change  
+ No rebuild  
+ Minimal risk  
+ Very fast

Industry rule:  
> During incidents → rollback first, fix later

---

### 3. Artifact-Based Rollback (core DevOps concept)  
Rollback is only possible because of artifacts.

An artifact is:  
+ The output of CI  
+ Built once  
+ Immutable (never changes)  
+ Versioned  
+ Stored safely

Because artifacts are immutable:  
+ The same artifact can be deployed again  
+ Dependencies do not change  
+ Behavior is predictable

Artifact-based rollback means:  
> Redeploying an older version of the same artifact that was previously stable

There is **no rebuild**, **no re-testing**, **no guessing**.

---

### 4. Artifact promotion and Rollback flow  
Typical artifact lifecycle:  
```mathematica
Build → Test → Artifact v1.0.0 → Deploy → Stable
Build → Test → Artifact v1.1.0 → Deploy → Failure
```

Rollback flow:  
1. Identify last stable version (v1.0.0)  
2. Fetch that artifact  
3. Deploy it to the same environment  
4. Restart or reload the service  
5. Verify health checks  
The artifact does not change, only the active version does.

---

### 5. Why Versioning is mandatory (Non-Negotiable)  
Without versioning:  
+ You don’t know what is deployed  
+ You can’t identify rollback targets  
+ You can’t audit incidents  
+ You can’t trace bugs

Names like:  
+ latest  
+ final  
+ prod-build  

are **dangerous** and **unprofessional**.

Versioning gives:  
+ Clear identification  
+ Traceability  
+ Safe rollback  
+ Accountability

No production system should exist without versioning.

---

### 6. Semantic Versioning (Industry Standard)  
Semantic versioning format:  
```
MAJOR.MINOR.PATCH
```

**PATCH** (e.g., 1.0.1)  
+ Bug fixes only  
+ No behavior change  
+ Lowest risk  
+ Best rollback candidate

**MINOR** (e.g., 1.1.0)  
+ New features  
+ Backward compatible  
+ Moderate risk

**MAJOR** (e.g., 2.0.0)  
+ Breaking changes  
+ Migrations required  
+ Rollback may be complex  

Understanding this helps DevOps engineers judge **rollback feasibility during incidents**.

---

### 7. Deployment vs Release (common confusion)  
**Deployment**  
+ Technical action  
+ Code is deployed to servers  
+ Can be automated  
+ Happens frequently

**Release**  
+ Business decision  
+ Features exposed to users  
+ Includes communication, approvals, and monitoring  
+ Happens cautiously

You can:  
+ Deploy without releasing (feature flags)  
+ Release without redeploying (config toggle)  

This separation reduces risk.

---

### 8. Release strategy (how companies stay safe)  
A proper release always includes:  
1. Version number  
2. Rollback plan  
3. Deployment window  
4. Monitoring readiness  
5. On-call ownership  
If rollback is not defined:  
> Release must be blocked

This is standard practice in organizations.

---

### 9. Incident Handling flow (Real-World)  
Standard production incident lifecycle:  
1. Alert triggered  
2. On-call engineer acknowledges  
3. Impact assessed  
4. Rollback executed  
5. Service stabilized  
6. Root cause analysis  
7. Permanent fix planned  
Key principle:  
> Rollback first, analyze later

Debugging during instability increases damage.

---

**How to use these Notes**:  
+ Read at least twice  
+ Revisit before interviews  
+ Apply mindset in future pipeline design

---
