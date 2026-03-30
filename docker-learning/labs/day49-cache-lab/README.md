# Day-49 Cache Lab

## Purpose
This lab demonstrates how Dockerfile instruction order affects layer caching and rebuild speed.

## Concepts covered
- Docker build cache  
- bad vs good Dockerfile ordering  
- why dependency files should be copied before app source  
- why changing only app code should not reinstall dependencies  
- `.dockerignore` and build context hygiene  
- difference between `.gitignore` and `.dockerignore`  

## Files
- `app.py` -> simple Python app used for rebuild testing  
- `requirements.txt` -> dependency manifest  
- `Dockerfile.bad` -> broad `COPY . .` before dependency installation  
- `Dockerfile.good` -> dependency-first Dockerfile with better cache reuse  
- `.dockerignore` -> excludes unnecessary files from build context

## Dockerfile.bad
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
```

## Why Dockerfile.bad is bad

Because `COPY . .` happens before dependency installation.  
If a source file like `app.py` changes, Docker may invalidate the earlier copy layer and rerun `pip install` even when `requirements.txt` did not change.

## Dockerfile.good
```dockerfile
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

## Why Dockerfile.good is better

Because `requirements.txt` is copied before dependency installation.  
If only `app.py` changes, Docker can reuse the cached dependency-install layer and rebuild only the later source-code layer.

## Files used in the lab

### app.py
```python
print("Hello from Day-49 cache lab - version 2")
```

### requirements.txt
```
requests==2.32.3
```

### Build commands

#### First builds
```bash
docker build -f Dockerfile.bad -t day49-cache-bad:v1 .
docker build -f Dockerfile.good -t day49-cache-good:v1 .
```

#### Rebuild after changing only app.py
```bash
docker build -f Dockerfile.bad -t day49-cache-bad:v2 .
docker build -f Dockerfile.good -t day49-cache-good:v2 .
```

## What was observed

### Bad Dockerfile

After changing only `app.py`, the `pip install` step ran again.  
This showed that the bad instruction order caused unnecessary dependency reinstall.

### Good Dockerfile

After changing only `app.py`, the `COPY requirements.txt` and `RUN pip install` steps stayed cached.  
Only the later `COPY app.py` step ran again.

## .dockerignore used in the lab
```dockerignore
.git
__pycache__/
*.pyc
.venv/
notes/
screenshots/
```

## What .dockerignore improved

The lab intentionally created junk folders like:  
- `notes/`  
- `screenshots/`  
- `.venv/`

Before `.dockerignore`, those files increased the Docker build context.  
After `.dockerignore`, the build context became smaller and cleaner because Docker stopped sending those unnecessary files into the build.

## Important learning
- a Dockerfile is not good just because it builds successfully  
- instruction order directly affects cache reuse  
- source-code changes should not force dependency reinstall when dependencies did not change  
- `.dockerignore` reduces unnecessary build context noise  
- `.gitignore` does not control Docker build context

## Final conclusion

This lab proved that good Dockerfile ordering and clean build context handling make Docker builds faster, cleaner, and more reliable.
