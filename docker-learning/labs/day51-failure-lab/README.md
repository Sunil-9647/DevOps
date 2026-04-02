# Day-51 Failure Lab

## Purpose
This lab demonstrates common Docker failure patterns and teaches how to classify them correctly before choosing a recovery action.

## Concepts covered
- normal container exit vs real failure  
- startup failure before the app properly begins  
- runtime failure caused by missing configuration  
- bind mount hiding files that exist in the image  
- why container state is not the same as application health  
- why logs, inspect output, and exit codes must be interpreted together

---

## Lab structure

### 1. `exit-immediately/`
Demonstrates a container that exits normally after completing a one-shot task.

**Key lesson:**  
An exited container is not automatically a failure. If PID 1 finishes successfully and exits with code `0`, the container also ends successfully.

---

### 2. `startup-failure/`
Demonstrates a startup failure caused by an invalid command in `CMD`.

**Key lesson:**  
Some failures happen before the application even starts properly. In such cases:  
- `docker run` error output is very important  
- logs may be empty  
- container state may remain `created`  
- exit code can still reveal useful information such as `127`

---

### 3. `bad-config/`
Demonstrates a valid image and valid startup script failing because a required runtime environment variable is missing.

**Files:**  
- `Dockerfile`  
- `app.sh`

**Key lesson:**  
A container can fail even when the image and command are correct, simply because runtime configuration is wrong.  
The correct recovery is to fix the config and rerun the same good image, not rebuild the image.

---

### 4. `mount-hide-files/`
Demonstrates a bind mount hiding files that exist in the image.

**Key lesson:**  
A bind mount can overlay a container path and hide files that were present in the image. Docker does not delete those files; they are simply hidden by the mounted host path.

This drill is especially important because the container may still remain running even though application behavior is broken.

---

## Recommended troubleshooting approach
For each failure drill, observe in this order:

1. `docker ps -a`  
2. `docker logs <container>`  
3. `docker inspect <container>`  
4. if the container is running, inspect inside only when needed

This is safer than randomly restarting, rebuilding, or deleting things.

---

## Drill summary

### Drill 1 — normal completion
- container exits  
- exit code `0`  
- not a crash

### Drill 2 — startup failure
- invalid command  
- startup fails early  
- logs may be empty  
- `docker run` error is important evidence

### Drill 3 — bad runtime config
- image is valid  
- command is valid  
- app exits because required env var is missing

### Drill 4 — mount hiding files
- image is valid  
- bind mount hides expected file  
- container may still stay running  
- application behavior can still be broken  

---

## How to run the mount drill
For the bind-mount drill, create an empty host directory manually before running the broken case:

```bash
mkdir -p ~/DevOps/linux-learning/docker-learning/labs/day51-failure-lab/empty-host-dir
```

Then mount it onto `/app` in the container to reproduce the file-hiding scenario.

This helper directory is intentionally created at runtime and is not required as a committed repo artifact.


## Important learning

- container state and application state are different  
- exit code matters  
- logs are useful, but some failures happen before logs are produced  
- wrong config can break a valid image  
- mounts can silently break expected runtime behavior  
- good troubleshooting starts with evidence, not panic

## Final conclusion

This lab taught me that Docker troubleshooting is about pattern recognition and evidence collection. Different failures can look similar from a distance, but their root causes and recovery actions are different. A good DevOps engineer must classify the failure first, then choose the correct fix.
