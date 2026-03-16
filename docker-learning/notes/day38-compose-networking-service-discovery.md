## Day 38 — Docker Compose Networking and Service Discovery

### Goal
Understand how Docker Compose automatically creates networks and allows services to communicate using service names instead of IP addresses.

---

### 1) Compose automatically creates a network
When running a Compose project, Docker automatically creates a user-defined bridge network.

Example from our project:  
```bash
python-fastapi-dockerfile_default
```

All services in the Compose file join this network automatically.  
Example services:  
+ `api`  
+ `db`  
These containers were attached to the same network.  

---

### 2) Inspecting the Compose network
We inspected the network using:  
```bash
docker network inspect python-fastapi-dockerfile_default
```

Output showed:  
```bash
db → 172.18.0.2
api → 172.18.0.3
```

This proves both containers are on the same network.

---

### 3) Docker DNS inside Compose
Docker provides an internal DNS server inside containers.

Inside the API container we tested:  
```bash
getent hosts db
```

Result:  
```bash
172.18.0.2 db
```

This shows Docker DNS resolves the service name `db` to the correct container IP.  
Applications should always use **service names**, not IP addresses.

Example:  
```bash
POSTGRES_HOST=db
```

---

### 4) Why IP addresses should not be used
Container IP addresses are not stable.

They can change when:  
+ containers restart  
+ containers are recreated  
+ networks are recreated

Docker DNS automatically updates service names to point to the correct IP.  
This is why service names are the correct way to connect services.

---

### 5) Container communication does not require exposed ports
The database container showed:  
`5432/tcp`

but not:  
`0.0.0.0:5432->5432`

This means the database was **not exposed to the host**.  
However, the API container still successfully queried the database.

Example test:  
```bash
curl http://localhost:8080/db-check
```

Result:  
```bash
{"ok":true,"db":"postgres","select":1}
```

This proves:  
Containers on the same Docker network can communicate **without publishing ports**.

---

### 6) Why DB ports are removed in production
In `compose.prod.yaml` we used:  
```bash
db:
ports: []
```

Reason:  
+ database should be private  
+ only API container should access it  
+ prevents external access to the database  
+ reduces attack surface

---

### 7) Why localhost cannot be used
Inside containers:  
`localhost = the same container`

If the API tries:  
`POSTGRES_HOST=localhost`

the API will try to connect to a database **inside the API container itself**, which does not exist.

The correct configuration is:  
`POSTGRES_HOST=db`

which resolves using Docker DNS.

---

### 8) Key takeaways
+ Docker Compose automatically creates a user-defined network.  
+ Services can communicate using service names.  
+ Docker DNS resolves service names to container IPs.  
+ Container IPs should never be hardcoded.  
+ Ports are required only for host access, not container communication.  
+ Databases should remain private and not expose host ports.

---
