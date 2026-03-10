## Docker Notes — GHCR Tags vs Digests (Immutable Deployments)

### What problem are we solving?
In production, we want deployments to be **deterministic** and **rollback-ready**.

If we deploy using a moving tag like `latest`, the same compose file can deploy different image content at different times.  
That makes incident response harder because you cannot guarantee what code is running.

So we avoid using `latest` in production deployments.

---

### Tag vs Digest (most important concept)

#### Tag (mutable pointer)
Example:  
- `ghcr.io/sunil-9647/devops-py-api:sha-2435712`  
- `ghcr.io/sunil-9647/devops-py-api:latest`  

A tag is a **human-friendly label**. But tags can be moved (reassigned) to a different image digest later.

#### Digest (immutable content ID)
Example:  
- `ghcr.io/sunil-9647/devops-py-api@sha256:<long-hash>`

A digest is **cryptographically stable**. It always points to the exact same image bytes.  
Even if someone changes tags, the digest reference stays correct.

---

### Our publish workflow gate (why it matters)
We updated the GHCR publish workflow to:  
1. Build the PROD image locally  
2. Run a smoke test against `/`  
3. Only if smoke test passes → push image to GHCR (update `sha-*` tag and `latest`)

This prevents broken builds (HTTP 500) from being published.

---

### Why `load: true` was needed in smoke test
In the smoke test workflow we use `docker run`.  
For `docker run` to work, the image must exist in the runner's local Docker engine.  
`load: true` loads the built image from Buildx into the local Docker engine without pushing.  

If we skip `load: true` and also do `push: false`, the smoke test fails because `docker run` cannot find the image.

---

### Production deployment rule we follow
- Dev can use tags for convenience.  
- Production should pin to an **immutable SHA tag** or, best, to an **image digest**.

#### Best practice
Pin PROD using digest:  
- `image: ghcr.io/sunil-9647/devops-py-api@sha256:...`

This ensures the exact same artifact is deployed every time.

---

### Quick checklist (real-world habit)
- ✅ Build passes
- ✅ Smoke test passes (HTTP 200 on `/`)
- ✅ Publish to GHCR
- ✅ Deploy PROD using pinned reference (tag/digest)
- ✅ Rollback plan: switch back to previous pinned version

---
