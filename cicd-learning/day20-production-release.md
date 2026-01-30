## Day 20 — Production Releases & Incident Control

### Why Production is different?  
`PROD` serves:  
+ Real users  
+ Real traffic  
+ Real money  
+ Real reputation

Mistakes in PROD:  
+ Cause downtime  
+ Break trust  
+ Can lead to financial and legal impact

Because of this:  
>Production releases must be slow, intentional, and controlled.

---

### The Golden rule of Production  
>PROD must never auto-deploy

Even if:  
+ CI is green  
+ STAGING passed  
+ Tests look good

Automation cannot judge:  
+ Business timing  
+ User impact  
+ Risk tolerance

Only humans can.

---

### Who controls `PROD` releases  
Production releases are decided by:  
+ Senior engineers  
+ Release managers  
+ On-call engineers  
+ Tech leads

The pipeline only **executes** the decision.

Separation of responsibility:  
+ CI/CD system = execution  
+ Humans = accountability

---

### Production Release checklist  
Before PROD deployment, teams verify:  
+ Correct artifact version  
+ STAGING validation passed  
+ Rollback plan exists  
+ Monitoring dashboards ready  
+ On-call engineer available  
+ No ongoing incidents  
+ Approval recorded

If rollback plan is missing → **no release**

---

### Production Deployment Strategies (conceptual)  
**In-place deployment**  
+ Replace old version directly  
+ Simple but risky  
+ Possible downtime

**Blue-Green deployment**  
+ Two identical environments  
+ Switch traffic after validation  
+ Fast rollback

**Canary deployment**  
+ Gradual rollout to users  
+ Monitor metrics  
+ Safest but complex

---

### What Rollback really means  
Rollback is **not**:  
+ Reverting commits  
+ Writing quick fixes  
+ Debugging during outage  
Rollback is:  
>Redeploying the last known-good artifact immediately.

Priority during incidents:  
1. Restore service  
2. Reduce user impact  
3. Investigate later

---

### Incident Handling flow (real-world)  
1. Alert triggers  
2. On-call acknowledges  
3. Impact assessed  
4. Rollback decision made  
5. Rollback executed  
6. System stabilized  
7. Post-incident review later

Writing code during step 2–4 is a **mistake**.

---

### Why Versioning is critical  
During incidents, teams must answer:  
+ Which version is running?  
+ When was it deployed?  
+ What changed?  
+ What can we roll back to?

Deploying “latest” removes all clarity.

Correct answer example:  
>PROD is running `app-v-f1b2267`

---

### Post-Incident culture  
After stability is restored:  
+ Root cause analysis  
+ Process improvements  
+ Automation fixes  
+ Documentation updates

---

### Outcome of Day-20  
By the end of Day-20:  
+ understand why PROD is guarded  
+ know why rollback beats hot-fix  
+ can explain incident handling clearly  
+ think like a production engineer 

---

### Final summary (very important)
```
CI builds once
DEV validates fast
STAGING validates release
PROD serves users
Rollback restores stability
```

---
