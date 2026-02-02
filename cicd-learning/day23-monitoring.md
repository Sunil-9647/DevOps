## Day 23 — Monitoring & Alerting Mindset for DevOps

### Why this matters?
CI/CD helps us ship changes. But after shipping, systems can break. Monitoring and alerting exist so that we can **detect issues early, reduce downtime, and recover safely** (often by rollback).  
A DevOps engineer is judged not only by how fast they deploy, but also by how safely they operate production systems.

---

### `Monitoring` vs `Alerting`
**Monitoring**  
Monitoring means observing the system continuously using:  
+ metrics (latency, traffic, errors, saturation)  
+ logs (events and errors)  
+ trends (how the system behaves over time)

Monitoring is information. It helps us understand what the system is doing.

**Alerting**  
Alerting is a subset of monitoring that creates notifications when:  
+ users are impacted, or  
+ business-critical functionality is failing, or  
+ action is needed immediately

Alerting is **interruption + action**.

**Rule:** If no human action is required, it should not be an alert.

---

### `Signal` vs `Alert`
**Signal**  
A signal is any measurement or event that describes system state.  
Examples:  
+ CPU usage  
+ memory usage  
+ disk usage  
+ pod restarts  
+ queue length  
+ cache hit rate

Signals are helpful for debugging and planning, but they are not always emergencies.

**Alert**  
An alert is a signal strong enough that someone must take action now.  
Examples:  
+ checkout failures rising above threshold  
+ login failures affecting users  
+ API latency breaching SLA consistently  

**Rule:** All alerts are signals, but not all signals are alerts.

---

### The four-golden `Signals`
Most production incidents can be detected using these four:  
1. **Latency:** how slow requests are (p95/p99 important)  
2. **Traffic:** how many requests are coming in (spike/drop indicates issues)  
3. **Errors:** failed requests or incorrect results  
4. **Saturation:** resource exhaustion (CPU, memory, connections, disk)

These signals are strongly connected to user experience.

---

### What makes a good alert?
A good alert must be:  

1. **User-impact based**  
    + it should represent what users feel (failure or slowness)  
2. **Time bounded**  
    + avoid alerting on 10-second spikes  
    + alert on sustained issues (example: 5–10 minutes)  
3. **Actionable**  
    + the on-call engineer must know what to do:  
        - rollback  
        - disable a feature  
        - investigate dependency  
        - scale resources (later)  

**Example of a good alert**  
“More than 5% login failures for 10 minutes”  
+ user impact is real  
+ sustained issue  
+ action required

**Example of a bad alert**  
“CPU is 70%”  
+ may be normal  
+ not always user-impacting  
+ creates noise and alert fatigue

---

### Alert fatigue (big operational risk)
Alert fatigue happens when teams get paged too often for low-severity issues. Over time, engineers:  
+ stop trusting alerts  
+ mute notifications  
+ miss real incidents

Bad alerting is dangerous because it delays response during real outages.

---

### On-call mindset
When an alert fires:  
+ don’t panic  
+ identify user impact quickly  
+ identify current production version  
+ identify last known-good version  
+ decide rollback vs investigate

On-call work is about restoring service first, then doing deep debugging later.

---

### Relationship between monitoring and CI/CD
Monitoring does not deploy anything. CI/CD does not decide incidents.  
Correct operational loop:  
1. Monitoring detects issue  
2. Alert fires  
3. Human decides the response (rollback / disable feature / observe)  
4. CI/CD executes the chosen action safely  
5. After stability, do root cause analysis

---

### Key takeaway
CI/CD is about delivery, but monitoring and alerting are about survival:  
+ controlled risk  
+ fast recovery  
+ minimizing user impact

---

