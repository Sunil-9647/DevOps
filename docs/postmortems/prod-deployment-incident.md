## Postmortem: Production Deployment Failure

### Incident summary
A production deployment failed, causing partial service disruption for users.

### Timeline
- 10:30 AM – Deployment to PROD triggered  
- 10:31 AM – Deployment job failed  
- 10:35 AM – Issue identified by on-call engineer  
- 10:40 AM – Rollback initiated  
- 10:45 AM – Service restored

### Impact
- Some users experienced errors  
- Deployment pipeline blocked  
- No data loss occurred

### Root cause
- Incorrect artifact version input during PROD deployment  
- Lack of validation before deployment

### Detection
- GitHub Actions deployment failure alert  
- User-facing error monitoring

### Resolution
- Rolled back to last stable version  
- Confirmed application health

### What went well
- Rollback pipeline worked as expected  
- Clear versioning enabled quick recovery

### What went wrong
- Manual input error  
- No pre-deploy validation

### Action items
- Improve version validation  
- Document rollback steps clearly  
- Add deployment checklist

### Lessons learned
Rollback is safer and faster than hotfix during incidents.
