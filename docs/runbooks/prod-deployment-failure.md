## Runbook: Production Deployment Failure

### Alert Trigger
- PROD deployment job failed in GitHub Actions  
- Deployment stuck or timed out  
- Health checks failing after deployment

### Impact
- New version not live  
- Possible partial outage  
- Risk of user-facing errors

### Immediate Actions
1. Stop further deployments  
2. Do NOT retry blindly  
3. Inform on-call / team channel

### Diagnosis Steps
1. Open GitHub Actions → Deploy to PROD logs  
2. Identify failure stage:  
   - Artifact download  
   - Extraction  
   - Permission issues  
   - Service start failure  
3. Check last successful PROD version

### Decision
- If deployment never completed → keep current PROD  
- If deployment partially applied → consider rollback

### Mitigation
- Abort pipeline  
- Rollback to last known stable version if required

### Recovery
- Confirm service health  
- Validate user flows  
- Close incident  

### Notes
Never fix production directly during an incident.
