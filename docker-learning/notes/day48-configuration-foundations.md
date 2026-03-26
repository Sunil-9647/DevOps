## Day 48 — Environment Variables and Configuration Discipline (Part 1)

### Objective of Day-48

Today I started learning how configuration should be handled in Docker and containerized applications. The focus was not just on “how to pass an environment variable,” but on understanding a much more important DevOps principle:

**The image should stay the same, while runtime configuration should change depending on the environment.**

This topic is important because in real projects, the application image is usually promoted across multiple environments such as development, staging, and production. If configuration values are hardcoded inside the image or source code, then the same image cannot be reused properly, and that breaks good CI/CD discipline.

---

### 1) Core principle: build once, configure at runtime

A Docker image should usually contain:

- the application code  
- dependencies  
- startup command  
- the fixed runtime setup that does not change between environments

But the image should usually not contain environment-specific runtime values such as:  
- database hostname  
- database port  
- database username  
- database password  
- application mode like development or production  
- log level  
- service endpoint values that differ between environments

**Why this matters**

If these values are baked into the image, then:  
- `dev` image becomes different from `prod` image  
- image promotion becomes difficult  
- rollback becomes less reliable  
- testing becomes less trustworthy  
- CI/CD discipline breaks

The correct pattern is:  
- build the image once  
- run the same image with different runtime configuration in each environment

This is aligned with the DevOps principle you already learned earlier:  
**build once, promote the same artifact.**

---

### 2) What configuration actually means

Configuration means values that tell the application how it should run in a particular environment.

Examples:  
- `DB_HOST=db`  
- `DB_PORT=5432`  
- `DB_NAME=appdb`  
- `DB_USER=appuser`  
- `APP_ENV=development`  
- `LOG_LEVEL=debug`  
- `PORT=8000`

These values are not the application logic itself. They are runtime instructions.

Simple distinction  
- **Code** = what the application is  
- **Configuration** = how the application should run here

This distinction is important because when code and configuration are mixed together, the application becomes harder to reuse across environments.

---

### 3) Why hardcoding runtime config in source code is bad

Suppose application code contains something like this directly:  
```Python
DB_HOST = "db"
DB_PORT = 5432
APP_ENV = "development"
```

This is a bad practice in real-world deployments.

#### Problems caused by hardcoding
1. Environment-specific values become trapped in code  
2. Code must be changed for different environments  
3. Even a small config change may require rebuild/redeploy  
4. Rollback becomes less trustworthy because image content differs  
5. Troubleshooting becomes harder  
6. Risk of accidentally hardcoding secrets increases

#### Better approach

The application should read such values at runtime from configuration sources, usually environment variables.

---

### 4) Environment variables as runtime configuration

The most common runtime configuration mechanism in Docker is the **environment variable**.

An environment variable is a key-value pair available to the process when the container starts.

Examples:  
```env
APP_ENV=development
DB_HOST=db
DB_PORT=5432
```

These values are given to the container when it starts, and the application reads them during runtime.

#### Why this is useful

Because the same image can behave differently depending on the runtime values it receives.

Example:  
- in development: `DB_HOST=db`  
- in production: `DB_HOST=prod-db`

Same image. Different runtime configuration. No rebuild needed.

---

### 5) `docker run -e` for passing runtime values

The most direct way to pass environment variables in plain Docker is with `-e`.

Example used in lab:  
```bash
docker run --rm -e APP_ENV=development -e DB_HOST=db -e DB_PORT=5432 alpine:3.20 env
```

**What this did**  
- started a temporary Alpine container  
- injected three runtime variables  
- ran the `env` command inside the container  
- printed the environment  
- removed the container after exit

**Output observed**  
The container correctly showed:  
- `APP_ENV=development`  
- `DB_HOST=db`  
- `DB_PORT=5432`

**Main lesson**

`-e` changes the container’s runtime environment, not the image itself.

---

### 6) Proving same image, different runtime values
I ran the same image two times:

#### First run
```bash
docker run --rm -e APP_ENV=development -e DB_HOST=db -e DB_PORT=5432 alpine:3.20 env
```

#### Second run
```bash
docker run --rm -e APP_ENV=production -e DB_HOST=prod-db -e DB_PORT=5432 alpine:3.20 env
```

**What changed**

Only the runtime values changed:  
- `APP_ENV`  
- `DB_HOST`

