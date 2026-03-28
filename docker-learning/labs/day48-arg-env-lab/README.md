# Day-48 ARG vs ENV Lab

## Purpose
This lab demonstrates the difference between Dockerfile `ARG`, Dockerfile `ENV`, and runtime override with `docker run -e`.

## Concepts covered
- `ARG` is mainly for build-time  
- `ENV` becomes available in running containers  
- runtime `-e` can override Dockerfile `ENV`  
- build-time `ARG` can still affect the image artifact

## Files
- `Dockerfile` -> small demo image showing build-time and runtime variable behavior

## Build command
```bash
docker build -t day48-arg-env-demo --build-arg APP_VERSION=2.5 .
```

## Run command
```bash
docker run --rm day48-arg-env-demo
```

## Runtime override example
```bash
docker run --rm -e APP_ENV=production day48-arg-env-demo
```

## Expected result
- default run shows `APP_ENV=development`  
- runtime override shows `APP_ENV=production`  
- `/build-info.txt` keeps the build-time value `APP_VERSION=2.5`

