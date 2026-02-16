## Day 11 — Environment Variables & Secrets

### Definitions:

#### What is Environment variable?

A key/value pair given to a running program from the outside. Used to configure runtime behavior (for example: `PORT=8080`, `APP_ENV=production`). Not part of the code — the program reads them at runtime.  

#### What is Secret?

A special kind of environment variable that contains sensitive values (passwords, API keys, cloud credentials). Secrets must never appear in source code or be committed to version control. CI systems treat secrets specially (encrypted at rest, masked in logs, injected at runtime).  

---

### Why use environment variables?

+ **Separation of code and configuration**. Same codebase runs in dev/stage/prod just by changing env vars.  
+ **Avoid hardcoding**. Hardcoded values force code changes for every environment and leak sensitive data.  
+ **Rotation & management**. Changing a secret doesn’t require editing or redeploying code when secrets are managed externally.  

---

### How programs read environment variables (examples)

+ Bash: `echo "$DB_PASSWORD"`  
+ Python: `import os; os.getenv("DB_PASSWORD")`  
+ Node: `process.env.DB_PASSWORD`  
CI simply sets these values in the runner environment — your program reads them as usual.  

---

### Where secrets live (GitHub Actions)

+ **Repo settings → Settings → Secrets and variables → Actions**  
+ Secrets are stored encrypted, controlled by GitHub permissions, and referenced in YAML. They are **never** placed directly in **YAML** as literal values.  

---

### YAML mapping — safe patterns

+ **Workflow-level (global)**

`env:APP_ENV: productionLOG_LEVEL: infoDB_PASSWORD: ${{ secrets.DB_PASSWORD }}   # permitted, but wide scope`  
**When to use:** only for non-sensitive shared values. If you place secrets here they are available everywhere — OK but larger blast radius.  

+ **Job-level (better)**

`jobs:build:runs-on: ubuntu-latestenv:BUILD_MODE: releaseDB_PASSWORD: ${{ secrets.DB_PASSWORD }}`  
**When to use:** secrets needed only by a specific job. Narrower scope = safer.  

+ **Step-level (best practice for secrets)**

`- name: Run migrationenv:DB_PASSWORD: ${{ secrets.DB_PASSWORD }}run: ./migrate.sh`  
**When to use:** limit secret lifetime and scope to the minimal step that requires it.  

---

### How secrets behave in logs

+ If a secret value is printed, GitHub Actions masks it in logs (e.g., shows `*****`).  
+ Masking is automatic but not perfect: avoid printing secrets intentionally. Masking prevents accidental exposure, but is not a substitute for scoping and least privilege.  

---

### Secrets lifecycle & scopes in GitHub

+ **Repo-level secrets** — available for that repo  
+ **Environment secrets** — bound to an environment (e.g., `production`) and can require approvals  
+ **Organization-level secrets** — can be shared across repos with access controls  
Use the most restrictive scope that meets your needs.  

---

### Principle of Least Privilege (`PLP`)

+ Give the smallest amount of access for the shortest time.  
+ Example: deploy job needs AWS creds — do not give those creds to build or test jobs.  

---

### Common beginner mistakes (and how to fix them)

1. **Hardcoding secrets** in code or `.env` files → fix: remove, rotate, and store in GitHub secrets.  
2. **Using secrets as global workflow env** unnecessarily → fix: move to step/job-level.  
3. **Echoing secrets in logs** — even if masked → remove `echo $SECRET` calls.  
4. **Committing** `.env` or `credentials.*` → use `.gitignore` and secrets manager.  
5. **Using cache to pass sensitive artifacts** (wrong) — use artifacts, not cache.  

---

### How to add secrets in GitHub (quick steps)

1. Repo → Settings → Secrets and variables → Actions  
2. Click **New repository secret**  
3. Give it a clear name (uppercase, underscores) and paste value  
4. Use `$ {{ secrets.NAME }}` in YAML  

If you need environment-level protection:  
+ Repo → Settings → Environments → add environment → add secrets for that environment.  

---

### Practical checklist before pushing any YAML that uses secrets

+ Secrets are stored in GitHub, not in code.  
+ Secrets referenced in YAML using `${{ secrets.NAME }}`.  
+ Scope secrets as narrowly as possible (step-level preferred).  
+ No `echo $SECRET` or logging secrets.  
+ Review workflow for unnecessary broad env scopes.  
+ Use environment-level secrets for prod and require approvals if needed.  

---

### Quick recovery note (if you accidentally commit a secret)

1. Remove the secret from history (`git rm`, `git commit --amend`, and consider `git filter-branch` or `git filter-repo` for deep history).  
2. Rotate the secret immediately at the provider (rotate API key/password).  
3. Revoke the leaked secret and create a new one.  
4. Use `git-secrets` or a pre-commit hook to detect future leaks.  

---

### Questions with Answers:

Q1: Why not store secrets in code?  

Answer:  
Code is versioned, shared, and often visible. Hardcoded secrets leak easily (PRs, forks) and prevent rotation. Secrets must be stored and rotated outside source control.  

Q2: How does GitHub avoid secrets appearing in logs?  

Answer:  
GitHub masks any detected secret matching a stored secret. Masked values show as ***. Still, don’t print secrets as a practice.  

Q3: When do you scope secrets at job-level vs workflow-level?  
Answer:  
Prefer job- or step-level scoping. Use workflow-level only for non-sensitive shared config. Narrow the scope to minimize blast radius.  

Q4: What is the difference between environment variables and secrets?  
Answer:  
Environment variables are config (plain text); secrets are sensitive variables encrypted at rest, masked in logs, and injected securely at runtime.  

---
