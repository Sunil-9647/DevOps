## Day 56 — Practical Production-Style Deployment Patterns on a Linux VM (Part 1)

### Objective of Day-56 Part 1

Today I started learning what a practical Dockerized deployment looks like on a real Linux VM or server. Until now, I learned how Docker images are built, how CI/CD pipelines push exact artifacts, how promotion should work across environments, and why release and rollback discipline matter. But knowing CI/CD logic alone is not enough. A DevOps engineer must also understand what actually exists on the deployment server and how runtime operations are handled there.

The purpose of this part was to understand that a Linux VM is not just “some machine where containers run.” It usually has a small but important operational structure that helps the team:  
- run exact prebuilt images  
- keep runtime configuration in the correct place  
- manage releases in a repeatable way  
- verify service behavior after release  
- roll back safely if needed

This is important because many learners know how to write Dockerfiles and GitHub Actions workflows, but they do not understand what a real single-host deployment environment looks like.

---

### 1) What usually exists on a practical Linux VM

A real Linux VM used for Dockerized application deployment usually contains several important operational pieces.

Typical things present on the VM are:  
- Docker engine  
- Docker Compose plugin  
- one application deployment directory  
- Compose file  
- environment/config files  
- helper scripts for deploy, verify, and rollback  
- persistent volumes or mounted data paths  
- release-history records  
- sometimes backups or backup references

This means the server is not empty magic.  
It has a small runtime control structure.

#### Why this matters

If I do not understand what exists on the VM, then I will also not understand:  
- what gets changed during a release  
- what should remain stable  
- where environment-specific values live  
- where rollback information should be recorded

**Main lesson**

A Dockerized Linux VM should be thought of as a small operational environment with files, scripts, configuration, and runtime state—not just as a place where containers happen to run.

---

### 2) What belongs inside the image and what belongs on the VM

This was one of the most important lessons in this part.

A stronger Docker deployment model clearly separates:  
- what belongs inside the image  
- what belongs outside the image on the server

#### Usually inside the image

The Docker image usually contains:  
- application code  
- built dependencies  
- runtime binaries  
- startup command  
- whatever is needed for the app itself to run

This is the prepared artifact produced by CI/CD.

#### Usually on the VM

The Linux VM usually holds:

- `compose.yaml`  
- `.env`  
- helper scripts like `deploy.sh`, `verify.sh`, `rollback.sh`  
- release-history records  
- mounted persistent data paths  
- backups or backup references  
- environment-specific runtime values

#### Why this separation matters

This directly supports the principle:  
- build once  
- configure at runtime

If environment-specific settings are baked into the image, then the same image becomes harder to promote safely between staging and production.

**Main lesson**

The image should carry the application artifact, while the VM should carry runtime control, configuration, deployment structure, and operational records.

---

### 3) Why the Linux VM should consume exact prebuilt images

A stronger deployment model does not rebuild application images directly on the server during release.

Instead, the VM should:  
- pull exact prebuilt images from the registry  
- run those images with the correct runtime configuration  
- verify behavior  
- roll back to an earlier exact image if needed

#### Why rebuilding on the VM is weak

If the VM rebuilds from source during deployment:  
- the artifact may differ from what CI tested  
- build reproducibility becomes weaker  
- rollback clarity becomes weaker  
- the build-once, promote-the-same-artifact principle breaks

#### Why consuming exact images is stronger

If the VM uses the exact image reference from CI/CD:  
- release identity stays intact  
- what was tested is what gets deployed  
- rollback can return to an exact previous artifact  
- the server does not invent new release identity

**Main lesson**

The Linux VM should be a consumer of exact prepared artifacts, not a place where new application artifacts are created during release.

---

### 4) What a practical deployment folder on the server may look like

A real single-host Dockerized application often has one deployment folder on the server. This folder acts like the runtime control center for that app.

A practical example could look like:  
```
/opt/myapp/
├── compose.yaml
├── .env
├── scripts/
│   ├── deploy.sh
│   ├── verify.sh
│   └── rollback.sh
├── release-history/
│   ├── 2026-04-15-prod.txt
│   └── 2026-04-20-prod.txt
└── backups/
```

This is not the only possible layout, but it is a very realistic one.

#### Meaning of each part
`compose.yaml`

This file usually defines:  
- which services run  
- which image references are used  
- networks  
- volumes  
- restart behavior  
- environment wiring

This is the main deployment definition.



`.env`

This file usually contains:  
- environment-specific values  
- image tag variables if used  
- runtime configuration values

This is where release-specific version values and environment settings may live.



`scripts/`

This directory contains helper scripts that make operations repeatable:  
- `deploy.sh`  
- `verify.sh`  
- `rollback.sh`

These help reduce human mistakes.



`release-history/`

This directory contains small release records, such as:  
- old image  
- new image  
- rollback target  
- verification result  
- notes about what changed

This is very useful during incidents and audits.



`backups/`

This may contain:  
- backup artifacts  
- config backups  
- database backup references  
- pre-release safety copies

This depends on the system, but the idea is operational safety.

**Main lesson**

A practical deployment directory on the VM acts like the runtime control plane for the application.

---

### 5) Why `compose.yaml` often lives on the VM

For simple single-host Docker deployments, the Compose file often stays on the server.

**Why**

Because Compose defines the runtime arrangement of the application:  
- which containers should run  
- which image references they should use  
- which networks connect them  
- which volumes are attached  
- how runtime environment wiring works

This means the VM usually does not need the full source code repository just to perform a normal release.

Instead, it mainly needs:  
- deployment definition  
- runtime config  
- exact image references  
- helper scripts

**Main lesson**

On a Linux VM, Compose is often the stable runtime definition, while CI/CD is the place where images are built and identified.

---

### 6) Two common ways to control image versions on the VM

