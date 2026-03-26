## Day 48 — Environment Variables and Configuration Discipline (Part 2)

### Objective of Part 2

In this part of Day-48, I learned the more dangerous and practical side of Docker configuration discipline. The focus was not just on passing variables, but on understanding:

- which value wins when the same variable is defined in multiple places  
- why empty values and missing values are not the same thing  
- the difference between Dockerfile `ARG` and `ENV`  
- why secrets must not be baked into Docker images  
- how runtime overrides can replace image defaults  

This part is important because many real-world configuration issues do not come from missing syntax. They come from misunderstandings about precedence, defaults, empty values, and build-time vs runtime behavior.

### 1) Why override and precedence matter

In real projects, the same variable may appear in more than one place.

Examples:  
- inside `env_file:`  
- inside Compose `environment:`  
- inside Dockerfile `ENV`  
- passed at runtime with `docker run -e`  
- or supplied through host/Compose substitution

If I do not know which one wins, then configuration becomes confusing and debugging becomes slow.

A common real-world mistake is:  
- changing one config source  
- expecting the container to use it  
- but another higher-priority source is overriding it

So a good DevOps engineer must always ask:  
**Where is this variable defined, and which definition takes precedence?**

---

### 2) Practical precedence learned in lab: `environment:` overrides `env_file:`

In this lab, I used:  
```YAML
services:
  app:
    image: alpine:3.20
    env_file:
      - app.env
    environment:
      APP_ENV: production
    command: env
```

and `app.env` contained:  
```env
APP_ENV=development
DB_HOST=db
DB_PORT=5432
```

**Result observed**  

The container printed:  
- `APP_ENV=production`  
- `DB_HOST=db`  
- `DB_PORT=5432`  

**What this proved**

This proved that:  
- `env_file:` was loaded correctly  
- but `environment:` overrode the overlapping key `APP_ENV`  
- non-overlapping values from `env_file:` stayed unchanged

**Main lesson**  
In the final running container, **explicit values in `environment:` override overlapping values coming from `env_file:`**.

This is a very important real-world behavior.

---

### 3) Override does not replace everything, only overlapping keys

Another important lesson from the same lab was that override behavior is selective.

Only this variable changed:  
- `APP_ENV`

These variables were not replaced:  
- `DB_HOST`  
- `DB_PORT`

They remained from `app.env`.

**Why this matters**

Because in real systems, it is common to have:  
- a base file with shared config  
- a service-specific override for only one or two values

That means partial override behavior is normal and useful.

**Main lesson**  
When one config source overrides another, it usually overrides only the keys it explicitly defines, not all variables.

---

### 4) Missing variable vs empty variable

A variable can be in three states:  
1. present with a value  
2. present but empty  
3. completely missing

These are not the same thing.

Example of present but empty:  
```env
DB_HOST=
```

Example of missing:  
- `DB_HOST` not defined at all

This distinction is small in appearance, but important in operations.

---

### 5) Why empty values are dangerous

If a required variable is empty, it may look like it exists, but it is still broken.

Example:  
- `DB_HOST=` exists  
- but it does not provide a usable hostname

This can cause problems like:  
- broken connection strings  
- runtime failures  
- confusing logs  
- validation being bypassed in weak checks

**Important operational lesson**

An empty required value can be more dangerous than a missing one, because it may silently pass through configuration layers and cause confusing behavior later.

---

### 6) Why missing values are often easier to detect

If a required variable is completely missing, many tools, scripts, or validation checks can fail early and clearly.

That is often better than having the variable present but empty.

**Example**

If `DB_HOST` is missing:  
- the app may fail fast  
- the problem is obvious

If `DB_HOST=` is empty:  
- the variable appears to exist  
- but the app may behave unpredictably  
- debugging becomes harde

**Main lesson**

For required configuration, an empty value is not harmless. It must be treated as a real config error.

---

### 7) Good habit: do not check only “whether variable exists”

A weak check is:  
- “Is the variable name present?”

