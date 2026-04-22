## Day 55 — Environment Promotion Flow and Release Discipline (Part 4)

### Objective of Day-55 Part 4

Today I learned how environment promotion appears inside a CI/CD pipeline. The main idea is that a strong promotion-aware pipeline should not stop at staging deployment. It should carry the same exact artifact identity forward through staging verification, production approval, production deployment, and production verification.

This is important because promotion is not only a technical deployment step. It is a release-control flow based on evidence.

---

### 1) A promotion-aware pipeline has multiple environment stages

A stronger promotion-aware pipeline can logically look like this:  
1. validate  
2. build_and_push  
3. deploy_staging  
4. verify_staging  
5. approve_production  
6. deploy_production  
7. verify_production

**A strong pipeline does not treat production as just another automatic deploy target. It creates a boundary between staging success and production release.**

---

### 2) Why approval belongs between staging and production

Approval should happen after staging verification and before production deployment.

At that point, the team can review:  
- exact image  
- exact digest  
- staging result  
- rollback target  
- production readiness

**Approval is the gate that asks whether the exact staging-tested artifact is allowed to move into production.**

---

### 3) What must flow forward during promotion

The exact following items should flow from staging toward production:  
- image reference  
- digest  
- release evidence

The pipeline should not rebuild the image or replace it with vague tags like `latest`.

**Promotion flow must carry exact artifact identity forward, not create new artifact identity later**.

---

### 4) What should remain unchanged during promotion

The following should remain unchanged between staging and production:  
- image tag for the release  
- digest  
- code inside image  
- built dependencies inside image


**If these change, the same tested artifact is no longer being promoted.**

---

### 5) What may differ between staging and production

The following may still differ:  
- environment target  
- runtime config  
- secrets  
- DB endpoint  
- hostname  
- approval requirement  
- rollback target  
- verification strictness

**The image stays the same, but runtime environment details may differ.**

---

### 6) Why production still needs verification

Even if staging passed, production must still be verified because:  
- production config may differ  
- production secrets may differ  
- production runtime conditions may differ

**Staging reduces risk, but production still requires its own verification stage.**

---

### 7) Promotion flow is also evidence flow

A promotion-aware pipeline should carry forward:  
- exact artifact identity  
- staging verification result  
- approval state  
- rollback target  
- release notes or promotion record

**Promotion is not just moving software; it is also moving release evidence forward.**

---

### 8) Final understanding statement for Part 4

Today I learned that a strong promotion-aware pipeline extends beyond staging deployment. It preserves exact image identity, verifies the artifact in staging, places an approval boundary before production, and then deploys the same exact artifact into production followed by production verification. This is how environment promotion becomes disciplined release control instead of casual deployment.

---

## Day-55 — Environment Promotion Flow and Release Discipline (Part 5)

### Objective of Day-55 Part 5

I learned how rollback discipline should be handled after production promotion. The main idea is that production promotion and production rollback must be planned together. Before the new image is deployed to production, the exact previous production artifact and rollback target should already be known and recorded.

This is important because rollback becomes much weaker if teams begin deciding recovery only after a production failure has already started.

---

### 1) Promotion and rollback must be planned together

A stronger release process does not separate production promotion and rollback planning. Before production deployment starts, the team should already know:  
- current production image  
- new production image  
- rollback target  
- rollback verification path

**Rollback planning must exist before production promotion begins.**

---

### 2) Previous production image is the most important rollback target

The most common rollback target is the exact previous production-known-good artifact.

Example:  

- previous production image: `ghcr.io/sunil-9647/myapp:1.2.0`  
- new promoted image: `ghcr.io/sunil-9647/myapp:1.2.1`

**Rollback should use the exact previous production artifact, not vague memory like “some older stable version.”**

---

### 3) Rollback target should be recorded before production changes

Before promoting a new image to production, a strong release record should capture:

- previous production image  
- previous production digest if available  
- new promoted image  
- new promoted digest  
- rollback target

**Rollback target should be recorded before failure happens, not reconstructed during panic.**