A practical VM usually needs some way to decide which app image version should run.

Two common patterns are used.

#### Pattern A — full image tag directly in `compose.yaml`

Example:  
```YAML
services:
  api:
    image: ghcr.io/sunil-9647/myapp:1.2.1
```

**How release happens**  
The operator changes:  
- `1.2.0` to `1.2.1`

directly in the Compose file.

**Good side**  
- very explicit  
- easy to read immediately

**Weak side**  
- the deployment definition changes every release  
- release history can become messy if not tracked carefully  
- harder to script in a clean repeatable way

#### Pattern B — image tag stored in `.env`

Example `compose.yaml`:  
```YAML
services:
  api:
    image: ghcr.io/sunil-9647/myapp:${APP_IMAGE_TAG}
```

Example `.env`:  
```
APP_IMAGE_TAG=1.2.1
```

**How release happens**  
The operator updates only the `.env` value.

**Good side**  
- `compose.yaml` stays stable  
- release-specific value is separated  
- easier to automate using scripts  
- easier to track as a runtime-controlled variable

**Why this is often cleaner**

Many single-host deployments benefit from keeping:  
- runtime definition stable  
- version value separately changeable

That makes release operations cleaner and more repeatable.

**Main lesson**

Keeping the image tag in `.env` is often cleaner for repeatable server-side releases because the Compose definition remains stable while only the release variable changes.

---

### 7) What a practical release on the VM may look like

Now we connect the VM layout to actual release activity.

Suppose `.env` currently contains:  
```
APP_IMAGE_TAG=1.2.0
```

and we want to deploy:  
```
APP_IMAGE_TAG=1.2.1
```

A practical release flow on the server may look like this:  
1. confirm current running image  
2. confirm target image  
3. update .env image tag  
4. use Compose to apply the update  
5. check container state, logs, and health  
6. record previous and new image in release-history  
7. keep rollback target known

**Why this is realistic**

In many single-host Docker releases, the biggest actual runtime change is simply:  
- one exact image reference changing from one version to another

This is why release discipline matters so much.

**Main lesson**

Many VM releases are controlled exact-image update events, not source-code rebuild events.

---

### 8) Why small server-side scripts are valuable

A weak operator may type deployment commands manually every time.

That is risky.

A stronger operator uses small helper scripts such as:  
- `deploy.sh`  
- `verify.sh`  
- `rollback.sh`

**Why scripts are safer**

Because they:  
- reduce repetition mistakes  
- preserve step order  
- make releases more repeatable  
- help under incident pressure  
- make team operations more consistent

**Important point**

These scripts are not “advanced luxury.”  
They are practical safety tools.

**Main lesson**

Small helper scripts make server-side release operations safer and more repeatable.

---

### 9) What `deploy.sh` may conceptually do

A simple deployment script may conceptually do the following:  
1. read the current image tag from `.env`  
2. accept a new target tag as input  
3. store the old tag for rollback record  
4. update `.env`  
5. run Compose update  
6. show service state/logs/health  
7. write a release-history record

**Why this is strong**

Because the script:  
- applies exact image identity  
- follows repeatable steps  
- preserves old and new version information  
- connects release action with release documentation

**Main lesson**

A deploy script should apply exact release identity and record what changed.

---

### 10) What `rollback.sh` may conceptually do

A simple rollback script may conceptually do this:  
1. read rollback target from release-history or operator input  
2. update .env back to previous image tag  
3. run Compose update again  
4. verify state, logs, and health  
5. record the rollback event

**Why this is strong**

Because rollback becomes:  
- exact  
- repeatable  
- less emotional  
- easier during incidents

**Main lesson**

A rollback script should return the system to an exact previous known-good image and then verify restoration.

---

### 11) What the operator actually cares about on the VM

Before a release, the operator usually cares about:  
- current running image  
- target image  
- rollback image  
- correctness of `.env`  
- volume safety  
- Docker health  
- service stability before change  
- disk space and general readiness

After a release, the operator usually cares about:  
- container state  
- logs  
- health  
- endpoint behavior  
- whether rollback is needed

This should feel familiar, because it connects directly to:  
- Day-53 release runbook thinking  
- Day-51 troubleshooting thinking

**Main lesson**

Server-side operations are where earlier Docker release and troubleshooting discipline become practical runtime work.

---

### 12) What the VM should not do in a strong model

A strong server-side release model avoids using the VM as a place to:  
- rebuild source code into images during release  
- invent release identity  
- pull random latest  
- mix many unrelated changes casually  
- act without rollback record

**Why this matters**

Because those responsibilities belong earlier in:  
- CI/CD  
- release control  
- promotion discipline

The VM should mostly:  
- consume exact image artifacts  
- apply runtime config  
- run services  
- expose runtime state  
- support verification and rollback

**Main lesson**

The Linux VM is where exact release identity is consumed and managed, not where it is invented.

---

### 13) Biggest lessons from Day-56 Part 1

The most important things I learned are:  
- a Linux VM has a practical runtime structure, not just containers  
- images and VM-side files have different responsibilities  
- exact prebuilt images should be consumed on the server  
- Compose often acts as the runtime definition  
- .env-based image versioning is often cleaner than changing Compose every release  
- small deploy/verify/rollback scripts improve safety  
- release-history records on the VM are useful during incidents  
- VM-side discipline is the operations half of CI/CD release discipline

---

### 14) Final understanding statement for Part 1

Today I learned that a Linux VM used for Dockerized deployments should be treated as a runtime control environment, not a build environment. The server should consume exact prebuilt images, apply runtime configuration through stable deployment files, verify service behavior after release, and keep rollback exact and repeatable. A strong server-side layout includes Compose, environment variables, helper scripts, and release-history records that support operational safety.

---
