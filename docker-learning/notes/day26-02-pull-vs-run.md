## Day 26(part-2) — Pull vs Run + Image Layers

### docker pull
Downloads the image only. No container is created.

### docker run
If image is missing: pulls it first, then creates + starts a container and runs the command.

Run = Pull(if needed) + Create + Start + Execute

### Layers
Images are built from multiple filesystem layers.  
Layers are cached and reused → faster downloads and faster builds.  

---

### Mini lab
- `docker pull hello-world` → no container  
- `docker run hello-world` → creates an exited container (unless `--rm`)

---
