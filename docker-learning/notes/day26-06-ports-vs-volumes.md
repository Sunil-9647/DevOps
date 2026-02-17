## Day 26(Part-6) — Ports (-p) and Volumes (-v)

### Ports
Containers have their own networking.  
To access a container service from host, we publish ports:
```bash
docker run -d -p 8080:80 nginx:alpine
```

Meaning:  
- host:8080 → forwarded to container:80

Format:  
> -p HOST_PORT:CONTAINER_PORT

---

### Volumes (data persistence)
Container filesystem is temporary. Deleting container deletes writable layer.  
Volumes store data outside container lifecycle.

Named volume (Docker-managed):
```bash
docker volume create vol1
docker run -v vol1:/data ubuntu:24.04
```

Bind mount (host path mapped):
```bash
docker run -v /host/path:/data ubuntu:24.04
```

Difference:  
- Named volume = Docker-managed storage (production-friendly)  
- Bind mount = host directory mounted (dev-friendly, depends on host path/permissions)

---

