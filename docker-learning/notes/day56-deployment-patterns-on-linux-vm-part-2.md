## Day 56 — Practical Production-Style Deployment Patterns on a Linux VM (Part 2)

### Objective of Day-56 Part 2

Today I learned a very practical and realistic single-host deployment pattern for Dockerized applications on a Linux VM. The main idea is that the Compose file should usually remain stable, while the application image version should be controlled through a runtime variable such as `APP_IMAGE_TAG` inside `.env`. A small deployment script can then update that variable, apply the Compose update, perform basic verification, and record the release.

This is important because many learners imagine deployments as large complicated changes, but in real single-host Docker operations, many releases are actually simple and disciplined **exact-image update events**. The image artifact should already be built and pushed earlier in CI/CD. The server’s job is only to consume that exact image in a controlled, repeatable way.

This part connects directly to:  
- Day-53 release runbook thinking  
- Day-54 CI/CD exact artifact thinking  
- Day-55 promotion and rollback discipline  
- Day-56 Part-1 VM layout and server-side operations

---

### 1. The basic pattern: stable Compose file + variable-driven image version

A strong and practical deployment pattern is:  
- `compose.yaml` stays mostly unchanged  
- `.env` contains the app image version value  
- a helper script updates the `.env` value and runs the release flow

This is a very useful model because it separates:  
- deployment structure  
    from  
- release-specific version changes

#### What this means in practice

The server does not need to rewrite the Compose definition for every release.  
Instead, it changes one controlled runtime value.

This makes the release process:  
- easier to understand  
- easier to automate  
- easier to roll back  
- less error-prone

**Main lesson**

A stable deployment definition plus one controlled version variable is often cleaner than editing many deployment details during every release.

---

### 2. Example `compose.yaml` in this pattern

A simple example Compose file may look like this:  
```YAML
services:
  proxy:
    image: nginx:alpine
    ports:
      - "8080:80"
    depends_on:
      - api

  api:
    image: ghcr.io/sunil-9647/myapp:${APP_IMAGE_TAG}
    env_file:
      - .env
    restart: unless-stopped

  db:
    image: postgres:16
    env_file:
      - .env
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  db_data:
```

#### Most important line

The most important part is:  
```
image: ghcr.io/sunil-9647/myapp:${APP_IMAGE_TAG}
```

That means the image version is **not hardcoded directly** in the Compose file.  
Instead, Compose will read the image tag from `.env`.

#### Why this matters

Now the Compose file can stay stable across many releases, while only the version variable changes.

That is much better operationally than touching many lines of deployment definition every time.

**Main lesson**

The Compose file should mainly define structure, while the exact release version can come from a controlled variable.

---

### 3. Example `.env` in this pattern

A simple `.env` might look like this:  
```
APP_IMAGE_TAG=1.2.0
POSTGRES_DB=myapp
POSTGRES_USER=myappuser
POSTGRES_PASSWORD=change-me
```

For release operations, the most important line is:  
```
APP_IMAGE_TAG=1.2.0
```

When a new release is promoted to the server, that line may become:  
```
APP_IMAGE_TAG=1.2.1
```

#### What this means

The main server-side release change may be only:  
- change one image tag value

Everything else:  
- Compose structure  
- service wiring  
- volume definition  
- restart behavior

can remain stable.

#### Why this is cleaner

Because releases become:  
- smaller  
- easier to review  
- easier to automate  
- easier to revert

**Main lesson**

A single exact image tag variable in .env can act as the controlled release switch for the application service.

---

### 4. What actually changes during a release

This part is very important.

In this pattern, many releases do not require:  
- source code rebuild on the server  
- major file rewrites  
- large configuration edits  
- many manual steps

Instead, the release often changes only one controlled thing:  
- `APP_IMAGE_TAG`

For example:  
**Before release**  
```
APP_IMAGE_TAG=1.2.0
```

**After release**  
```
APP_IMAGE_TAG=1.2.1
```

That one change tells Compose:  
- use a different exact application image

#### Why this is powerful

Because the release becomes:  
- specific  
- traceable  
- controlled  
- easy to document

**Main lesson**

A practical single-host Docker release is often just an exact image version change applied carefully and verified properly.

---

### 5. The simple practical server-side release flow

A realistic release on the Linux VM using this pattern may look like this:  
1. confirm current running image/tag  
2. confirm new target image/tag  
3. preserve old tag as rollback target  
4. update `.env` with the new tag  
5. use Compose to pull and apply the new image  
6. check running state  
7. check logs and health  
8. write a release-history entry  
9. keep rollback target clearly known

#### Why this flow is strong

Because it does not:  
- rebuild artifacts  
- invent new release identity  
- depend on memory  
- use vague tags like `latest`

Instead, it:  
- applies an exact image identity  
- preserves the old identity  
- performs basic verification  
- records what changed

**Main lesson**

A strong server-side release flow is a controlled exact-image switch with verification and release history.

---

### 6. What a simple `deploy.sh` script conceptually does

A deployment script is a practical way to make this process repeatable.

A simple `deploy.sh` may conceptually do the following:  
1. read the current image tag from `.env`  
2. accept a new target tag as input  
3. store the current tag as rollback target  
4. update `.env`  
5. call Compose to pull and update the app service  
6. display state/logs  
7. record the release in release-history

