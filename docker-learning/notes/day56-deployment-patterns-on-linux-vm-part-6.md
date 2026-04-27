## Day 56 — Practical Production-Style Deployment Patterns on a Linux VM (Part 6)

### Objective of Day-56 Part 6

Today I learned how the VM-side deployment pattern connects back to CI/CD and environment promotion flow. This is one of the most important conceptual parts of the whole Docker and deployment track, because it connects everything I learned so far into one complete release system.

Earlier, I learned:  
- how Docker images are built and tagged  
- why CI/CD should build exact artifacts only once  
- why the registry stores the exact release artifact  
- why staging should verify the same artifact before production  
- why production promotion should use approval and release evidence  
- how a Linux VM can use `compose.yaml`, `.env`, and helper scripts to apply runtime changes  
- how operators should verify runtime behavior and roll back safely

In this part, I connected all of those layers together.

The biggest idea is this:  
- CI/CD creates and identifies the exact artifact  
- promotion flow decides where that exact artifact may go  
- the Linux VM applies that approved artifact in runtime  
- the operator verifies it  
- rollback returns to the exact previous known-good artifact if needed

This is important because many learners understand each layer separately, but real DevOps strength comes from understanding how all of them work together as one release system.

---

### 1. The release system starts in CI/CD, not on the VM

One of the strongest lessons in this part is that release identity should begin earlier in the process, not on the server.

A weak mental model says:  
- source code reaches the server  
- the server decides what to build or run  
- the server figures out the release

That is weak because the server should not be creating release identity.

A stronger model says:  
- CI validates the source code  
- CI builds the Docker image once  
- CI pushes the exact image to the registry  
- CI records the exact image tag and digest  
- promotion flow decides whether that exact artifact may move to another environment  
- the Linux VM consumes that approved artifact

#### Why this matters

If the VM starts inventing or changing artifact identity later, then the release process becomes disconnected. The artifact that passed CI/CD and approval may not be the same one that actually runs in production.

**The Linux VM should be a consumer of exact release identity, not the creator of release identity.**

---

### 2. The full connected release chain

A strong end-to-end release flow looks like this:  
1. developer changes code  
2. CI validates code  
3. CI builds Docker image once  
4. CI pushes exact image to registry  
5. exact image tag and digest are recorded  
6. staging deploys the same exact artifact  
7. staging verification passes  
8. production promotion is approved  
9. Linux VM applies that exact approved image  
10. operator verifies runtime behavior on the VM  
11. if needed, rollback restores the exact previous known-good image

This is the connected chain.

#### Why this matters

Each stage has a different responsibility:  
- CI/CD prepares the artifact  
- promotion flow controls where the artifact is allowed to go  
- the VM applies the approved release in runtime  
- the operator proves that the runtime result is correct

If one of these layers becomes vague, the whole release process becomes weaker.

**A strong deployment system is not one step. It is a connected chain of exact artifact creation, controlled promotion, runtime application, and verification.**

---

### 3. What exactly should flow from CI/CD into the Linux VM

When the release reaches the Linux VM, the VM should receive clear and exact information.

It should receive things like:  
- exact image reference  
- exact digest if available  
- release context  
- rollback target  
- maybe release note or promotion record

For example, the VM-side operator or automation should know something like:  
```
Deploy ghcr.io/sunil-9647/myapp:1.2.1
Digest: sha256:abc123...
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
```

This is much stronger than receiving vague instructions like:  
- deploy latest  
- deploy newest build  
- deploy whatever was just pushed

#### Why this matters

If the VM receives vague instructions, then:  
- the wrong image may be deployed  
- release traceability breaks  
- rollback becomes less exact  
- the approved artifact and running artifact may differ

**CI/CD and promotion flow should hand over exact artifact identity to the Linux VM, not ambiguity.**

---

### 4. Where `.env` fits into the full connected system

Earlier, I learned that the Linux VM can use `.env` to control the app image version, for example:  
```
APP_IMAGE_TAG=1.2.1
```

Now the important correction is:  
`.env` is not the place where release truth is invented.  
`.env` is the place where the already-approved release identity gets applied on the server.

#### What this means

Suppose CI/CD and promotion flow decided that the approved artifact is:  
```
ghcr.io/sunil-9647/myapp:1.2.1
```

Then the VM-side deployment process may update `.env` to:  
```
APP_IMAGE_TAG=1.2.1
```

That means `.env` is acting like a runtime application mechanism for release identity.

#### Why this matters

A weak operator may incorrectly think:  
- changing `.env` decides the release

But the stronger interpretation is:  
- the release was already decided by CI/CD and promotion flow  
- `.env` simply applies that approved exact version on the VM

**`.env` should be treated as a runtime release switch, not as the original source of release truth.**

---

### 5. Where Compose fits into the full connected system

Compose is also not the source of release truth.

Compose is the tool that applies the configured runtime state on the Linux VM.

For example:  
- `compose.yaml` defines the service structure  
- `.env` provides the selected image tag  
- Compose then pulls and runs the exact image defined by that state

