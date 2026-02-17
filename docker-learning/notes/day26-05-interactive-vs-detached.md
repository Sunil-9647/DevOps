## Day 26(Part-5) — Interactive vs Detached (-it vs -d)

In Docker and similar container engines, the choice between **interactive (-it)** and **detached (-d)** modes depends on whether you want to engage with the container in real-time or let it run quietly in the background.

+ `-it` is used for interactive terminal sessions (shell).  
```bash
docker run -it ubuntu:24.04 bash
```

+ `-d` runs containers in background (services).  
```bash
docker run -d --name web nginx:alpine
```

Why nginx stays running but bash exits:  
+ nginx is a long-running service (PID 1 keeps running)  
+ bash exits if it has nothing to do (PID 1 exits → container stops)  

---

