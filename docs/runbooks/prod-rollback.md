## Runbook: Production Rollback (very important)

### When to Rollback
- User-facing errors after deployment  
- Increased error rate or latency  
- Business-critical functionality broken

### Preconditions
- A previous stable version exists  
- Rollback pipeline is available  
- Approval from on-call lead (if required)

### Rollback Steps
1. Identify last stable version:  
   - Check previous successful PROD deploy  
2. Trigger Rollback PROD workflow  
3. Provide version input (example: app-v-62be9cc)

### Validation
- Monitor logs  
- Verify key user actions  
- Check alerts recovery

### Post-Rollback
- Inform stakeholders  
- Freeze new deployments  
- Start root cause analysis

### Important Rule
Rollback is preferred over hotfix during incidents.
