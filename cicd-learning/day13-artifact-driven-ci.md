## Day 13 — Notes: Artifact-Driven CI (CI → CD Handshake)

### 1. What changed in Day-13 compared to Day-12?

In Day-12, my CI pipeline was mainly validating code using:  
+ lint checks  
+ build script execution  
+ test script execution  
+ log upload for debugging

In Day-13, I upgraded CI to **produce a real build output** and package it as a reusable artifact.  
This is important because CI is not only about running scripts—CI must deliver something useful that CD can deploy.  

---

### 2. Key Terminology (must be clear)

#### 2.1 Logs  
Logs are text outputs from build/test steps.  
+ Purpose: debugging, investigation, evidence  
+ Not reusable for deployment  
+ Not deployable  
Examples:  
+ build.log  
+ test.log

Logs are “supporting evidence”, not the main deliverable.

#### 2.2 Build Output  
Build output is the raw generated files produced during build.  
+ Typically stored in a folder like `dist/`, `target/`, or `build/`  
+ Exists only temporarily inside the CI runner unless saved/published  
+ Can be reused only if packaged properly  

In Day-13, I created build output in:  
+ `dist/app.txt`  
+ `dist/version.txt`  

#### 2.3 CI Artifact (main topic of Day-13)  
A CI artifact is a packaged, versioned output that is uploaded/stored outside the runner and can be downloaded later.  
+ Reusable  
+ Versioned  
+ Can be consumed by CD  
+ Stored by CI system (GitHub Actions artifacts, S3, Nexus, etc.)  

In Day-13, my CI artifact is:  
+ `ci-artifacts/app-build-<sha>.zip`  

#### 2.4 Deployment Artifact (next phase)  
Deployment artifact is what actually gets deployed to environments (dev/stage/prod).  
Often it is the same as CI artifact, but sometimes it is transformed (example: docker image, helm chart).  
We will handle this in later days.  

---

### 3. What makes a “good” CI artifact?

A good artifact must be:

#### 3.1 Deterministic  
Same commit → same output behavior.  
To support determinism, I clean old output before generating new output:  
+ `rm -rf dist`  
+ `mkdir -p dist`  

#### 3.2 Immutable  
Once created, the artifact should not be overwritten.  
If code changes, a new artifact must be created.  

#### 3.3 Versioned  
Artifact must include commit SHA/build number.  
Using commit SHA avoids “latest” confusion and enables rollback.  
In my scripts:  
+ `GITHUB_SHA` is used in CI  
+ locally, fallback is `local`  

Example artifact name:  
+ `app-build-<sha>.zip`  

### 3.4 Self-contained  
Artifact must contain everything needed to run/deploy without depending on CI runner state.  
For now, we simulate with `dist/` folder inside zip.  

#### 3.5 Reusable  
The same artifact should be deployable to multiple environments.  
Rule:  
> CI builds once. CD deploys many times.

---

### 4. Changes I implemented in Day-13

#### 4.1 Updated build.sh to generate build output  
My build script now:  
+ creates `dist/`  
+ writes application output file `app.txt`  
+ writes metadata file `version.txt` (commit + time)  
This is the first step toward real artifact generation.  

#### 4.2 Added package.sh to zip build output  
I created `package.sh` which:  
+ checks `dist/` exists  
+ creates folder `ci-artifacts/`  
+ zips `dist/` into `ci-artifacts/app-build-<sha>.zip`  

This is the real “artifact packaging” step.

#### 4.3 Updated GitHub Actions workflow to publish artifact  
In the **Build job** of GitHub Actions I added:  
+ Install zip package  
+ Run build.sh  
+ Run package.sh  
+ Upload build artifact using `actions/upload-artifact`  

Key point:  
- Artifact upload is done in the **build job**, not in test job.  
Because build job produces output; test job validates it.  

---

### 5. Why build artifact upload must be in Build job  
Build job responsibility:  
+ produce output  
+ package output  
+ publish output  

Test job responsibility:  
+ verify correctness  
+ upload test/debug logs if needed  

Even if tests fail, build artifact should still exist because it is produced by build step.  
Tests decide whether the artifact can move forward to deployment, but they do not create it.  

---

### 6. Evidence from CI run (What I verified)  
My workflow run shows:  
+ Lint job passed  
+ Build job passed  
  - install zip  
  - run build  
  - package artifact  
  - upload artifact  
+ Test job passed  
+ Artifacts count shows 1 in GitHub Actions  

This confirms CI is producing a reusable artifact.  

---

### 7. Files created/modified in Day-13  
+ `cicd-learning/ci-simulation/build.sh` (modified to create dist/)  
+ `cicd-learning/ci-simulation/package.sh` (new)  
+ `.github/workflows/ci.yml` (modified to upload build artifact)  

---

### 8. Key Takeaway of Day-13  
Day-13 taught me that:  
+ Logs are not the deliverable of CI  
+ A real CI pipeline must produce a reusable build artifact  
+ Artifacts are the handshake between CI and CD  
+ CI builds once; CD deploys many times  

---