So Compose is doing runtime application work:  
- start/update services  
- attach networks  
- preserve volumes  
- apply container definitions

#### Why this matters

Compose should not be treated like a release-decision engine.  
It is a runtime application tool.

That means:  
- CI/CD decides the artifact  
- promotion decides whether it is allowed  
- Compose applies it on the VM

**Compose applies the approved runtime state; it does not create release approval or artifact identity.**

---

### 6. Where operator verification fits into the connected system

Even after:  
- CI validation  
- image build  
- registry push  
- promotion decision  
- VM-side Compose update

the release is still not finished until the operator verifies runtime behavior.

This is where all earlier learning comes back together:  
- **Day-51** taught failure classification and runtime truth  
- **Day-53** taught release and rollback runbook discipline  
- **Day-55** taught evidence-based promotion  
- **Day-56** taught VM-side deployment patterns

Operator verification proves that:  
- the exact approved artifact actually works in the real runtime environment

#### Why this matters

CI/CD can prove:  
- code passed checks  
- image was built  
- image was pushed

Promotion can prove:  
- the artifact was accepted for staging or production

But only runtime verification on the VM can prove:  
- the service actually works there

**Operator verification on the VM is the final runtime truth of the release.**

---

### 7. Where rollback fits into the full connected system

Rollback is not just a server-side action, and it is not just a CI/CD concept. It depends on both.

#### CI/CD and promotion provide:
- exact previous artifact identity  
- release history  
- promotion evidence  
- current and previous approved image references

#### VM-side operations provide:
- the mechanism to restore the previous exact image  
- Compose-based runtime reapplication  
- post-rollback verification  
- rollback event recording

That means rollback is a connected discipline across:  
- exact artifact identity  
- release record  
- promotion state  
- server-side execution  
- runtime recovery verification

#### Why this matters

If the earlier layers did not preserve exact identity, then rollback on the server becomes weaker.  
And if the VM-side operations are sloppy, then exact rollback records are still not enough.

**Strong rollback depends on both earlier release identity discipline and correct VM-side execution and verification.**

---

### 8. One full connected release example

This part becomes strongest when seen as one full story.

#### Example story
1. developer pushes commit `a1b2c3d`  
2. CI validates the code  
3. CI builds `ghcr.io/sunil-9647/myapp:1.2.1`  
4. CI records digest `sha256:abc123...`  
5. staging deploys that exact image  
6. staging verification passes  
7. production approval is granted  
8. Linux VM operator updates `.env` from `APP_IMAGE_TAG=1.2.0` to `APP_IMAGE_TAG=1.2.1`  
9. Compose pulls and updates the app service  
10. operator verifies state, logs, health, endpoint, and dependency path  
11. if healthy, a release-history record is written  
12. if broken, the operator restores `.env` back to `1.2.0`, re-applies Compose, verifies recovery, and writes a rollback record

This is a complete end-to-end release story.

#### Why this is strong

Because:  
- the artifact identity remained exact from CI to production  
- staging and approval added release evidence  
- the VM did not invent a new release  
- operator verification checked runtime truth  
- rollback target was exact and pre-known

**A real DevOps release system works only when CI/CD, promotion, VM runtime application, verification, and rollback all stay connected.**

---

### 9. What happens if these layers are disconnected

This is also very important to understand.

If CI/CD, promotion, and VM operations are disconnected, bad patterns appear, such as:  
- CI built one image, but the VM deploys another  
- staging passed one artifact, but production runs a different one  
- the VM uses `latest` instead of the approved exact image  
- rollback target is unclear  
- release notes do not match runtime reality  
- promotion evidence becomes meaningless

#### Why this is dangerous

Because then nobody can confidently answer:  
- what exact code is running?  
- what exact image was approved?  
- what exact artifact passed staging?  
- what exact image should be rolled back to?

That is how incidents become confusing and recovery becomes slower.

**Release discipline becomes weak when artifact identity, promotion evidence, and VM runtime execution are not aligned.**

---

### 10. The biggest lessons from Day-56 Part 6

The most important things I learned are:  
- CI/CD should create and identify the exact Docker artifact  
- promotion flow should decide where the artifact may go  
- the Linux VM should consume the exact approved artifact  
- `.env` and Compose apply the approved runtime state on the VM  
- operator verification is the final proof of runtime success  
- rollback depends on exact earlier records and correct VM-side restoration  
- real DevOps strength comes from connecting all layers into one release system

---

### 11. Final understanding statement for Part 6

Today I learned how CI/CD, promotion flow, and Linux VM operations connect into one full Docker release system. CI/CD builds and identifies the exact image artifact, promotion flow decides whether that exact artifact may move forward, and the Linux VM applies that approved image using stable runtime files such as `.env` and `compose.yaml`. The operator then verifies runtime behavior, and if necessary, rolls back to the exact previous known-good image. This is how Docker artifact discipline becomes real deployment discipline.

---
