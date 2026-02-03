## CI/CD Architecture (GitHub Actions)

### High-Level Flow

Developer  
  |  
  v  
Git Push / PR  
  |  
  v  
CI Pipeline (GitHub Actions)  
  - Lint  
  - Build  
  - Test  
  - Package  
  - Upload Artifact  
  |  
  v  
Artifact Store (GitHub Artifacts)  
  |  
  +--> CD - DEV (Auto / Fast feedback)  
  |  
  +--> CD - STAGING (Manual approval)  
  |  
  +--> CD - PROD (Manual + Versioned)  
  |  
  v  
Rollback Workflow (Manual, Version-based)

### Key Principles
- Build once, deploy many times  
- Same artifact promoted across environments  
- Human approval for higher environments  
