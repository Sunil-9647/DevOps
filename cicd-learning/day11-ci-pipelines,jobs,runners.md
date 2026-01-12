## Day 11 - CI in the Real World (Pipelines, Jobs, Runners)

### Key terms (short)
+ **Pipeline:** The whole automated flow (build → test → package → optionally deploy). Triggered by events (push, PR, schedule, manual).  
+ **Stage:** Logical phase of the pipeline (build, test, deploy). Not always explicit in all CI systems, but useful for design.  
+ **Job:** A collection of ordered steps that run on one runner (one machine). One job = one isolated VM/container.  
+ **Step:** A single command or action inside a job (`run`: shell command or `uses`: an action).  
+ **Runner/Agent:** The ephemeral machine provided by the CI tool that executes a job. Fresh each run.  
+ **Artifact:** Files uploaded by a job (binaries, logs, test reports) to be downloaded by later jobs or humans.  
+ **Cache:** Best-effort storage to speed future runs (dependencies).  
+ **Fail-fast:** If a step or job fails (non-zero exit code), dependent work stops immediately.  

---

### What actually happens at runtime?

1. An event (push/PR/manual/schedule) triggers the pipeline.  
2. The CI system schedules jobs. Each job gets its own runner (fresh machine).  
3. The runner is empty — you must explicitly checkout code and install tools.  
4. Steps inside the job run in order. A non-zero exit code fails the step → job fails.  
5. Jobs run in parallel by default; use dependency primitives (e.g., needs:) to enforce order.  
6. If a job produces files needed later, it must upload them as artifacts; later jobs must download those artifacts.  
7. Runner is destroyed at the end — nothing persists unless stored via artifacts or external storage.  

---

### Why runners are fresh every time? (three reasons)

+ **Isolation:** avoids hidden state or "it works on my machine" problems.  
+ **Reproducibility:** same inputs should produce same outputs.  
+ **Security:** prevents data leak / cross-run contamination.

---

### Jobs vs Steps

+ Use **steps** inside a job when commands must share filesystem or environment. Steps share the job’s runner and can access the same files.  
+ Use separate **jobs** when tasks are independent, can run in parallel, or must be isolated (lint, unit tests, security scans).  
+ If a job needs output from another job, use artifacts to transfer files; do not assume files exist across jobs.  
+ Default parallelism speeds CI but requires thinking about artifacts and ordering.  

---

### Artifacts vs Cache

+ **Artifacts** = correctness. Use to pass build outputs and logs between jobs or to humans. Persist per-run.  
+ **Cache** = performance. Use to store dependencies for future runs. Cache may not be restored and is not guaranteed — never use it to transfer build outputs required for correctness.

---

### Failure logic and observability

+ **Default**: step failure → job failure → pipeline failure (fail-fast).  
+ Use `if: always()` (or equivalent) to upload logs/artifacts even on failure so you can debug.  
+ Avoid `continue-on-error` except for non-blocking checks; use it intentionally and document why.

---

### Practical job patterns

+ Single job build+test — when test needs build artifacts in the same workspace.  
+ Multiple jobs + artifacts — build job produces an artifact; test job downloads it and runs tests.  
+ Parallel checks — lint, unit tests, static analysis run concurrently to save time.  
+ Matrix jobs — run the same job across versions/OS (e.g., Python 3.10 / 3.11).  
+ Needs/dependency chaining — explicit `needs`: to ensure order and to skip dependent jobs on failure.

---

### Common beginner mistakes (and how to avoid them)

+ **Assuming runner has code** — always `checkout`.  
+ **Sharing files without artifacts** — explicitly upload/download artifacts between jobs.  
+ **Using cache for correctness** — never. Cache can be missing or stale.  
+ **Printing secrets** — secrets may be masked but should never be printed or logged intentionally.  
+ **Running heavy pipeline on every branch** — use triggers/filters to limit resource use.  
+ **Giving deploy credentials to all jobs** — scope secrets to the job/step that needs them.

---

### Short checklist to design a CI pipeline

1. **Define goals:** what must this pipeline guarantee? (e.g., build success, unit tests, integration tests).  
2. **Identify blocking steps:** which failures must block merges? (unit tests, critical security scans).  
3. **Choose granularity:** single job vs multi-job (use single job if steps share files; multiple jobs for parallel checks).  
4. **Plan artifacts:** what outputs must be passed between jobs? (binaries, test reports).  
5. **Decide triggers:** push, PR, schedule, manual — be conservative.  
6. **Scope secrets** to minimal jobs/steps.  
7. **Add observability:** upload logs & artifacts always.  
8. **Fail-fast:** ensure the first failing step stops useless downstream work.  
9. **Add caching** for dependencies where it speeds up runs (but not for correctness).  
10. **Document** the pipeline behavior in repo README or docs.  

---

