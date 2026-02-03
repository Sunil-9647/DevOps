## Production Incident Flow

### Incident Lifecycle

Monitoring System
  |
  v
Alert Triggered
  |
  v
On-call Engineer
  |
  v
Incident Analysis  
  - Logs  
  - Metrics  
  - Recent Deployments
  |
  v
Decision Point
  |
  +--> Rollback to Stable Version
  |
  +--> OR Investigate Further
  |
  v
Service Restored
  |
  v
Postmortem Documentation

## Important Rule
Monitoring informs decisions.  
Rollback is a controlled human action.
