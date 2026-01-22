## Day 14 — Notes: Artifact Consumption + Deploy Simulation (CI → CD Flow)

### 1. Day-14 Objective  
The goal of Day-14 was to prove the CI → CD handshake:  
+ CI produces a reusable build artifact (ZIP)  
+ A separate job (deploy simulation) downloads and consumes that artifact  
+ No rebuild happens in the deploy job  

Key idea:  
> Jobs are isolated. They cannot share files unless we pass artifacts.

---

### 2. Why jobs are isolated in GitHub Actions?  
Each job runs on a fresh runner VM.  
So files created in `build` job are NOT available automatically in `deploy-sim` job.  

This is why we need:  
+ `actions/upload-artifact` in build job  
+ `actions/download-artifact` in deploy job  

Artifacts are the bridge between jobs.

---

### 3. Deploy Simulation Job (CD simulation)  
A new job was added:

+ Job name: `deploy-sim`  
+ `needs: [ build, test ]` ensures it runs only after:  
  - build succeeded and artifact exists  
  - tests succeeded (quality gate)  

Main steps in deploy-sim:  
1. Download artifact:  
   - `actions/download-artifact@v4`  
2. Inspect downloaded files:  
   - `ls` to confirm zip exists  
3. Unzip artifact into `extracted/`  
4. Copy extracted build output to a fake environment folder:  
   - `deploy-env/dev/`  
5. Print deployed files and contents as evidence:  
   - shows version.txt and app.txt  

This simulates deployment by consuming the artifact, not rebuilding.

---

### 4. Common Day-14 Failures & Fixes (real debugging)

#### 4.1 Folder name mismatch (typo)  
Issue:  
+ Download path used one folder name but later steps referenced a different folder name  
Example:  
+ created: `download-artifact`  
+ referenced: `downloaded-artifact`  

Fix:  
+ Use one consistent folder name across all steps.

Lesson:  
> Path mismatches are one of the most common CI/CD failures.

---

#### 4.2 Wrong command typo (`la` vs `ls`)  
Issue:  
+ Using `la -la` instead of `ls -la` causes command-not-found and pipeline fails.

Fix:  
+ Correct command to `ls`.

Lesson:  
> Even 1-character typos break pipelines. CI/CD is strict.

---

#### 4.3 Unzip failed due to multiple zip matches  
Issue:  
+ `download-artifact/*.zip` matched more than one zip:  
  - SHA zip (correct)  
  - `app-build-local.zip` (leftover local file)  
+ Unzip behaved unexpectedly and failed with exit code 11.  

Fix options:  
1. Unzip only one zip file (prefer SHA zip)  
2. Prevent local.zip from being uploaded at all  

In our pipeline:  
+ we selected SHA zip (ignore local)  
+ we also cleaned old artifacts in build job before packaging so wildcard upload does not include local files.  

Lesson:  
> Never assume only one file matches a wildcard. Always be explicit for deployment steps.

---

### 5. Why `app-build-local.zip` existed in CI  
Root cause:  
+ Local artifact zip was present in workspace/repo and got included by wildcard upload:  
  - upload path: `ci-artifacts/*.zip`

Fix:  
+ Clean artifact directory before packaging in CI:  
  - `rm -rf ci-artifacts`

Lesson:  
> Wildcards are convenient but dangerous if your workspace contains extra files.

---

### 6. Evidence of Successful Deploy Simulation  
The deploy job printed:  
+ `deploy-env/dev/dist/version.txt`:  
  - includes `BUILD_COMMIT=<sha>`  
  - includes `BUILD_TIME_UTC=<timestamp>`  
+ `deploy-env/dev/dist/app.txt`:  
  - contains “Hello from CI build output”  

This proves:  
+ CD simulation consumed CI artifact  
+ No rebuild was needed in deploy job  

---

### 7. Key Takeaways of Day-14  
1. CI builds artifacts; CD consumes artifacts  
2. Jobs are isolated; artifacts connect jobs  
3. Use `needs` to enforce correct flow (gates)  
4. Avoid hardcoding artifact names (use SHA-based selection)  
5. Avoid unsafe wildcards in deployment steps  
6. Debugging CI/CD requires reading logs carefully and validating paths  

---
