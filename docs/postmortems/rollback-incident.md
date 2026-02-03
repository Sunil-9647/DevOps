## Postmortem: Production Rollback Event

### Incident summary
A rollback was executed after a faulty production deployment.

### Timeline
- 11:00 AM – New version deployed  
- 11:02 AM – Error rate increased  
- 11:05 AM – Rollback decision made  
- 11:07 AM – Rollback completed  
- 11:10 AM – System stabilized

### Impact
- Short user disruption  
- No permanent impact

### Root cause
- New code introduced unexpected behavior  
- Issue was not caught in staging

### Detection
- Monitoring alerts  
- User reports

### Resolution
- Rolled back to last stable artifact  
- Confirmed system health

## What went well
- Versioned artifacts enabled fast rollback  
- Human approval prevented wrong rollback

## What went wrong
- Insufficient test coverage  
- Staging did not catch the issue

### Action items
- Improve staging test scenarios  
- Add monitoring-based deployment gates

## Lessons learned
Manual rollback decisions are safer under pressure.
