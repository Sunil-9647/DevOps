## Day 26(part-3) — Images vs Containers

### Image
- Immutable, read-only  
- Stored on disk  
- Identified by tag + IMAGE ID

### Container
- Created from an image  
- Has a writable layer (changes live here)  
- Has states: created/running/exited/removed 

---

### Proof we did:

- **Create file inside container → restart same container → file stays.**

**Step 1:** Create an Ubuntu container (interactive)  
```bash
docker run -it --name test-ubuntu ubuntu:24.04 bash
```

**Step 2:** Inside the container, create a file  
```bash
echo "hello from container" > inside.txt
ls -l
```

**Step 3:** Exit the container  
```bash
exit
```

**Step 4:** Now check containers  
```bash
docker ps -a
```

Showes `test-ubuntu` as Exited.

**Step 5:** Start it again and check the file is still there  
```bash
docker start -ai test-ubuntu
cat inside.txt
exit
```

That proves the container has its own writable layer (it kept my file).

- **Remove container → recreate container from same image → file is gone.**

**Step 6 (final proof):** Delete the container and recreate it  
```bash
docker rm test-ubuntu
docker run -it --name test-ubuntu ubuntu:24.04 bash
ls
```

`inside.txt` will be gone — because i deleted the container layer.

---
