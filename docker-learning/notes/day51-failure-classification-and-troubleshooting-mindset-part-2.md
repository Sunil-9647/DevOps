## Day 51 — Failure Drills and Operational Recovery Mindset (Part 2)

### Objective of Day-51 Part 2

In this part, I practiced controlled Docker failure drills to understand how different types of failures look in real commands and outputs. The goal was not just to “see an error,” but to learn how to classify the failure correctly and choose the right recovery action.

The drills were designed to show that:  
- not all exited containers are failures  
- not all failures produce useful logs  
- configuration problems can break a valid image  
- bind mounts can break application behavior without deleting image content  
- a running container can still be functionally broken

This part is important because real troubleshooting depends on recognizing these patterns quickly and accurately.

---

### 1) Failure Drill 1 — container exits normally after successful work

I created a simple image whose command printed a message and exited with code `0`. The container status became `Exited (0)`, and the logs showed normal completion. This proved that an exited container is not automatically a failure. If PID 1 finishes successfully, the container also ends successfully.

```dockerfile
FROM alpine:3.20
CMD ["sh", "-c", "echo 'Starting container'; echo 'Work completed'; exit 0"]
```

#### What happened

When I ran the container:  

- it printed `Starting container`  
- then printed `Work completed`  
- then stopped

#### Evidence collected
- `docker ps -a` showed Exited (0)  
- `docker logs` showed both messages  
- `docker inspect --format '{{.State.Status}} {{.State.ExitCode}}'` showed:  
    - `exited 0`

**Meaning**  
This was not a crash.  
PID 1 completed successfully and then exited with code `0`.

**Main lesson**  
An exited container is not automatically a failure. Some containers are short-lived one-shot tasks and are expected to exit after finishing their work.

---

### 2) Failure Drill 2 — startup failure because command does not exist

I created another image with this Dockerfile: `CMD ["nonexistent-command"]`. The image built successfully, but `docker run` failed with an error saying the executable file was not found in `$PATH`. The container state remained `created`, the exit code was `127`, and `docker logs` was empty. This proved that some failures happen before the application even starts properly, so logs may not always contain the main clue. In such cases, the `docker run` error message and `docker inspect` state are important evidence.

```dockerfile
FROM alpine:3.20
CMD ["nonexistent-command"]
```

#### What happened

The image built successfully, but `docker run` failed immediately because the runtime could not find the executable.

#### Error observed

Docker showed an error like:  
- executable file not found in `$PATH`

#### Evidence collected
- `docker ps -a` showed container state as Created  
- `docker logs` was empty  
- `docker inspect --format '{{.State.Status}} {{.State.ExitCode}}'` showed:  
    - `created 127`

**Meaning**  
This was a **startup failure before the real process began successfully**.  
The container object was created, but PID 1 could not be launched.

**Important lesson**

Some failures happen so early that logs may be empty. In such cases, the most useful clues may come from:  
- the `docker run` error itself  
- `docker ps -a`  
- `docker inspect`

**Main lesson**
If the startup command is invalid, Docker may fail before the application ever begins, so empty logs do not mean “nothing is wrong.”

---

### 3) Failure Drill 3 — valid image but missing required runtime configuration

I created a small shell app that required `DB_HOST`. The image built correctly and the startup script itself was valid, but when I ran the container without `DB_HOST`, it printed `ERROR: DB_HOST is missing` and exited with code `1`. This proved that a container can fail even when the image and command are valid, simply because runtime configuration is wrong. The correct recovery action in this case is to fix the environment variable and run the same image again, not rebuild the image.

`app.sh`

```bash
#!/bin/sh

echo "Starting app"

if [ -z "$DB_HOST" ]; then
  echo "ERROR: DB_HOST is missing"
  exit 1
fi

echo "DB_HOST=$DB_HOST"
echo "App started successfully"
sleep 300
```

`Dockerfile`

```dockerfile
FROM alpine:3.20
WORKDIR /app
COPY app.sh .
RUN chmod +x /app/app.sh
CMD ["/app/app.sh"]
```

#### What happened when `DB_HOST` was missing

I ran the container without setting `DB_HOST`.

The logs showed:  
- `Starting app`  
- `ERROR: DB_HOST is missing`

The container state showed:  
- `Exited (1)`

And inspect showed:  
- `exited 1`

**Meaning**  
The image itself was fine.  
The command itself was fine.  
Docker itself was fine.

The real issue was:  
- missing runtime configuration

**Recovery action**  
Instead of rebuilding the image, I ran the same image again with:  
```bash
docker run -d --name day51-bad-config-fixed -e DB_HOST=db day51-bad-config:v1
```

