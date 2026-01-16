## Day 11 — Designing and Building My Own CI Pipeline (GitHub Actions)

### What is Continuous Integration (CI)

Continuous Integration (CI) is the practice of automatically validating code changes whenever a developer pushes code or creates a pull request.  
The main goal of CI is to ensure that:  
- The code builds correctly  
- Quality checks are passed  
- Tests are executed automatically  
- Issues are detected early before merging into the main branch  

CI acts as a **quality gate** for the codebase.

---

### What is CI contract?

A CI pipeline must always answer these questions:  
- Is the code buildable?  
- Does it meet quality standards?  
- Do tests pass?  
- Can we provide logs or reports if something fails?  

If a pipeline cannot answer these, it is not a real CI pipeline.

---

### Why CI pipelines are split into multiple jobs?

Instead of using one big job, CI pipelines are divided into separate jobs for:  
- Better readability  
- Easier debugging  
- Faster execution (parallelism)  
- Strict quality enforcement  

#### Jobs used in my pipeline:  
1. **lint** – quality validation  
2. **build** – compilation or packaging  
3. **test** – correctness verification  

Each job has a **single responsibility**, which is a best practice in real DevOps teams.

---

### Triggers (`PR` main vs `push` main vs `workflow_dispatch`)

**pull_request (to main)**  
- Ensures quality checks before merging  
- Prevents broken code from entering main branch  

**push (to main)**  
- Verifies final merged code  
- Confirms main branch remains stable  

**workflow_dispatch**  
- Allows manual execution  
- Useful for debugging or re-running pipelines

---

### `Lint` Job (Quality Gate)  

The `lint` job runs first and acts as a **gatekeeper**.  

**What it does:**
- Ensures all shell scripts are executable  
- Runs `shellcheck` to catch:  
  - syntax errors  
  - bad practices  
  - unsafe shell usage  

If `lint` fails:  
- build job does NOT run  
- test job does NOT run  

This saves time and prevents bad code from moving forward.

---

### Why Shellcheck is installed in CI?

Even if shellcheck exists locally, it is installed in CI because:  
- CI runners are fresh machines  
- CI must not depend on developer environments  
- Ensures same rules for all contributors  
- Prevents environment drift  

This is a real-world standard.

---

### Build Job

The build job:  
- Runs only if `lint` passes  
- Executes `build.sh`  
- Validates that the application can be built successfully  

The build job proves that the code is technically correct and usable.

---

### Test Job

The test job:  
- Runs only if `build` passes  
- Executes `test.sh`  
- Validates application behavior  

Testing ensures confidence that the change did not break existing functionality.

---

### Job Dependencies (`needs`)

The `needs` keyword is used to control job execution order.  

Example:  
- build → needs lint  
- test → needs build  

This ensures:  
- proper sequence  
- no wasted execution  
- clear pipeline logic  

---

### Artifacts:

Artifacts are files saved from CI runs for later inspection.  

**In this pipeline**:  
- log files (`*.log`) are uploaded  
- upload happens even if build or test fails  

This is done using:  
```yaml
if: always()
```
**Why this matters:**  
+ logs are required for debugging  
+ failures without logs are useless  
+ real production pipelines always preserve evidence  

---

### Why `if: always()` is used

By default, steps stop on failure.  

Using `if: always()` ensures:  
+ logs are uploaded even when jobs fail  
+ debugging is possible without re-running CI  
+ faster root-cause analysis  

---

### Handling missing Artifacts safely

To avoid pipeline failure when logs are missing:  
```yaml
if-no-files-found: warn
```

This makes the pipeline more robust and production-ready.

---

### Why `pull_requests` are preferred over direct `push`

Pull Requests are used because:  
+ CI runs before merge  
+ code reviews are possible  
+ main branch stays stable  
+ rollback and audit history is preserved  

Direct push to main is discouraged in professional environments.

---

### Files created / modified in Day-12

+ `cicd-learning/day12-ci-design.md`  
+ `cicd-learning/ci-simulation/lint.sh`  
+ `.github/workflows/ci.yml`  
+ `notes/day12-ci-pipeline-notes.md`  

---
