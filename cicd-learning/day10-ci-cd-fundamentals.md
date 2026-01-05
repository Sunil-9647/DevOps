## Day 10 - CI/CD Fundamentals

### What is CI/CD?
CI/CD stands for __Continuous Integration__ and __Continuous Delivery/Continuous Deployment__.

CI/CD is a process, not a tool.<br>
It's main purpose is to deliver software changes safely, repeatedly, and automatically without breaking production.

Before CI/CD, software teams:

+ Manually copied code to servers
+ Forgot steps
+ Deployed different versions on different machines
+ Broke production frequently
+ Were scared to deploy changes
+ CI/CD exists to remove human error and increase confidence in deployments.

---

### Why CI/CD Exists?
In real companies:

+ Many developers push code every day
+ Code changes must be tested quickly
+ Production downtime costs money
+ Manual deployments do not scale

CI/CD solves these problems by:

+ Automatically validating code
+ Catching errors early
+ Preventing broken code from reaching production
+ Making deployments predictable and repeatable

---

### What is Continuous Integration (CI)?
Developers frequently push code to a central repository where it is push code to a central repository where it is automatically built and tested to detect issues early.

CI answers one main question:<br>
    “Is this code safe to merge with the existing codebase?”

What CI does in real life:

+ Pulls latest code from Git
+ Builds the application
+ Runs tests
+ Checks basic quality rules
+ Stops immediately if something fails

*CI does NOT deploy to production*.<br>
*CI’s job is to protect the codebase*.

If CI fails:

+ The pipeline stops
+ Developers must fix the issue
+ Code is not merged

---

### What is Continuous Delivery vs Continuous Deployment?
__Continuous Delivery__

+ Code is always ready to deploy
+ Deployment requires manual approval
+ Used in:
	* Banks
	* Healthcare
	* Enterprises

__Continuous Deployment__

+ Code is automatically deployed after tests pass
+ No human approval
+ Used in:
	* Startups
	* SaaS products
	* High-automation teams

Important Point:<br>
    “CD can mean Delivery or Deployment depending on company risk tolerance.”

---

### CI/CD Pipeline Stages:

1. __Source (Commit)__: Developers commit code to a version control system (like Git). This action triggers the pipeline.
2. __Build__: The code is compiled, dependencies are gathered, and a deployable artifact is created.
3. __Test__: Automated tests (unit, integration, functional) run to check code quality and functionality.
4. __Staging (Delivery)__: The artifact is deployed to an environment mimicking production to catch issues before release.
5. __Deploy (Production)__: The final, validated artifact is released to live users

---

### CI simulation explained step-by-step Using Linux:
***To understand CI deeply, we simulated it using Linux shell scripts.***

__Bulid Script__(`build.sh`).
```bash
	#!/bin/bash
	echo "Building application..."
	sleep 2
	echo "Build successful"
```

Explanation:

+ `#!/bin/bash` → tells Linux to use Bash
+ `echo` → prints logs (CI logs)
+ `sleep` → simulates build time
+ Successful execution → exit code 0

If this script fails:

+ CI stops immediately
+ Tests do not run

__Test Script__(`test.sh`).
```bash
	#!/bin/bash
	echo "Running tests..."
	sleep 2
	echo "All tests passed"
```
Explanation:

+ Represents automated tests
+ If tests fail (exit 1), pipeline fails
+ CI prevents broken code from moving forward

---

### Commands used and WHY:

#### Why `chmod +x` is mandatory

Linux does not allow scripts to run without execute permission.

In CI:<br>
+ Scripts often fail due to missing permissions
+ This is a very common real-world issue

Giving execute permission ensures CI can run scripts.

#### Why We Used `&&` Instead of `;`

```bash
./build.sh && ./test.sh
```

+ `&&` means:
	+ Run next command only if previous succeeds
+ Enforces fail-fast behavior
+ Prevents tests from running on broken builds

Using `;`:

```bash
./build.sh ; ./test.sh
```

+ Both scripts run regardless of failure
+ Dangerous in CI
+ Can produce misleading results

Note:
	“CI pipelines must fail fast. That’s why `&&` is preferred over `;`.”

---

### Why CI Always Starts from a Clean Workspace?

CI does not trust:
+ Developer machines
+ Cached files
+ Previous runs

Starting fresh ensures:
+ Reproducibility
+ No hidden dependencies
+ Consistent results

If code works only on one machine, it is not production-ready.

---

### 5-6 real interview questions with answers:

Q1: Why do CI pipelines fail fast?

Answer:<br>
To stop broken code early, save resources, and prevent invalid test results.

Q2: What happens if tests fail in CI?

Answer:<br>
The pipeline stops and code is blocked from merging or deployment.

Q3: Why is CI important before deployment?

Answer:<br>
CI ensures code quality and stability before reaching any environment.

Q4: How do CI tools work internally?

Answer:<br>
They create a clean environment, run scripts, and check exit codes.

Q5: Why are shell scripts important in CI/CD?

Answer:<br>
Because CI tools execute scripts; understanding scripts means understanding CI.

---