#### Why this is useful

Because now deployment is no longer:  
- random manual typing  
- memory-based  
- different each time

Instead, it becomes:  
- repeatable  
- easier to trust  
- easier to run under pressure

**Main lesson**

A deploy script should apply one exact new artifact identity and preserve enough evidence to reverse the change if needed.

---

### 7. Why exact tag input is very important

A strong deploy script should accept an exact version/tag, for example:  
```bash
./deploy.sh 1.2.1
```

This is much stronger than:  
- deploy latest  
- deploy stable  
- deploy whatever is newest

#### Why exact input matters

Because exact input gives:  
- clear release intent  
- clear release records  
- easier rollback  
- less ambiguity during incidents

**Weak pattern**  
“Deploy latest.”

**Strong pattern**  
“Deploy 1.2.1.”

**Main lesson**  

A deployment command should use exact release identity, not vague moving labels.

---

### 8. Why `pull` plus `up -d` is a common Compose release pattern

In many Compose-based server releases, operators use a pattern like:  
- `docker compose pull api`  
- `docker compose up -d api`

#### What `pull` does
It fetches the exact image version now referenced by the config.

#### What `up -d` does
It updates or recreates the service using that configured version.

#### Why this pattern is common
Because it is simple and matches the idea:  
- update version variable  
- pull exact image  
- apply update

This is very common in practical single-host Docker operations.

**Main lesson**

Compose-based releases often work by changing the configured image version and then reapplying the relevant service cleanly.

---

### 9. Why backing up `.env` before modifying it is useful

A useful safety habit in deployment scripts is to preserve the existing `.env` before changing it.

For example:  
```bash
cp .env .env.bak
```

#### Why this helps

If something goes wrong during script execution or variable editing, the previous configuration file still exists.

This is not a full rollback strategy by itself, but it is:  
- a useful safety net  
- a quick recovery aid  
- a practical ops habit

**Main lesson**

Small file-safety steps help reduce risk during runtime configuration updates.

---

### 10. Why release-history on the VM is valuable

A practical deployment should leave behind a small release record on the server.

For example, a file may contain:  
```
Date: 2026-04-23
Environment: production
Previous image: ghcr.io/sunil-9647/myapp:1.2.0
New image: ghcr.io/sunil-9647/myapp:1.2.1
Rollback target: ghcr.io/sunil-9647/myapp:1.2.0
Verification: passed
Notes: production config unchanged
```

#### Why this is valuable

Because later, when something goes wrong, the operator can quickly answer:  
- what changed?  
- when did it change?  
- what was the old image?  
- what should be rolled back to?

This is simple but very strong operational evidence.

**Main lesson**

Release-history on the server improves incident response, audit clarity, and rollback safety.

---

### 11. Why small helper scripts are safer than manual typing

A weak operator may type deployment commands manually every time.

That is risky because:  
- steps may be forgotten  
- commands may be typed inconsistently  
- rollback target may not be recorded  
- pressure may lead to mistakes

A stronger operator prefers helper scripts such as:  
- `deploy.sh`  
- `verify.sh`  
- `rollback.sh`

#### Why scripts are safer

Because they:  
- preserve step order  
- reduce repeated human mistakes  
- make releases more repeatable  
- make rollback faster  
- improve team consistency

**Main lesson**  
Small helper scripts are practical safety tools, not luxury extras.

---

### 12. What a simple rollback script conceptually does

A rollback script may conceptually do this:  
1. accept exact rollback tag  
2. identify current tag  
3. update .env back to the rollback value  
4. use Compose to pull and apply the previous image  
5. show state/logs/health  
6. record the rollback event

#### Why this is strong

Because rollback becomes:  
- exact  
- repeatable  
- less emotional  
- easier under incident pressure

**Main lesson**

Rollback should restore an exact previous known-good image in a structured way, not based on vague memory.

---

### 13. What this pattern still does not cover yet

This deployment pattern is strong, but still basic.

It does **not yet fully include**:  
- digest recording in the VM-side script  
- real health endpoint checks  
- endpoint curl verification  
- dependency connectivity verification  
- stronger rollback automation from release-history parsing  
- approval handling inside the script  
- production/staging separation logic inside one toolchain

That is okay.
Right now we are learning the practical pattern first.

**Main lesson**

A simple exact-tag deployment model is already valuable, even before advanced automation is added.

---

### 14. Biggest lessons from Day-56 Part 2

The most important things I learned are:  
- stable Compose definition plus variable-driven image version is a strong single-host pattern  
- `.env` can act as a controlled release switch for image version  
- many real releases are exact-image update events  
- deploy scripts make server operations more repeatable  
- exact tag input is much stronger than using vague labels like `latest`  
- `pull` + `up -d` is a common Compose release pattern  
- release-history on the VM gives useful operational evidence  
- rollback should also update exact version identity and verify restoration

---

### 15. Final understanding statement for Part 2

Today I learned a practical Linux VM deployment model where the Compose definition stays stable, the application image version is controlled through `.env`, and helper scripts apply exact image updates in a repeatable way. This pattern is strong because it keeps release identity clear, reduces manual editing, supports rollback discipline, and matches the idea that the VM should consume exact prebuilt images instead of rebuilding software during deployment.

---