---

### 4) Rollback should be considered when release safety is lower than previous state

Rollback becomes a strong option when:  
- production verification fails  
- health checks fail  
- critical endpoint fails  
- dependency connectivity breaks  
- user impact appears  
- the new release is clearly less safe than the previous known-good state

**Rollback is a safety action to restore service stability, not something to avoid out of pride.**

---

### 5) Production rollback is environment-specific

Rollback target for production must be based on:  
- what production was actually running before the new promotion

It should not be confused with:  
- staging image history  
- staging rollback target

**Each environment needs its own rollback identity tracking.**

---

### 6) Weak rollback patterns to avoid

Weak rollback patterns include:  
- rebuilding image again  
- guessing older tags  
- using `latest`  
- saying “roll back to something stable”  
- ignoring exact digest and artifact identity

**Strong rollback must use exact previous production artifact identity.**

---

### 7) Rollback also needs verification

After rollback, the team should still verify:  
- container state  
- logs  
- health  
- endpoint behavior  
- dependency connectivity

**Rollback is only successful when service behavior is restored, not just when an older image is redeployed.**

---

### 8) Final understanding statement for Part 5

I learned that production rollback discipline must be treated as part of production promotion planning. The most important rollback target is the exact previous production-known-good artifact, and it should be recorded before the new release is deployed. Strong rollback is exact, environment-specific, and verified after execution. 

---

## Day 55 — Environment Promotion Flow and Release Discipline (Part 6)

### Objective of Day-55 Part 6

I learned how a simple promotion-aware pipeline should look from end to end. The main idea is that the same exact Docker artifact should move from build stage to staging deployment, then through staging verification and approval, and finally into production deployment and production verification.

This is important because promotion is not only a deployment sequence. It is a controlled flow of exact artifact identity and release evidence.

---

### 1) Full logical promotion-aware pipeline shape

A strong logical promotion-aware pipeline can look like this:  
- validate  
- build_and_push  
- deploy_staging  
- verify_staging  
- approve_production  
- deploy_production  
- verify_production

**A strong pipeline creates a boundary between staging success and production release.**

---

### 2) Responsibility of each stage

**validate**

Checks whether the source code is acceptable.

**build_and_push**

Builds the Docker artifact once, pushes it, and records exact image identity.

**deploy_staging**

Deploys the exact artifact to staging.

**verify_staging**

Checks whether the staging deployment actually works.

**approve_production**

Decides whether the exact staging-tested artifact is allowed to move to production.

**deploy_production**

Deploys the same exact artifact to production.

**verify_production**

Checks whether the production deployment actually works.

**Main lesson**

Each stage has a distinct responsibility, and later stages should consume exact earlier evidence.

---

### 3) What should move forward through promotion

The following should move through the promotion flow:  
- exact image reference  
- exact digest  
- source commit  
- staging verification result  
- approval state  
- rollback target

**Main lesson**

Promotion is both software movement and evidence movement.

---

### 4) What must remain unchanged across promotion

The following should remain unchanged between staging and production:  
- image reference for the release  
- digest  
- code inside image  
- built dependencies inside image

**If artifact identity changes, then the same tested image is no longer being promoted.**

---

### 5) What may differ across environments

The following may differ:  
- secrets  
- env vars  
- endpoints  
- hostnames  
- target servers  
- verification strictness  
- rollback target  
- approval requirements

**The image stays the same, but runtime environment context may differ.**

---

### 6) Promotion is also confidence flow

A strong promotion flow does not only move software. It also moves:  
- exact artifact identity  
- verification evidence  
- approval  
- rollback readiness  
- release record information

**Promotion is a controlled release-confidence process, not just deployment movement.**

---

### 7) Final understanding statement for Part 6

I learned how to view a promotion-aware pipeline as a complete release path. A strong flow builds one exact image, deploys and verifies it in staging, reviews the evidence, approves production, and then deploys and verifies the same exact image in production. This is how Docker artifact promotion becomes disciplined release engineering.

---
