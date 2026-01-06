## Day 10 - CI Fundamentals & Failure Logic

### What is Continuous Integration (CI)?

Continuous Integration (CI) is a software development practice where developers frequently integrate code changes into a shared repository, and every integration is automatically validated by running builds and tests.

The goal of CI is not automation for the sake of automation, but to catch problems early, when they are small, cheap, and easy to fix.

In real-world teams, CI runs:

+ Every time code is pushed  
+ Every time a pull request is opened  
+ Sometimes on a schedule (nightly builds)  

CI acts as a gatekeeper that decides whether code is healthy enough to move forward.

---

### Why CI exists?

Before CI:  
+ Developers merged code manually  
+ Bugs appeared days or weeks later  
+ Finding the cause was painful  
+ Production failures were common  

With CI:  
+ Errors are detected within minutes  
+ Broken code is rejected immediately  
+ Teams move faster with confidence  

CI replaces human checking with machine discipline

---

### Core principle of CI: Fail Fast
CI pipelines follow a __fail-fast principle__.

This means:
+ If any stage fails, the pipeline stops immediately  
+ No further stages are executed  
+ Downstream work is prevented  

__Why fail fast is critical__

Running later stages after a failure:  
+ Wastes time and resources  
+ Produces misleading results  
+ Hides the real root cause  

Fail fast ensures:  
+ Fast feedback  
+ Clear failure reason  
+ Clean debugging  

---

### Exit Codes — the language CI understands
CI systems do not understand logs or text output.  
They understand exit codes.

Exit code rules:  

+ `0` → Success  
+ `non-zero` (1, 2, 127, etc.) → Failure  

When a script exits with a non-zero code:  
+ CI immediately marks the step as failed  
+ Pipeline execution stops  

Example:
```bash
exit 0
exit 1
```
This is why exit codes are more important than printed messages.

---

### Pipeline Stages
A basic CI pipeline is divided into stages.

```bash
Code → Build → Test → Quality Checks → Artifact → Deploy
```

Typical stages:  
1. **Checkout** – Fetch source code  
2. **Build** – Compile or package the application  
3. **Test** – Run automated tests  
4. **Package** – Create artifacts (optional)  
5. **Deploy** – Release to environment (later stages)  

Each stage depends on the success of the previous stage.  

---

### `&&` vs `;` — why CI uses `&&`
Using `&&`
```bash
./build.sh && ./test.sh
```

Behavior:  
+ test.sh runs only if build.sh succeeds  
+ If build fails → test never runs  

This matches CI’s fail-fast design.

Using `;`
```bash
./build.sh ; ./test.sh
```

Behavior:  
+ Both scripts run regardless of success or failure  
+ Tests may run on broken builds  
+ Results are unreliable  

CI pipelines should not use `;`

---

### Clean environment rule in CI
CI systems never trust local machines.

Every pipeline run starts from:  
+ A clean directory  
+ Fresh dependencis  
+ No leftover files  
+ No cached state (unless explicitly configured)  

Reason:  
+ Ensures reproducibility  
+ Prevents “works on my machine” problems  
+ Guarantees consistency across environments  

---

### Why CI pipelines are deterministic

CI pipelines must produce the same result when run:

+ Today or tomorrow  
+ On any machine  
+ By any developer  

If the result changes:  
+ CI configuration is broken  
+ Environment is leaking state  
+ Debugging becomes impossible  

---

### Real-World CI failure scenario
**Scenario**:  
A developer pushes code that breaks compilation.

What CI does:  
1. Build stage runs  
2. Build fails with exit code 1  
3. Pipeline stops  
4. Tests are skipped  
5. Developer gets instant feedback  

What CI prevents:  
+ Running useless tests  
+ Wasting CPU time  
+ Deploying broken code  

---

### Questions with Answers:

Q1: Why do CI pipelines stop when a command exits with non-zero?

Answer:   
Because CI systems rely on exit codes to determine success or failure, and a non-zero exit indicates an invalid state that makes downstream stages unreliable.

Q2: Why should tests not run if build fails?

Answer:   
Because tests assume a valid, built artifact. Running tests on a failed build produces misleading results and violates pipeline correctness.

Q3: Why does CI start from a clean environment every time?

Answer:   
To ensure reproducibility, prevent hidden dependencies, and eliminate machine-specific behavior.

Q4: Why is && preferred over ; in CI scripts?

Answer:   
Because && enforces fail-fast behavior by stopping execution when a command fails, aligning with CI pipeline logic.

---
