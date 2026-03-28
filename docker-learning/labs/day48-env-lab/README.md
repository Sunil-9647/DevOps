# Day-48 Env Lab

## Purpose
This lab demonstrates Docker Compose environment variable handling in simple and controlled way.

## Concepts covered
- `environment:`  
- `.env` for Compose variable substitution  
- `env_file:`  
- override behavior where `environment:` overrides overlapping keys from `env_file:`

## Files
- `compose.yaml` -> main Compose lab file  
- `.env.example` -> example file for Compose variable substitution  
- `app.env.example` -> example file for `env_file:` injection

## Important learning
- `.env` helps Compose substitute `${...}` values in YAML  
- `env_file:` loads variables into the container environment  
- `environment:` explicitly sets container environment values  
- if the same key is present in both `env_file:` and `environment:`, the value in `environment:` wins

## How to run
Copy the example env file if needed:

```bash
cp app.env.example app.env
docker compose up
```

## Expected result
The container prints environment variables and shows that:

- `DB_HOST` and `DB_PORT` come from `app.env`  
- `APP_ENV` is overridden by `environment:` in `compose.yaml`
