## Day 59 — Practical Remote Deployment Flow from CI/CD to Linux VM (Part 1)

### Objective of Day-59 Part 1

Today I learned what remote deployment means in a Docker-based CI/CD flow and why the Linux VM should receive exact artifact identity from CI/CD instead of rebuilding from source again. The goal was to understand how release responsibility should be divided clearly between CI/CD and the target VM.

This topic is important because many weak deployment models mix responsibilities between pipeline and server. That makes artifact identity weaker and production behavior less trustworthy.

### 1. What remote deployment means

Remote deployment means the exact artifact is prepared in one place and then made to run in another place.

In this learning flow:  

- CI/CD prepares the exact Docker artifact  
- the Linux VM applies that artifact in runtime


**Remote deployment is the bridge between artifact preparation and runtime application on the target VM.**

### 2. Different responsibilities of CI/CD and the Linux VM

A stronger model gives each side a clear responsibility.

#### CI/CD should:
- validate code  
- build image once  
- push exact image  
- record exact tag and digest  
- approve the artifact for deployment

#### Linux VM should:
- consume the exact approved artifact  
- apply runtime config  
- update the running service  
- verify runtime behavior  
- support rollback

**CI/CD should prepare and approve the artifact, while the Linux VM should only consume and run it correctly.**

### 3. What exact information should be handed to the VM

The Linux VM should receive deployment information such as:  

- exact image reference  
- exact digest if available  
- environment context  
- rollback target

For example:  
- image: `ghcr.io/sunil-9647/myapp:1.2.1`  
- digest: `sha256:abc123...`  
- rollback target: `ghcr.io/sunil-9647/myapp:1.2.0`

**The VM should receive exact approved artifact identity by reference, not vague deployment instructions.**

### 4. Why rebuilding on the VM is still wrong

Rebuilding on the VM is weak because:  

- the VM may run a different artifact than CI tested  
- rollback clarity becomes weaker  
- traceability becomes weaker  
- the build-once, promote-the-same-artifact rule breaks

**Remote deployment should move exact artifact identity to the VM, not move build responsibility to the VM.**

### 5. What artifact handoff by reference means

Artifact handoff by reference means the VM is told:  

- exactly which image to run

It is not given:  

- source code for rebuild  
- local build responsibility  
- vague release guessing

**The VM should be told exactly what to run, not asked to recreate what to run.**

### 6. Why this makes deployment safer

Exact image-reference handoff makes the deployment side:  

- smaller  
- clearer  
- easier to reason about  
- easier to roll back  
- less dependent on accidental local differences


**Exact artifact reference makes remote deployment simpler and safer.**

### 7. Final understanding statement for Part 1

Today I learned that in a stronger remote deployment flow, CI/CD builds and approves the exact Docker artifact, and the Linux VM receives that artifact identity by reference and applies it in runtime. This preserves traceability, release confidence, and rollback clarity because the VM is consuming the tested artifact instead of rebuilding a new one.

---
