## Day 26(Part-4) — Container lifecycle (create/start/stop/rm)

**Commands and meaning:**
```bash
docker create --name c1 ubuntu:24.04   # create only
docker start c1                        # start
docker stop c1                         # stop gracefully
docker rm c1                           # remove
```

`docker run` is the shortcut:
> run = pull(if needed) + create + start + execute

Important concept:
> A container runs as long as its main process (PID 1) runs.

---

