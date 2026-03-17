## Day 41 — Wheel-Based Multi-Stage Build for Python (and Why It Was Not Better for This Project)

### Goal of Day-41
The goal of this day was to try a more realistic Python multi-stage build pattern using **wheel files** instead of copying a full virtual environment.

On Day-40, the first multi-stage approach copied an entire `/opt/venv` into the runtime image. That worked technically, but it made the image larger than the existing production image.

So Day-41 was about testing a better Python pattern:  
+ builder stage prepares wheel files  
+ runtime stage installs packages from wheels  
+ then we measure the result honestly

---

### 1) What is a wheel in Python?
A wheel (`.whl`) is a built Python package format.

It is like a ready-to-install package bundle.  
Instead of re-downloading and resolving everything during runtime image build, pip can install directly from wheel files.

This makes wheel-based builds a common pattern in Python container workflows.

---

### 2) Why wheel-based multi-stage is useful in general
Wheel-based multi-stage builds are useful because they separate:

#### Builder stage
+ fetch/build package artifacts  
+ prepare wheels

#### Runtime stage
+ install only from those wheel files  
+ avoid contacting package indexes directly  
+ keep build preparation separate from runtime behavior

This can be useful when:  
+ packages require compilation  
+ build dependencies are heavy  
+ a clean separation between build and runtime is needed

---

### 3) What we implemented
We created a two-stage Dockerfile.

#### Builder stage
+ started from `python:3.12-slim`  
+ copied requirements files  
+ used:  
```bash
pip wheel --no-cache-dir --wheel-dir /wheels -r requirements-${TARGET}.txt
```

This produced wheel files under `/wheels`.

#### Runtime stage
+ started from a fresh `python:3.12-slim`  
+ copied `/wheels` from builder  
+ copied requirements files  
+ installed packages using:  
```bash
pip install --no-cache-dir --no-index --find-links=/wheels -r requirements-${TARGET}.txt
```
+ removed `/wheels`  
+ copied app code  
+ kept non-root user, healthcheck, and CMD

This was a valid wheel-based multi-stage pattern.

---

### 4) What we expected
The expectation was:  
+ cleaner runtime stage than copying a full virtual environment  
+ maybe smaller final image than the first multi-stage attempt  
+ maybe a practical improvement over the original production image

This was the hypothesis.

---

### 5) What actually happened
After building the new image, the results were:  
+ `py-api:prod` → 199MB  
+ `py-api:ms1` → 243MB  
+ `py-api:ms2` → 243MB

So the wheel-based multi-stage image still did not beat the current production image.

This means the more advanced pattern worked technically, but did not improve the final image for this project.

---

### 6) Why `ms2` stayed large
The Docker history made the reason clear.  
Important layers in py-api:ms2 were:  
+ `COPY /wheels /wheels` → about 8.6MB  
+ `RUN pip install ...` → about 37.9MB

This is the key lesson:  
**Docker layers are immutable**  
When files are copied into one layer, that layer keeps them.  
If those files are deleted later in another layer, they disappear from the final container view, but the earlier layer still exists in image history and still contributes to image size.

So even though the Dockerfile used:  
```bash
rm -rf /wheels
```

the wheel files were already stored in a previous image layer.

This is why the runtime image still carried the weight of:  
+ wheel files layer  
+ installed package layer

---

### 7) Compare with the original production image
The original production image had a simpler dependency layer:  
+ direct `pip install` layer → about **16.7MB**

That was much smaller than the combined wheel-related layers in `ms2`.

So for this project, the original `py-api:prod` image remained the best practical result.

---

### 8) The most important lesson
The lesson of Day-41 is not “**wheel builds are bad**.”

The real lesson is:  
> Advanced patterns must be measured in the real project.

Wheel-based multi-stage is a valid Python pattern, but it does not automatically guarantee:  
+ smaller image  
+ better runtime image  
+ worth-the-complexity improvement

In this specific FastAPI project:  
+ dependencies are already simple  
+ no heavy OS build tools were installed  
+ the original production image was already lean

So the advanced pattern added complexity without improving the final image.

---

### 9) Final decision for this project
For this specific application, the correct decision is:  
+ keep `py-api:prod` as the real production image  
+ keep `py-api:ms1` and `py-api:ms2` only as learning experiments

This is the correct outcome because it is based on:  
+ measurement  
+ comparison  
+ actual image history  
+ not assumptions

---

### 10) Why Day-41 still matters
Even though we did not adopt `ms2`, Day-41 was still very valuable because it taught:  
1. how wheel-based Python multi-stage builds work  
2. how Docker layering affects final image size  
3. why deleting files in a later layer does not remove the size of earlier layers  
4. why production decisions must be based on measured results

This is real DevOps thinking.

---

### Commands used

**Build wheel-based multi-stage image**
```bash
docker build --build-arg TARGET=prod -t py-api:ms2 .
```

**Compare image sizes**
```bash
docker images | grep 'py-api'
```

**Inspect image layer history**
```bash
docker history py-api:ms2
docker history py-api:prod
```

---

### Final takeaway
Wheel-based multi-stage builds are a real Python production pattern, but for this small FastAPI app they did not produce a better final image than the current single-stage production Dockerfile. The right decision is to keep the smaller and simpler `py-api:prod` image and move forward with a measured, disciplined approach.

---
