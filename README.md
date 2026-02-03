# Project Name:  **ReleaseOps Mini** — End-to-end CI/CD + Promotion + Incident & Rollback drills using GitHub Actions

## DevOps CI/CD Pipeline with GitHub Actions (Production-Oriented)

### Project Overview

This repository demonstrates a **real-world CI/CD pipeline design using GitHub Actions**, built step-by-step with a **production mindset.**

The focus of this project is not just automation, but:  
+ Reliability  
+ Traceability  
+ Safe deployments  
+ Human-controlled releases  
+ Fast and confident rollback during incidents

This setup closely mirrors how CI/CD is implemented in **actual DevOps teams**, not just demos.

### Key Goals of This Project
+ Build once and deploy the same artifact across environments  
+ Separate CI (build & test) from CD (release & deploy)  
+ Enforce manual approvals for sensitive environments  
+ Enable fast rollback to a known good production version  
+ Follow real-world incident handling and monitoring mindset

### Repository Structure
```powershell
DevOps/
├── .github/
│   └── workflows/
│       ├── ci.yml                # Continuous Integration
│       ├── cd-dev.yml            # Deploy to DEV
│       ├── cd-staging.yml        # Deploy to STAGING (approval-based)
│       ├── cd-prod.yml           # Deploy to PROD (manual & controlled)
│       └── rollback-prod.yml     # Manual PROD rollback
│
├── cicd-learning/
│   └── ci-simulation/            # Build & artifact simulation
│
├── linux-learning/               # Linux fundamentals
├── git-learning/                 # Git & GitHub fundamentals
│
├── docs/
│   ├── architecture/             # CI/CD architecture & flow
│   ├── runbooks/                 # Incident handling guides
│   └── postmortems/              # Incident analysis documents
│
└── README.md
```

### CI/CD Flow (High Level)
**Continuous Integration (CI)**  
Triggered on every push to `main`.  
Steps:  
1. Lint shell scripts  
2. Build the application  
3. Run tests  
4. Package build artifact  
5. Upload artifact (`build-artifact`)

Important principle:  
>CI only builds and verifies.  
>CI does NOT deploy.

**Continuous Deployment (CD)**  
Each environment has its **own workflow**, all deploying the **same CI-built artifact**.  

**DEV Deployment**  
+ Fast feedback  
+ No approvals  
+ Used for early validation

**STAGING Deployment**  
+ Same artifact as DEV  
+ Requires manual approval  
+ Acts as a production-like gate

**PROD Deployment**  
+ Manual trigger only  
+ Requires explicit version input (example: `app-v-bf577b7`)  
+ No “latest” deployments  
+ Full control with traceability

### Promotion Model (Critical Concept)
This project follows **artifact promotion**, not rebuilds.
```
CI (build once)
   ↓
DEV  (same artifact)
   ↓
STAGING (same artifact)
   ↓
PROD (same artifact)
```

Why this matters:  
+ Prevents “works in staging but fails in prod”  
+ Enables confident rollback  
+ Preserves traceability

### Rollback Strategy (Production-Safe)
Rollback is implemented as a **separate manual workflow**:  
+ Operator selects a **previous known-good version**  
+ No rebuilding  
+ No code changes  
+ No guessing

Rollback principles used:  
+ Human decision under pressure  
+ Minimal steps  
+ Fast recovery  
+ Safety over speed

### Monitoring & Incident Mindset
This project follows a realistic incident response flow:
```
Monitor → Detect → Decide → Rollback → Fix → Redeploy
```

Key ideas:  
+ Not every signal is an alert  
+ Alerts should reflect real user impact  
+ Rollback is preferred over hot-fix during outages  
+ Postmortems are written after recovery, not during panic

### Runbooks
Runbooks document **what to do during incidents**, including:  
+ Deployment failures  
+ Artifact issues  
+ Rollback procedures  
+ Approval failures

Purpose:  
+ Reduce panic  
+ Speed up response  
+ Ensure consistent actions

### Postmortems
Postmortems document **what happened after incidents**, including:  
+ Timeline  
+ Root cause  
+ Impact  
+ Lessons learned  
+ Preventive actions

### Tools Used
+ Git & GitHub  
+ GitHub Actions  
+ Linux shell scripting  
+ Artifact-based deployments

No extra tools were added — focus is on **concept clarity**.
