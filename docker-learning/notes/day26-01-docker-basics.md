## Day 26(Part-1) — Docker Basics (from zero)

### Why Docker?
Docker lets you package an application with its dependencies into an **image** and run it anywhere as a **container**.  
This improves:  
- consistency (works same on every machine)  
- speed (fast setup and testing)  
- portability (dev → staging → prod)  

---

### Core terms (must know)
- **Docker CLI**: the `docker` command you type.  
- **Docker daemon / engine**: background service that builds images and runs containers.  
- **Image**: read-only template (app + OS libs + config).  
- **Container**: running instance of an image.  
- **Registry**: place to download images (example: Docker Hub).  
- **Docker context**: decides which Docker server your CLI talks to (example: Docker Desktop vs local engine).

---

### Quick mental model
Think like this:

**Image = blueprint**  
**Container = running house made from the blueprint**

You can create many containers from the same image.

---

### Verify Docker setup

```bash
docker version
docker context ls
docker info
```