A better check is:  
- Is the variable present?  
- Is it non-empty?  
- Is it the correct value?  
- Did it come from the correct source?  
- Was it overridden unexpectedly?

This is real configuration discipline.

---

### 8) Dockerfile `ARG` vs `ENV`

This was one of the most important concepts in Part 2.

At first glance, both look like variables in a Dockerfile, but they serve different purposes.

`ARG`

`ARG` is mainly for **build-time** values.

Example:  
```dockerfile
ARG APP_VERSION=1.0
```

This can be supplied during `docker build`.

`ENV`

`ENV` is for **environment variables in the image/runtime context.**

Example:  
```dockerfile
ENV APP_ENV=development
```

This becomes part of the image configuration and is available in running containers, unless overridden later.

---

### 9) Clean difference between `ARG` and `ENV`
`ARG`  
- exists mainly during image build  
- used to customize the build process  
- not the normal mechanism for runtime application configuration

`ENV`  
- becomes part of the image’s environment configuration  
- available inside containers created from the image  
- can still be overridden at runtime

**Main lesson**

Build-time and runtime are different stages.  
`ARG` belongs mainly to build-time.  
`ENV` is visible in the running container.

---

### 10) Practical `ARG` vs `ENV` lab

I created this Dockerfile:  
```dockerfile
FROM alpine:3.20

ARG APP_VERSION=1.0
ENV APP_ENV=development

RUN echo "Build-time APP_VERSION=$APP_VERSION" > /build-info.txt

CMD sh -c 'echo "Runtime APP_ENV=$APP_ENV"; echo "Contents of /build-info.txt:"; cat /build-info.txt'
```

Then I built it with:  
```bash
docker build -t day48-arg-env-demo --build-arg APP_VERSION=2.5 .
```

and ran it with:  
```bash
docker run --rm day48-arg-env-demo
```

**Result observed**

The container printed:  
- `Runtime APP_ENV=development`  
- `Build-time APP_VERSION=2.5`

**What this proved**

This proved that:  
- `ARG APP_VERSION=2.5` was used during image build  
- the build result was written into `/build-info.txt`  
- `ENV APP_ENV=development` existed in the running container

So build-time and runtime behavior were clearly separated.

---

### 11) Build-time `ARG` can affect the image artifact
One very important lesson is that even though `ARG` is mainly a build-time value, it can still influence what gets baked into the image.

In the lab:  
- `APP_VERSION` was used during the `RUN` step  
- that value was written into `/build-info.txt`  
- the file remained inside the final image

So the correct understanding is:  
- `ARG` is not a runtime env mechanism  
- but it can affect the final built image if it is used during build steps

This is a subtle but important distinction.

---

### 12) Dockerfile `ENV` is only a default, not a final law
Another very important lesson from the lab:  

Even though the Dockerfile had:  
```dockerfile
ENV APP_ENV=development
```

I later ran:  
```bash
docker run --rm -e APP_ENV=production day48-arg-env-demo
```

**Result observed**

The container printed:  
- `Runtime APP_ENV=production`  
- but `/build-info.txt` still showed:  
    - `Build-time APP_VERSION=2.5`

**What this proved**

This proved:  
- Dockerfile `ENV` provides a default runtime value  
- runtime `-e` can override that default  
- build-time artifact created by `ARG` remains unchanged

**Main lesson**

`ENV` in Dockerfile is not permanent. It can be overridden at runtime.

---

### 13) Correct mental model after the lab

After the lab, the correct mental model is:  

`ARG`  
- used while building the image  
- can shape built artifacts  
- not the normal runtime config mechanism

**Dockerfile `ENV`**

- sets default environment values in the image  
- available in running containers  
- can be overridden at runtime

**Runtime `-e` or Compose runtime config**

- can replace Dockerfile defaults  
- should be used for environment-specific values

This is the correct engineering understanding.

---

### 14) Why secrets should not be baked into the image
A very important warning from Part 2 is that secrets must not be put into Dockerfile `ENV` or otherwise baked into image layers.

