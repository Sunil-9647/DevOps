## Day 57 — Reverse Proxy and App Exposure Patterns on a Linux VM (Part 6)

### Objective of Day-57 Part 6

Today I learned how reverse proxy exposure connects back to the full Docker, CI/CD, promotion, and Linux VM deployment system. The purpose of this part was to understand that a production release is not complete just because a backend image was built and deployed. In a real user-facing environment, the application must also be exposed correctly through the reverse proxy, verified through the real public path, and recovered through that same path if rollback is needed.

This part was important because many learners understand these areas separately:  
- Docker image build  
- CI/CD workflow  
- promotion from staging to production  
- Linux VM deployment  
- reverse proxy routing  
- runtime verification  
- rollback

But in real DevOps work, these are not separate random tasks. They are one connected system.

A strong connected release system looks like this:  
- CI/CD creates and identifies the exact backend artifact  
- promotion flow decides where the artifact is allowed to go  
- Linux VM runtime applies that exact approved backend image  
- reverse proxy exposes the service safely to users  
- operator verifies the service through the real user-facing route  
- rollback restores the previous exact backend artifact and verifies recovery through the same user-facing route

This is the complete operational picture.

---

### 1) Where reverse proxy fits in the complete release chain

One of the biggest lessons from this part is that the reverse proxy is not some extra unrelated container. It is a core part of the real production delivery path.

A strong release system can be understood in layers:

#### CI/CD layer

This layer does:  
- source code validation  
- image build  
- registry push  
- exact tag and digest recording

This layer creates the exact artifact identity.

#### Promotion layer

This layer does:  
- staging deployment  
- staging verification  
- production approval  
- promotion evidence  
- rollback target awareness

This layer decides whether the exact artifact is allowed to move forward.

#### Linux VM runtime layer

This layer does:  
- apply exact approved image version  
- use stable deployment files like `compose.yaml`  
- use runtime variables such as `.env`  
- run helper scripts for deploy, verify, rollback

This layer applies the release in the real environment.

#### Reverse proxy layer

This layer does:  
- receive the real outside traffic  
- expose the service publicly  
- forward traffic internally to the backend app  
- act as the public entry point to the stack

This layer connects the runtime system to real users.

#### Operator verification layer

This layer does:  
- verify real proxy-facing route  
- inspect proxy logs  
- inspect backend logs  
- confirm dependency path  
- make the real release/rollback decision

This layer proves whether the promoted artifact actually works.

#### Why this matters

Without the reverse proxy layer, the release story is incomplete for a user-facing system. Users do not directly care which backend image exists in the registry. They care whether the service works through the actual public route.

**The reverse proxy is part of the real production release chain because it is the layer through which users actually experience the application.**

---

### 2) Connecting release flow and request flow

This part becomes much clearer when I separate two flows and then connect them.

#### Release flow

This is the operational release process:  
1. code changes  
2. CI validates  
3. CI builds exact image  
4. CI pushes exact image  
5. staging verifies exact image  
6. production approval happens  
7. Linux VM applies exact backend image  
8. operator verifies real runtime behavior  
9. rollback restores previous exact image if needed

#### Request flow

This is the real runtime request path:  
- user → reverse proxy → backend app → dependency

A strong system requires that these two flows stay aligned.

#### What alignment means

If the release flow approves:  
- backend image `1.2.1`

then the runtime flow must also actually expose:  
- backend image `1.2.1`  
    through
- the correct proxy path  
    with
- working backend behavior  
    and
- working dependencies

If the release flow says one thing and the runtime path serves another thing or serves broken behavior, then the system is weak even if individual steps looked successful.

**A release is only truly successful when the approved artifact is also the artifact that correctly serves user traffic through the real request path.**

---

### 3) What exact information must move from CI/CD into the VM in a proxy-based system

When the release reaches the Linux VM, the VM should not receive vague instructions. It should receive exact operational release information.

This includes things like:  
- exact backend image reference  
- exact digest if available  
- promotion approval state  
- rollback target  
- maybe a release note or deployment summary  
- the public entry point that must be verified

For example, the VM-side release should effectively know something like:  
```
Approved backend image: ghcr.io/sunil-9647/myapp:1.2.1
Digest: sha256:abc123...
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Public entry point: http://localhost:8080
```

#### Why this matters

In a proxy-based system, the backend image is often not directly exposed to users. But it still determines whether the public route works. So exact backend artifact identity still matters completely.

#### What would be weak

It would be weak if the VM received instructions like:  
- deploy latest  
- deploy newest image  
- deploy current build  
- deploy the one from yesterday maybe

That breaks release discipline and weakens traceability.

**In proxy-based deployments, the Linux VM should receive exact backend release identity plus user-facing verification context.**

---

### 4) How `.env`, Compose, and proxy work together in this connected system

Earlier, I learned that the Linux VM may use `.env` to control the exact backend app image:  
```
APP_IMAGE_TAG=1.2.1
```

And `compose.yaml` may use that value in a service definition like:  
```YAML
api:
  image: ghcr.io/sunil-9647/myapp:${APP_IMAGE_TAG}
```

Now this part connects that runtime pattern to the full release system.

#### What `.env` is doing

`.env` is acting as the runtime switch that tells the VM which exact backend image version to run.


#### What Compose is doing

Compose reads the current runtime state and applies it:  
- pulls the configured backend image  
- updates the service  
- attaches the expected network  
- preserves volumes  
- runs the defined stack

#### What the reverse proxy is doing

The proxy remains the public entry point and continues forwarding traffic internally to the backend app.

#### What this means together

