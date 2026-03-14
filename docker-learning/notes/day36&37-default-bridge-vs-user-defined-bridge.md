## Day 36 & 37 — Default Bridge vs User-Defined Bridge and Docker DNS Debugging

### Goal
The goal of this day was to understand the real networking difference between:  
+ Docker’s default `bridge` network  
+ a user-defined bridge network  

This topic is very important because multi-container applications should not depend on Docker’s default bridge behavior. Real applications need:  
+ clean service discovery  
+ project-level isolation  
+ predictable networking

---

### 1) What is the default `bridge` network?
Docker creates a built-in network called `bridge` when Docker is installed.

If we run a container without specifying `--network`, Docker usually attaches it to this default `bridge` network.

Example characteristics of the default bridge:  
+ it provides normal IP-based connectivity  
+ containers on it can communicate by IP if routing allows  
+ but it does not provide the same clean name-based service discovery expected by real multi-container systems

In our machine, the default bridge subnet was:  
+ `172.17.0.0/16`

This means containers attached there can receive IPs like:
+ `172.17.0.2`  
+ `172.17.0.3`

---

### 2) What is a user-defined bridge network?
A user-defined bridge network is created manually, for example:

```bash
docker network create net36
```

This creates a separate bridge-based virtual LAN just for selected containers.

Advantages:  
+ automatic Docker DNS for attached containers  
+ better isolation between projects  
+ easier debugging  
+ better real-world multi-container behavior

This is why Docker Compose automatically creates a user-defined network for each project.

---

### 3) Key practical difference between default bridge and user-defined bridge
**Default bridge**  
+ containers can often reach each other by IP  
+ but clean container-name-based resolution is not available in the same way  
+ not ideal for real application stacks

**User-defined bridge**  
+ containers can reach each other by IP  
+ Docker also registers container/service names in internal DNS  
+ containers on the same network can use stable names instead of hardcoded IPs

This is the most important operational difference.

---

### 4) What we implemented and observed

#### A) We created a custom network
We created:  
```bash
docker network create net36
```

Docker assigned a subnet for this network and created a private container LAN.

#### B) We ran api36 on the user-defined network
We started a FastAPI container attached to `net36`.  
Then we inspected it and found:  
+ network name: `net36`  
+ IP address: `172.19.0.2`  
+ Docker DNS names included `api36`

That means Docker registered the container name in the DNS scope of that network.

#### C) We proved name-based communication works on the same user-defined network
We launched a temporary curl container on the same network and used:  
```bash
curl http://api36:8000/
```

It returned `HTTP 200 OK`.

This proved:  
+ Docker DNS resolved api36  
+ container-to-container communication worked by name  
+ no hardcoded IP was needed

#### D) We proved the same name fails outside that network
We launched another curl container without joining net36 and ran the same request:  
```bash
curl http://api36:8000/
```

This failed with:  
+ `Could not resolve host: api36`

This proved:  
+ Docker DNS resolution is scoped to network membership  
+ container names are not globally resolvable  
+ the requesting container must be on the same network

---

### 5) Docker DNS inside the container
Inside the container we checked:  
```bash
cat /etc/resolv.conf
```
and saw:  
+ `nameserver 127.0.0.11`

This is Docker’s embedded DNS server.

Its role:  
+ resolve service/container names inside attached Docker networks  
+ return the correct current IP for those names

This is why applications can connect using service names like:  
+ `db`  
+ `api36`

instead of hardcoded IP addresses.

---

### 6) Default bridge experiment
We created a container called `bridge-test` without specifying a network.  
It was attached to the default `bridge` network and got an IP:  
+ `172.17.0.2`

Then we tested two cases.

#### Case 1: Access by name
```bash
curl http://bridge-test
```

This failed with:  
+ `Could not resolve host: bridge-test`

#### Case 2: Access by IP
```bash
curl http://172.17.0.2
```

This worked and returned the nginx page.

**What this proves?**  
On the default bridge:  
+ IP connectivity worked  
+ but name resolution for the container did not work the same way as on the user-defined network

This is the exact practical reason why we prefer user-defined networks for real projects.

---

### 7) Multi-network container concept
We also attached `api36` to another network called `net36b`.  
After doing this, the container had:  
+ one IP on `net36`  
+ another IP on `net36b`

This proves an important fact:  
> A container gets one IP per network it joins.

This is how a service can act as a controlled bridge between different internal networks.

Example real-world pattern:  
+ frontend network  
+ backend network  
+ database network

A middle-tier service may join more than one network.

---

### 8) Why Compose uses service names like `db`
Docker Compose creates a user-defined network automatically and registers each service name in Docker DNS.

So in a compose project:  
+ service `db` can be reached using hostname `db`  
+ service `api` can be reached using hostname `api`

Even if the DB container restarts and gets a new IP, Docker DNS updates the mapping.  
That is why applications should connect to service names instead of container IPs.

---

### 9) Debugging steps we learned
When a container cannot reach another service, the correct debugging order is:  
1. Check network membership  
2. Check DNS resolution  
3. Check reachability  
4. Check application response

Examples:  
+ `docker inspect ...`  
+ `getent hosts api36`  
+ `ping api36`  
+ `curl http://api36:8000/`

This debugging ladder is more reliable than random guessing.

---

### 10) Main takeaways

+ Default bridge is okay for simple single-container tests, but not ideal for real multi-container apps.  
+ User-defined bridge provides better isolation and Docker DNS service discovery.  
+ Container/service names are better than hardcoded IPs because IPs can change.  
+ Docker DNS is provided by `127.0.0.11` inside containers.  
+ A container can join multiple networks and receive one IP per network.

---

### Commands used
```bash
docker network inspect bridge
docker network create net36
docker run -d --name api36 --network net36 -p 8082:8000 ghcr.io/sunil-9647/devops-py-api:sha-2435712
docker inspect api36 --format '{{json .NetworkSettings.Networks}}' | python3 -m json.tool
docker run --rm --network net36 curlimages/curl:latest curl -i http://api36:8000/
docker exec -it api36 cat /etc/resolv.conf
docker run -d --name bridge-test nginx:alpine
docker inspect bridge-test --format '{{json .NetworkSettings.Networks}}' | python3 -m json.tool
docker run --rm curlimages/curl:latest curl -i http://bridge-test
docker run --rm curlimages/curl:latest curl -i http://172.17.0.2
```

---
