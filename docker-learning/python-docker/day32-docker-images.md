## Day 32 Notes 04 — CI for Docker Images (FastAPI)

### 0) What we were trying to achieve (goal of Day-32)
Until now we were building/running your FastAPI Docker image on our laptop. That is not enough in a real DevOps team.

**Day-32 objective**:  
Create a **GitHub Actions CI workflow** that automatically checks your Docker image whenever you raise a **Pull Request**, so you catch Dockerfile/app problems **before merge**.

In simple words:  
> “If the Docker image cannot build + cannot start + basic API is not responding, PR must fail.”

That is Docker Image CI.

---

### 1) Why “CI for Docker images” is required in real companies
Many juniors think: “My Python code is correct, so deployment will work.” Wrong.

In production, failures happen because of:  
+ wrong Dockerfile COPY paths  
+ missing dependencies in requirements  
+ wrong CMD/ENTRYPOINT  
+ port mismatch (8000 inside vs published port)  
+ broken healthcheck  
+ image builds but container fails at runtime  
+ “works locally” but fails in clean runner

So the pipeline must validate the packaging, not only the code.

**Correct DevOps thinking:**  
+ Code + Dockerfile + build context + runtime command = one unit.  
+ If that unit is broken, you stop it at PR stage.

---

### 2) What we implemented in Day-32 (exactly)
We created a separate GitHub Actions workflow for Docker image CI.  
+ **Workflow file**: `.github/workflows/docker-image-ci.yml`  
+ **Trigger**: `pull_request` (not push to main)  
+ **Path filter**: only run when files in the FastAPI docker lab change  
(so the workflow doesn’t run for unrelated commits and you don’t get confused by extra runs)

**Main actions in this workflow:**  
1. Checkout repository  
2. Set up Docker Buildx (so we can build images in GitHub runner properly)  
3. Build the Docker image from your lab folder (Dockerfile)  
4. Ensure the built image is usable for the next step (important detail: load vs cache)  
5. Run a container from the built image  
6. Perform a smoke test (curl the root endpoint)  
7. If smoke test fails → workflow fails (PR blocked)

---

### 3) Theory: Buildx “cache vs load”
When GitHub Actions builds an image using Buildx, **the image does not automatically appear in** `docker images` inside the runner.

So if you do:  
+ build with buildx  
+ then `docker run myimage:tag`

It can fail with “image not found”.

**Why?**  
Because Buildx can store the output in its internal build cache, but Docker engine doesn’t “see” it unless you explicitly export it.

**What we learned (very important)**

If our workflow wants to **run the image after building**, then in the build step we must ensure one of these:  
+ Option 1 (CI build only, then run): `load: true`  
   This loads the image into the local Docker engine on the runner, so `docker run` works.  
+ Option 2 (build then push): `push: true`  
   This pushes to registry; then you can pull/run. (But Day-32 CI is PR-based, so normally we do NOT push.)

So Day-32 learning is:  
> “In PR CI, we build and test locally in runner. Therefore we need `load: true`.”

---

### 4) Theory: Why smoke test is mandatory in Docker image CI
A Docker image can build successfully, but the app can still be broken:  
+ app starts and exits immediately  
+ wrong command  
+ wrong port  
+ runtime crash

So in Day-32, we did smoke test.

**Smoke test meaning** (importance):  
+ Start container  
+ hit one endpoint (like `/`)  
+ expect HTTP 200  
+ if not 200, fail CI

This is the cheapest, fastest proof that:  
+ container started correctly  
+ uvicorn is listening  
+ API responds

---

### 5) Practical flow (what the CI runner does step-by-step)
This is the exact flow our CI follows logically:

#### Step A — PR created / updated
GitHub triggers the workflow because:  
+ event is `pull_request`, and  
+ files changed match our lab path filter

#### Step B — Build image in runner
Runner builds image from:  
+ `context: docker-learning/labs/python-fastapi-dockerfile`  
+ Dockerfile inside that folder  
+ it uses the pinned Python base image we defined

#### Step C — Make image runnable
We ensure the image becomes available for `docker run` (key learning: **load**).

#### Step D — Run container for testing
Runner starts the container (mapped to a known port).  
Then we do the smoke curl.

#### Step E — CI verdict
+ curl success ⇒ job success ⇒ PR can be merged  
+ curl failure ⇒ job fails ⇒ PR blocked

That is real CI behavior.

---

### 6) Why we used paths: filter (understanding)
If in future we change anything under the FastAPI docker lab path, the workflow must trigger.  
If we change unrelated files, it should not trigger.  

Result:  
+ fewer unnecessary runs  
+ less confusion  
+ faster feedback

---

### 7) Mistakes we encountered (and the real debugging habit)

#### Mistake type 1: “Image built but cannot run”
Root cause: build output not loaded into Docker engine in runner.  
Fix: ensure build step exports image (`load: true`) for PR CI.

#### Mistake type 2: “Workflow seems to run twice”
This happens when you have multiple workflows with overlapping triggers:  
+ one runs on `push`  
+ one runs on `pull_request`

Day-32 discipline: keep Docker image CI strictly on PR, so it behaves like a quality gate.

---

### 8) What we should keep in GitHub (what to commit)
For Day-32, we should commit:  
+ `.github/workflows/docker-image-ci.yml`  

That is the actual “deliverable” of Day-32.  
(Notes are separate, but workflow file is the real engineering output.)

---

### 9) Day-32 checklist (self-verify)
+ PR triggers docker image CI  
+ workflow builds image from correct context  
+ workflow runs container successfully  
+ curl to root endpoint returns HTTP 200  
+ failing endpoint causes CI fail (PR blocked)  

---
