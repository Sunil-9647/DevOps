## Day 19 — STAGING, Promotion & Release Governance

### Goal  
The goal of Day-19 is to understand **how software moves safely from DEV towards PROD**, without rebuilding or losing control.  
This day focuses on:  
+ Promotion vs deployment  
+ Role of STAGING  
+ Human approval gates  
+ Release governance  
+ Why CI and CD must be decoupled

---

### Why `DEV` is not enough?  
DEV environment exists for:  
+ Fast feedback  
+ Frequent deployments  
+ Developer experimentation  
+ Early validation

Characteristics of DEV:  
+ Unstable by nature  
+ Can break without business impact  
+ Configurations may differ from PROD  
+ Multiple deployments per day

Because of this:  
>DEV cannot be trusted for release decisions

A build working in DEV does not automatically mean it is safe for production.

---

### Why `STAGING` exists?  
STAGING is a **pre-production environment** whose purpose is to validate the **release**, not just the code.  
STAGING characteristics:  
+ Production-like configuration  
+ Same artifact as PROD  
+ Controlled deployments  
+ Human approval required

Key rule:  
>If it is not tested in STAGING, it has no right to go to PROD.

---

### `Deployment` vs `Promotion` (Core Concept)  
**Deployment**  
+ Technical act of installing software  
+ Happens when code/artifact is copied and started in an environment  
+ Can be automated

Example:  
+ Deploy artifact to DEV

**Promotion**  
+ Decision to move the same artifact to a higher environment  
+ No rebuild  
+ No code change  
+ Controlled and intentional

Example:  
+ Promote artifact from DEV → STAGING

Important rule:  
>Build once. Promote many times.

---

### Why rebuilding for `STAGING` is dangerous?  
If we rebuild for STAGING:  
+ A new artifact is created  
+ That artifact was not tested in DEV  
+ Hash/version changes  
+ Traceability breaks  
+ Rollback becomes unreliable

Worst-case scenario:  
+ DEV tested artifact A  
+ STAGING tested artifact B  
+ PROD runs artifact C

This leads to **production-only bugs**, which are hardest to debug.

---

### `CI` as the Source of Truth  
CI is responsible for:  
+ Building the code  
+ Running tests  
+ Creating immutable artifacts  
+ Producing versioned outputs

Artifacts belong to a **specific CI run**, identified by `run_id`.

Key rule:  
>Artifacts are promoted. Environments are not.

DEV, STAGING, and PROD all depend on **CI artifacts**, not on each other.

---

### Why `STAGING` depends on `CI`, not `DEV`?  
DEV can fail for reasons unrelated to artifact quality:  
+ Misconfiguration  
+ Broken secrets  
+ Experimental changes  
+ Temporary infra issues

If STAGING depended strictly on DEV success:  
+ One unstable DEV issue could block releases  
+ Hotfixes would be delayed

Correct model:  
+ CI provides the artifact  
+ DEV provides feedback  
+ Humans decide promotion to STAGING

---

### `Human approval` and governance  
STAGING requires approval because:  
+ It represents a release decision  
+ Someone must take responsibility  
+ Accidental deployments must be prevented  
+ Audit trail is required  
GitHub Environments provide:  
+ Approval gates  
+ Environment-specific secrets  
+ Deployment history  
+ Accountability (who approved what)

---

### STAGING workflow summary  
STAGING workflow characteristics:  
+ Triggered manually (`workflow_dispatch`)  
+ Requires CI `run_id`  
+ Downloads artifact from that CI run  
+ Uses `environment: staging`  
+ Waits for human approval  
+ Deploys without rebuilding

This is **true promotion**.

---

### Outcome of Day-19  
By the end of Day-19:  
+ Same artifact was deployed to DEV and STAGING  
+ Promotion was controlled and approved  
+ No rebuilds happened  
+ Release traceability was preserved

---