**What did not change**

The image remained the same:  
- `alpine:3.20`

**Main lesson**

We did not rebuild the image.  
We only changed runtime configuration.

That is the practical proof of:  
**same image, different runtime config.**

---

### 7) Why this matters for DevOps and CI/CD
If separate images are built just because configuration changes between dev and prod, then the promotion discipline becomes weak.

Correct approach:  
- one image artifact  
- different runtime configuration per environment

**Benefits**

- easier rollback  
- consistent testing across environments  
- cleaner promotion pipeline  
- fewer configuration surprises hidden inside image content  
- better alignment with CI/CD best practices

**Important correction**

This does not automatically make secrets safe.  
It only avoids baking config into the image. Secret handling still requires additional care.

---

### 8) Compose `environment:` — explicit variables in YAML
In Docker Compose, runtime variables can be written directly under `environment:`.

Lab example:  
```YAML
services:
  app:
    image: alpine:3.20
    environment:
      APP_ENV: development
      DB_HOST: db
      DB_PORT: "5432"
    command: env
```

**What happened**

When `docker compose up` was run, the container printed:  
- `APP_ENV=development`  
- `DB_HOST=db`  
- `DB_PORT=5432`  

**Meaning**

This proves that `environment:` injects variables into the running container environment.

**Use case**

This is useful when:  
- the number of variables is small  
- you want explicit config visible in the Compose file  
- service behavior should be easy to review directly in YAML

---

### 9) Compose `.env` — used for Compose substitution

Then I changed the Compose file to use placeholders:  
```YAML
services:
  app:
    image: alpine:3.20
    environment:
      APP_ENV: ${APP_ENV}
      DB_HOST: ${DB_HOST}
      DB_PORT: ${DB_PORT}
    command: env
```

and created a `.env` file:

```env
APP_ENV=development
DB_HOST=db
DB_PORT=5432
```

**What happened**

Compose substituted the placeholder values before creating the container.

So the actual flow was:  
`.env` -> Compose substitution -> `environment:` -> container

**Main lesson**

The container did not get the values just because `.env` existed.  
It got them because the Compose file explicitly referenced `${APP_ENV}`, `${DB_HOST}`, `${DB_PORT}` inside `environment:`.

That is a very important distinction.

---

### 10. Real lesson from typo in `.env`

In one test, I accidentally wrote:  
```env
APP_ENV=devlopment
```

instead of:  
```env
APP_ENV=development
```

Compose still passed that value exactly as written.

**Important lesson**

Docker and Compose do not understand my intention.  
They only pass the exact value I provide.

So:  
- environment injection can succeed  
- but the configuration can still be wrong

**Operational meaning**

A running container does not guarantee that configuration values are correct.  
This is a real-world lesson because many incidents come from wrong values, not from missing syntax.

---

### 11) Compose `env_file:` — direct file-to-container environment injection
Next, I used `env_file:` in Compose.

Example:  
```YAML
services:
  app:
    image: alpine:3.20
    env_file:
      - app.env
    command: env
```

with:  
```env
APP_ENV=development
DB_HOST=db
DB_PORT=5432
```

**What happened**

The container printed:  
- `APP_ENV=development`  
- `DB_HOST=db`  
- `DB_PORT=5432`

**Main lesson**

Here the flow was different:  
`app.env` -> `env_file:` -> container environment

This is not the same as `.env` placeholder substitution.

---

### 12) Difference between `.env` and `env_file:`
This is one of the most important distinctions in Day-48.

`.env`  
Used by Compose to substitute `${...}` variables in the Compose YAML.

`env_file:`  
Used by Compose to load variables from a file directly into the container environment.

**Why the distinction matters**

Because many think:  
“I created a `.env` file, so the container will definitely receive all variables.”

That is not always true.

The actual result depends on how the Compose file is written.

---

### 13) Compose variable defaults using `${VAR:-default}`

Then I tested fallback/default syntax in Compose.

Example:  
```YAML
services:
  app:
    image: alpine:3.20
    environment:
      APP_ENV: ${APP_ENV:-development}
      DB_HOST: ${DB_HOST:-db}
      DB_PORT: ${DB_PORT:-5432}
    command: env
```

with `.env` containing only:  
```env
APP_ENV=production
```

**Result observed**