Bad example:  
```dockerfile
ENV DB_PASSWORD=supersecret
```

This is poor practice.

**Why it is dangerous**

Because:  
- the secret becomes part of image metadata or layers  
- anyone with access to the image may inspect it  
- the secret may appear in image history or environment inspection  
- changing the secret may require rebuilding the image  
- the same image becomes less portable and less safe across environments

**Main lesson**

Sensitive values such as passwords, tokens, and secret keys should not be baked into the image.

---

### 15) Safe use of `ARG`, careful use of `ENV`, and runtime injection for real config

**`ARG` should be used for**

- build customization  
- version values  
- non-secret build parameters

**Dockerfile `ENV` can be used carefully for**

- fixed non-sensitive defaults  
- base runtime behavior  
- settings that do not vary by environment

**Runtime injection should be used for**

- environment-specific values  
- DB connection details  
- environment mode differences  
- secrets and credentials  
- staging/prod-specific behavior

This is the correct maturity model.

---

### 16) Build-time values and runtime values must not be confused

This part of Day-48 taught that configuration problems often happen because engineers mix build-time and runtime ideas.

**Wrong thinking**

- using `ARG` as if it is normal runtime app configuration  
- putting secrets into Dockerfile `ENV`  
- baking environment-specific values into the image

**Correct thinking**

- use build-time values only for build concerns  
- use runtime config for environment-specific behavior  
- keep the image reusable across environments

This distinction is one of the most important DevOps habits.

---

### 17) Extra practical lesson: lab discipline also matters

During the ARG/ENV demo, I ran the build in the older `day48-env-lab` folder instead of a separate `day48-arg-env-lab` folder.

This still worked, but it was not good lab discipline.

**Why separate lab folders are better**

Because mixing experiments in one folder can create:  
- accidental file reuse  
- confusion during review  
- overwriting of unrelated test files  
- harder understanding later

**Main lesson**

Even while learning, folder structure and experiment isolation matter.

---

### 18) Warning seen during build: shell-form CMD vs JSON-form CMD
While building the ARG/ENV demo image, Docker showed this warning:  
- `JSONArgsRecommended`

This happened because the Dockerfile used:  
```dockerfile
CMD sh -c '...'
```

This is called shell-form `CMD`.

**Why Docker warns about it**

Because JSON/exec form is often better for signal handling and process behavior.

**Important note**

For this tiny teaching lab, the shell-form `CMD` was acceptable.  
But the warning itself is useful and should not be ignored in real projects.

**Main lesson**

Even simple teaching labs can expose good production lessons.

---

### 19) Biggest lessons from Day-48 Part 2

The main things I learned in this part are:  
- configuration precedence matters  
- `environment:` overrides overlapping keys from `env_file:`  
- non-overlapping keys remain from the lower source  
- missing and empty values are not the same  
- empty required values can be more dangerous than missing ones  
- `ARG` is mainly for build-time  
- `ENV` is available in running containers  
- Dockerfile `ENV` is only a default and can be overridden at runtime  
- build-time `ARG` can still shape final image artifacts  
- secrets must not be baked into Docker images  
- build-time and runtime configuration must not be mixed carelessly

---

### 20) Final understanding statement for Part 2

In this part of Day-48, I moved from basic environment variable usage to real configuration control thinking. I learned that it is not enough to know how to pass values into containers. I also need to understand which source wins, whether a value is missing or empty, whether the value belongs to build-time or runtime, and whether a secret is being exposed incorrectly inside the image. This is important because many real deployment bugs come from configuration confusion, not from application code itself.

---

### 21) Combined practical conclusion from Day-48 Part 2

The most important practical conclusion is this:  
- build-time values shape the image  
- runtime values shape the container behavior  
- image defaults can be overridden at runtime  
- secrets should stay out of image layers  
- configuration must be verified carefully, not assumed

That is the correct DevOps mindset for Docker configuration discipline.

---

