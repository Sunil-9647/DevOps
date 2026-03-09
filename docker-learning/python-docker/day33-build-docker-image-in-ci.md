## Day 33 Notes 04 —Build Docker image in CI and publish to a registry (GHCR)

### 0) Day-33 Goal (what we wanted by end of the day)

By the end of Day-33, we should be able to:  
> “Whenever I push code, GitHub Actions can build my Docker image automatically, tag it with a traceable version, and publish it to a real registry (GHCR), so later I can pull the exact same image anywhere.”

---

### 1) What we built in Day-33 (high-level)
We created **two separate workflows** (this separation is important in real companies):

#### A) Docker Image CI (Validation) — runs on Pull Requests
Purpose: **prove the Docker image can build** (and optionally run smoke checks) before code is merged.  
+ Trigger: `pull_request` to `main`  
+ Typical action: build image (no push)  
+ Why: PR code is not “final”; we don’t want to publish “untrusted / unapproved” images.

#### B) Publish to GHCR (Release) — runs on Push to main
Purpose: after merge, **publish an image** to GHCR so it becomes a versioned artifact.  
+ Trigger: **push** to **main**  
+ Action: build + push  
+ Output: image available at `ghcr.io/<username>/<image>:<tag>`

This design prevents confusion and keeps your pipeline clean: **PR validates, main publishes.**

---

### 2) Core theory (must understand before YAML)

#### 2.1 What is a “registry” and why do we publish images?
A Docker registry (like GHCR, Docker Hub, AWS ECR) is basically an artifact warehouse for container images.

Why we publish:  
+ Our laptop is not production.  
+ We want the same image to run on:  
    - our system,  
    - staging VM,  
    - production server,  
    - Kubernetes cluster.  
+ A registry becomes the **single source of truth** for the built image.

In CI/CD language:  
+ Source code → CI builds artifact  
+ For containers, that artifact is the Docker image (not a zip file).

#### 2.2 Why GitHub Actions needs permissions for GHCR
Publishing to GHCR is not “free”. GitHub Actions must be allowed to push packages.

So we set in the publish workflow:  
+ `contents: read` → can read repository code  
+ `packages: write` → can push to GHCR

Without `packages: write`, your workflow will fail during push (permissions/auth error).

#### 2.3 Tagging: why we used `sha-<shortsha>`
A tag is a human-friendly label pointing to an image.

We used:  
+ `sha-<shortsha>` (example: `sha-2435712`)

Because:  
+ It is traceable back to the exact Git commit.  
+ It is unique per change.  
+ It helps rollback: we can redeploy **the exact build**.

Important truth:  
+ Tags are pointers; they **can be moved**.  
+ That’s why later we also discussed digests (`@sha256:...`) as truly immutable.

But for Day-33, the key was: **use a unique version tag, not only** `latest`.

#### 2.4 Why we added `paths:` filters
We restricted workflow execution to only run when files inside the FastAPI Docker lab change.

Reason:  
+ Saves CI minutes.  
+ Avoids noisy runs.  
+ Real-world pipelines always filter triggers to reduce cost and confusion.

---

### 3) Practical implementation we did (YAML explained line-by-line)

#### 3.1 Publish workflow: `.github/workflows/publish-py-api-ghcr.yml`
This is our actual “publish to registry” workflow (our current file structure).

**Trigger**

```YAML
on:
  push:
    branches: ["main"]
    paths:
      - "docker-learning/labs/python-fastapi-dockerfile/**"
      - ".github/workflows/publish-py-api-ghcr.yml"
  workflow_dispatch:
```

Meaning:  
+ On push to `main`, run only if that lab folder or the workflow file changes.  
+ `workflow_dispatch` allows manual runs (useful for testing).

**Permissions**

```YAML
permissions:
  contents: read
  packages: write
```

Meaning:  
+ Read repo code.  
+ Push image to GHCR.

**Login step**

```YAML
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

Meaning:  
+ Uses GitHub’s built-in token to authenticate.  
+ No separate “GHCR account” is needed; GHCR is part of GitHub Packages.

**Tag generation (docker/metadata-action)**

```YAML
- name: Docker metadata (tags/labels)
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ${{ env.IMAGE_NAME }}
    tags: |
      type=sha,format=short
      type=raw,value=latest,enable={{is_default_branch}}
```

Meaning:  
+ Automatically generates:  
    - `:sha-<shortsha>` (example `sha-2435712`)  
    - `:latest` only for default branch  
+ This avoids you manually typing versions.

**Build and push (actual publishing)**

```YAML
- name: Build and push (TARGET=prod)
  uses: docker/build-push-action@v6
  with:
    context: docker-learning/labs/python-fastapi-dockerfile
    push: true
    build-args: |
      TARGET=prod
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

Meaning:  
+ Builds using the Dockerfile in that folder.  
+ Pushes to GHCR.  
+ Tags include sha tag and latest tag (as configured above).  
+ `TARGET=prod` is your build-time switch (so prod dependencies get installed).

#### 3.2 Why we kept PR CI workflow separate
Workflows ran separately and had different “versions/tags”.

That’s expected if we have:  
+ PR workflow (CI build only)  
+ Main branch workflow (publish)

This prevents confusion:  
+ PR run = validation only  
+ Push to main = official image published

---

### 4) How to verify the result

After publish succeeds:  

**A) Verify in GitHub UI**  
+ Repo → Packages  
+ Find your package name (example: `devops-py-api`)  
+ You should see tags like:  
    - `sha-xxxxxxx`  
    - `latest`

**B) Verify via terminal (proof)**  
Pull the exact version:  
```bash
docker pull ghcr.io/sunil-9647/devops-py-api:sha-2435712
```

Then run:  
```bash
docker run --rm -p 8080:8000 ghcr.io/sunil-9647/devops-py-api:sha-2435712
```

This proves:  
+ the registry image works,  
+ and you can run it on a clean machine.

---

### 5) Common mistakes we avoided (and why they matter)

**Mistake 1: Publishing on PR**  
Bad because:  
+ PR code may be broken or unreviewed.  
+ You will pollute registry with junk images.

Correct: PR builds only; main publishes.

**Mistake 2: No `packages: write`**  
Publish fails because GitHub Actions cannot push packages.

**Mistake 3: No `paths:` filter**  
Everything triggers everything. In real orgs, this creates cost + noise + confusion.

**Mistake 4: Relying only on latest**  
“latest” is not a version. It’s a moving pointer.  
For rollback and debugging, sha tags are far safer.

---