The container received:  
- `APP_ENV=production`  
- `DB_HOST=db`  
- `DB_PORT=5432`

**Meaning**

Compose used:  

- actual value from `.env` for `APP_ENV`  
- fallback values for missing `DB_HOST` and `DB_PORT`

**Important lesson**

Defaults are resolved by Compose before the container starts.

---

### 14) When defaults are useful

Default values can be useful for:  
- local development  
- non-sensitive values  
- reducing friction in small labs  
- safe fallback values

Examples:  
- `APP_ENV=development`  
- `PORT=8000`  
- `DB_HOST=db`  
- `DB_PORT=5432`

These defaults can make development easier.

---

### 15) When defaults are dangerous
Defaults are dangerous for:  
- `DB_PASSWORD`  
- `SECRET_KEY`  
- API tokens  
- security-sensitive values  
- production-only critical values

**Why?**

Because silent fallback can hide a real configuration problem.

Example:  
- production variable is missing  
- Compose silently uses a weak or wrong fallback  
- application starts but behaves incorrectly or insecurely

In such cases, failing fast is better than quietly using a bad value.

---

### 16) Config success is not the same as application correctness
One of the biggest lessons from today is:

A container can:  
- start correctly  
- print environment variables  
- even appear healthy

and still the application may be misconfigured.

Examples:  
- hostname misspelled  
- wrong database name  
- wrong environment mode  
- wrong service endpoint  
- missing secret

So a real engineer must verify:  
- what values were actually injected  
- whether those values are semantically correct for the application

Not just whether Compose ran successfully.

---

### 17) Connection between Day-47 and Day-48

Day-47 taught networking:  
- which service talks to which  
- what hostname should be used  
- why `localhost` is wrong for cross-container communication

Day-48 teaches configuration:  
- where those hostnames and ports come from at runtime  
- how the application receives them  
- how dev and prod can differ without rebuilding images

**Example**

If networking design says:  
- API should reach DB by hostname `db`  
- DB port is `5432`

then runtime config should reflect that:  
```env
DB_HOST=db
DB_PORT=5432
```

If config says `DB_HOST=localhost`, then even correct networking design will fail at application runtime.

**Main lesson**  
Correct networking `+` wrong configuration `=` broken application.

---

### 18) Config vs secrets
Not every environment variable is equally sensitive.

#### Usually normal config
- `DB_HOST`  
- `DB_PORT`  
- `APP_ENV`  
- `LOG_LEVEL`  
- `PORT`

#### Usually sensitive / secret
- `DB_PASSWORD`  
- API tokens  
- access keys  
- secret keys

This distinction matters because:  
- normal config may safely use dev defaults  
- secrets usually require stricter handling  
- secrets should not be casually hardcoded or silently defaulted

Today’s learning focused on configuration discipline, while secret-handling discipline will be covered more deeply later.

---

### 19) What usually belongs in image vs runtime config

#### Usually belongs inside the image
- application code  
- installed dependencies  
- startup command  
- fixed runtime setup

#### Usually belongs in runtime config
- DB host  
- DB port  
- DB name  
- environment mode  
- log level  
- credentials  
- environment-specific endpoints

**Rule**

- Image contains what the application **is**  
- Runtime config contains how the application should **run here**

This rule is one of the most important DevOps habits.

---

### 20) Biggest lessons from Day-48 Part 1

The key things learned today are:  
- same image should be reused across environments  
- runtime config should change, not image contents  
- hardcoding environment-specific values in code is bad practice  
- `docker run -e` injects runtime env vars directly  
- Compose `environment:` writes container env vars in YAML  
- `.env` helps Compose fill `${...}` placeholders  
- `env_file:` loads variables into the container environment  
- `.env` and `env_file:` are not the same thing  
- `${VAR:-default}` provides fallback values  
- defaults are useful for safe development values  
- defaults are dangerous for secrets and critical values  
- successful container startup does not guarantee correct configuration

---

### 21) Final understanding statement for Part 1

Today I learned that configuration discipline in Docker is not just about syntax. It is about keeping environment-specific behavior outside the image and outside hardcoded source code, so the same image can be reused across dev, staging, and production. I also learned that Docker Compose has multiple ways to work with environment variables, and each one has a different purpose. Most importantly, I learned that configuration must be verified carefully because a container can start successfully even when the runtime values are wrong.

---
