## Runbook: High Error Rate / User Impact

### Alert Trigger
- >5% login failures for 10 minutes  
- Spike in 5xx errors  
- Customer complaints

### Impact
- Direct user impact  
- Revenue risk  
- SLA breach possible

### Immediate Actions
1. Acknowledge alert  
2. Pause deployments  
3. Check monitoring dashboards

### Diagnosis
1. Confirm issue is real (not noise)  
2. Identify affected services  
3. Check recent deployments

### Decision
- If linked to latest deployment → rollback  
- If infra-related → mitigate infra issue

### Mitigation
- Rollback if needed  
- Scale resources if required

### Resolution
- Confirm alert recovery  
- Update incident channel