A proxy-based backend release can work like this:  
- CI/CD approves backend image `1.2.1`  
- VM updates `.env` to `APP_IMAGE_TAG=1.2.1`  
- Compose updates the internal `api` service  
- proxy continues to forward user traffic to `api:8000`  
- operator verifies the public route and backend behavior

#### Important correction

None of these server-side tools should be treated as the source of release truth.  
- `.env` does not invent the release  
- Compose does not invent the release  
- the proxy does not invent the release

They all apply or expose the release that was already decided earlier.

**In a proxy-based system, `.env`, Compose, and the reverse proxy are runtime application mechanisms for the exact backend artifact identity already approved by CI/CD and promotion flow.**

---

### 5) Why proxy-aware verification is the final runtime truth

This is one of the most important lessons in all of Day-57.

A release can look good in many weak ways:  
- CI passed  
- image pushed successfully  
- backend container started  
- proxy container started  
- no immediate crash visible

But the real question is:  
**Can the user actually use the service through the public proxy-facing route?**

That is the final truth.

**Example**

Suppose:  

- CI built `ghcr.io/sunil-9647/myapp:1.2.1`  
- production approval was granted  
- VM updated `.env`  
- Compose updated the `api` service  
- proxy container is running  
- app container is running

But:  
- `curl http://localhost:8080` returns 502

That means the release is still bad for real users.

#### Why this matters

This proves that internal container liveness and deployment completion are weaker than real user-facing path success.

**In a reverse-proxy-based production system, successful user-facing proxy-path behavior is the final proof that the release actually succeeded.**

---

### 6) Why rollback must also be judged through the proxy path

Rollback in this type of system is also not complete just because the old backend image was restored internally.

A weak operator may think:  
- backend reverted  
- rollback done

That is incomplete.

A stronger operator asks:  
- did the real public route recover?

#### After rollback, the operator should still verify:
- proxy is running  
- public route works again  
- proxy logs no longer show upstream errors  
- backend logs returned to normal  
- dependency path works again

#### Why this matters

Because users never asked whether:  
- the old backend tag was restored internally

Users care whether:  
- the service works again through the real entry point

So rollback success must be judged using the same real public path that defines release success.

**In proxy-based systems, rollback success must be verified through restored user-facing proxy behavior, not only by seeing an older backend image running.**

---

### 7) One full connected example story

This part becomes strongest when seen as one full story from source code to user-facing route.

#### Example story
1. developer pushes commit `a1b2c3d`  
2. CI validates the code  
3. CI builds backend image `ghcr.io/sunil-9647/myapp:1.2.1`  
4. CI records digest `sha256:abc123...`  
5. staging deploys exact backend image `1.2.1`  
6. staging verification passes  
7. production approval is granted  
8. Linux VM updates `.env` from `APP_IMAGE_TAG=1.2.0` to `APP_IMAGE_TAG=1.2.1`  
9. Compose updates the internal `api` service  
10. reverse proxy continues exposing `http://localhost:8080` and forwarding to `api:8000`  
11. operator checks the public route, proxy logs, app logs, and dependency path  
12. if the public route works, the release is accepted  
13. if the public route breaks, rollback restores `APP_IMAGE_TAG=1.2.0`, Compose reapplies the previous backend image, and the operator verifies that the public route works again  
14. release or rollback record is written

#### Why this story is strong

Because every layer stayed connected:  
- exact artifact identity was preserved  
- promotion evidence existed  
- runtime application used the approved backend image  
- the proxy exposure model remained stable  
- user-facing verification was included  
- rollback restored the previous exact backend version and confirmed recovery through the real public path

**A strong production release system connects exact artifact identity to real public service behavior all the way from CI/CD to proxy-facing runtime verification.**

---

### 8) What goes wrong when these layers are disconnected

This is also very important to understand.

If CI/CD, promotion, VM runtime, and reverse proxy verification are disconnected, then bad patterns appear, such as:  
- CI/CD approved one image, but the VM applied another  
- staging verified one artifact, but production served a different backend  
- backend container was healthy internally, but public route was never checked  
- rollback restored the old backend tag, but nobody verified whether the public route recovered  
- release records existed, but they did not match what users actually experienced

#### Why this is dangerous

Because then the team cannot answer clearly:  
- which exact image is serving users?  
- did the approved artifact actually reach production correctly?  
- is the service healthy only internally, or also publicly?  
- did rollback restore real usability or only container state?

**A reverse-proxy-based release becomes weak when exact artifact identity, runtime application, public exposure, and user-facing verification are not aligned.**

---

### 9) Biggest lessons from Day-57 overall

By the end of Day-57, the most important things I learned are:  
- in a stronger single-host Docker deployment, the reverse proxy is usually the only public service  
- the application and database usually stay internal  
- the reverse proxy is the real user-facing gateway into the stack  
- proxy-to-app routing depends on correct service names, ports, network membership, and backend health  
- 502 and gateway-style errors often indicate proxy-to-backend path failures  
- release verification must include the public proxy-facing path, not just backend container state  
- a backend image release can break the public service even when the proxy container itself was unchanged  
- rollback success in a proxy-based system must also be verified through restored public behavior  
- CI/CD, promotion, Linux VM deployment, reverse proxy exposure, runtime verification, and rollback all form one connected production release system

---

### 10. Final understanding statement for Part 6

Today I learned how reverse proxy exposure fits into the complete Docker release system. CI/CD builds and identifies the exact backend artifact, promotion flow decides whether that artifact may move forward, the Linux VM applies that approved artifact through stable runtime files, and the reverse proxy exposes it through the real public entry point. The operator then verifies the service from the user-facing side, and if that public behavior becomes unsafe, rollback restores the exact previous backend artifact and confirms recovery through the same route. This is how reverse-proxy-aware release discipline works in a real single-host Docker environment.

---
