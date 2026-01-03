## Day 6 — Linux Networking Basics

### Purpose of each commands:

#### `ip` Internet Protocol:
ip command is a powerful utility for network configuration and management. It allows users to interact with various networking components such as network interfaces, routing tables, addresses, and more.<br>
Syntax:
	ip [options] object {command | help}

#### `ss` Socket Statistics:
ss command is used for inspecting and displaying detailed information about network sockets on a Linux system.<br>
Syntax:
	ss [options]

#### `ping` Packet Internet Groper:
ping command is used to check the network connectivity between the host and server/host. This command takes as input the IP address or the URL and sends a data packet to the specified address with the message "PING" and gets a response from the server/host this time is recorded which is called latency. Fast ping with low latency means a faster connection.<br>
Syntax:
	ping [options] host_or_IP_address
	
#### `ssh` Secure Shell:
ssh is a secure communication protocol that allows a user to access and control a remote computer over a network.<br>
Syntax:
	ssh [options] [user@]hostname

#### `curl` 
curl is used to transfer data between a system and a server using different network protocols. It is widely used for fetching web content, testing APIs, and sending or receiving data over the network.<br>
Syntax:
	curl [options] [URL]

---

### Difference between `ping` and `curl`
`ping` is a basic connectivity test utility, while `curl` is a versatile tool for data transfer using various application-level protocols.

* Use `ping` when you need to quickly determine if a server or IP address is online and responsive at the network level. It is the first step in troubleshooting basic connectivity issues.
* Use `curl` when you need to interact with a web service, download a file, test an API endpoint,  or see how a server responds to application-specific requests.

---

### Debugging app not reachable
Check IP → Network → Port → Application.

1. **Check IP** (Reachability):
Confirm the server is powered on and connected by using Ping; if there is no response, the host is either offline or basic routing has failed.

2. **Check Network** (Firewall):
Ensure the "path" is clear by checking for firewalls or ACLs that might be dropping your traffic; use Traceroute to find exactly where the connection is being blocked.

3. **Check Port** (The Door):
Verify the specific port is open and accepting requests using Netcat (nc) or Telnet; a "Connection Refused" here means the server exists, but nothing is listening at that specific port number.

4. **Check Application** (The Service):
Confirm the software is actually running and bound to the correct network interface; use ss -tulpn to see if the app is listening on 0.0.0.0 (everyone) rather than just 127.0.0.1 (itself).

---

### Common networking failures
Wrong port, Firewall blocks, DNS issues, Service not listening.

* **Wrong port**: A "wrong port" error is a common networking failure that refers to human error where a cable is physically plugged into an incorrect socket, or a software/configuration setting is pointing to an incorrect port number.

* **Firewall blocks**: "Firewall blocks" are a common category of networking failures, usually stemming from misconfiguration of firewall rules. These issues often lead to connection timeouts, service unavailability, and application errors due to legitimate traffic being inadvertently blocked.

* **DNS issue**: DNS issues, a common networking failure, prevent website access by disrupting the translation of domain names (like google.com) to IP addresses, often caused by incorrect device settings, ISP/server outages, router misconfigurations, firewall blocks, or malware, leading to slow loads, timeouts, or complete inaccessibility.

* **Service not listening**: The "Service not listening" error is a common networking failure that indicates a connection attempt reached the target host, but no application was ready or configured to accept the connection on the specified port. The server is online, but the specific service is unreachable.

---
 