Then:  
- the container stayed `Up`  
- logs showed:  
    - `Starting app`  
    - `DB_HOST=db`  
    - `App started successfully`

**Main lesson**  
If the failure is caused by missing or wrong runtime configuration, the correct fix is to correct the environment/config and rerun the same good image. Rebuilding the image would be the wrong action.

---

### 4) Failure Drill 4 — bind mount hides expected image files

I created an image that contained a file inside `/app`.

**Dockerfile**

```dockerfile
FROM alpine:3.20
WORKDIR /app
RUN echo "This file exists inside the image" > /app/message.txt
CMD ["sh", "-c", "echo 'Container started'; ls -l /app; cat /app/message.txt; sleep 300"]
```

**First run without mount**

I ran the container normally.

Logs showed:  
- `Container started`  
- `/app/message.txt` existed  
- file contents printed successfully

Inspect showed:  
- `running 0`

This proved the image itself was correct.

---

### 5) Same image with a bad bind mount

Then I created an empty host directory and mounted it over `/app`:

```bash
docker run -d --name day51-mount-broken \
  -v ~/DevOps/linux-learning/docker-learning/labs/day51-failure-lab/empty-host-dir:/app \
  day51-mount-hide:v1
```

#### What happened

Logs showed:  

- `Container started`  
- `total 0`  
- `cat: can't open '/app/message.txt': No such file or directory`

`docker inspect --format '{{json .Mounts}}'` clearly showed:  
- source = empty host directory  
- destination = `/app`

#### Important observation

The container was still:  
- `running`

It did not exit.

Why?  
Because after the failed `cat`, the shell still continued to `sleep 300`, so PID 1 stayed alive.

**Meaning**

This is very important:  
- Docker did not delete the file from the image  
- the bind mount overlaid `/app`  
- the empty host directory hid the image file at runtime  
- the container stayed running, but the expected app behavior was broken

**Main lesson**  
A bad bind mount can break application behavior while the container still appears healthy at a superficial level.

---

### 6) What Drill 4 proved operationally

This drill proved several real-world lessons:  

#### A. Bind mounts can hide image content

A file that exists in the image can become invisible at runtime if a bind mount overlays that path.

#### B. Running container does not guarantee correct behavior

The container was still `Up`, but the expected file was missing and the app logic was wrong.

#### C. `docker inspect` is essential for mount debugging

The mount information made the root cause visible immediately.

**Main lesson**  
When expected files disappear inside a running container, check mounts before blaming the image.

---

### 7) Comparison of all four failure drills

#### Drill 1 — normal completion
- container exited
- exit code `0`
- task finished successfully

#### Drill 2 — invalid startup command
- container creation happened
- command failed before proper startup
- state remained `created`
- exit code `127`

#### Drill 3 — missing runtime config
- script started correctly  
- app detected missing `DB_HOST`  
- exited with code `1`

#### Drill 4 — bind mount hiding files
- container kept running  
- app behavior was broken because expected file disappeared behind a mount

**Main lesson**  
Docker failures are not one single pattern. The state, logs, exit code, and inspect output must all be interpreted together.

---

### 8) Recovery thinking learned from the drills

The drills also taught that recovery action depends on failure type.

**When not to rebuild**  
- if the image is fine  
- if only runtime config is wrong  
- if a bind mount path is wrong  
- if dependency availability is the issue

**When rebuild may be needed**  
- if the image itself is broken  
- if the `CMD` is wrong in the Dockerfile  
- if required files are missing from the image

**When recreate or rerun is enough**  
- if the same good image only needs corrected runtime env values  
- if a bad mount must be removed or corrected

**Main lesson**  
Recovery must match the real failure type. Restarting, rebuilding, and recreating are not interchangeable actions.

---

### 9) Biggest lessons from Day-51 Part 2

The most important things I learned in these drills are:  
- an exited container is not automatically a crash  
- exit code `0` usually means normal completion  
- command-not-found startup failures may leave the container in `created` state with exit code `127`  
- some failures happen so early that logs are empty  
- a valid image can still fail because required runtime config is missing  
- missing runtime config should be fixed by correcting env values, not by rebuilding the image  
- bind mounts can hide files that exist in the image  
- a container can keep running even while important app behavior is broken  
- `docker inspect` is extremely important for mount and config debugging  
- failure classification must come before choosing recovery action

---

### 10) Final understanding statement for Part 2

Today I learned that Docker troubleshooting becomes much easier when I compare failure patterns carefully. Some containers exit normally, some fail before startup, some fail because of missing configuration, and some keep running while the actual application behavior is broken. These drills showed me that correct troubleshooting depends on reading the evidence from container state, logs, exit codes, and inspect output together. This is the mindset needed for real operational support and incident handling.

---

