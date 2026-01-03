## Day 4 — Processes & Services

### Basic Commands and What They Do

#### `ps` Process Status:
ps command is used to provide information about the currently running processes on your system, including their Process ID (PID), memory usage, and the command that started them.<br>
Syntax:
	ps [options]

1. **`ps aux` (The BSD style)**: This is the most common way to use ps. It shows every process running on the system from every user.
	- `a`: Show processes for all users.
	- `u`: Display the user/owner of each process.
	- `x`: Show processes that aren't attached to a terminal (background services).

2. **`ps -ef` (The Standard style)**: This provides similar information but in a slightly different format, often used to see the "Parent Process ID" (PPID), which tells you which program started another program.

#### `top`:
top command is used for real-time system monitor. While `ps` gives you a static snapshot of what is running,`top` provides a live, updating dashboard of your computer's health.
Syntax:
	top [options]

The`top` interface is split into two halves: the System Summary (top 5 lines) and the Process List (the columns below).

Most Ubuntu users prefer a tool called htop. It’s not installed by default, but it’s much more user-friendly: it has color-coded bars, supports mouse clicking, and lets you scroll up/down and left/right.

#### `kill`:
kill command is a very useful command in Linux that is used to terminate the process manually. It sends a signal which ultimately terminates or kills a particular process or group of processes. If the user does not specify a signal to send with the kill command, the process is terminated using the default TERM signal.
Syntax:
	kill [option] <pid>

#### `systemctl`:
systemctl command is the central tool for controlling the systemd init system and service manager. It is essentially the "remote control" for your operating system's background services (daemons).

Whether you are starting a web server, checking why your database failed, or telling your computer to reboot, systemctl is the command you will use.
Syntax:
       systemctl [option] comand [unit...]

**Note**: The `systemctl` command needs the superuser privileges, i.e., `sudo` to deal with the system services.

---

### Process vs Service

* A **Process(Task)** is simply a running instance of a program. When you run ls, nano, or firefox, the system creates a process.
* A **Service(called a Daemon)** is a specialized process that runs in the background, independent of any specific user session. These are usually "always-on" programs that provide functionality to the whole system.

---

### When to use `kill` vs `kill -9`?

When you issue a standard `kill` command, the Linux kernel sends a SIGTERM signal to the process. This is the industry-standard way to stop a service.
* When it receives SIGTERM, it executes a cleanup routine.
* It flushes data buffers to the disk, closes active database connections, finishes current network requests, and removes its PID file.
* Used for routine maintenance, service restarts, or scaling down application instances.

Whern in `kill -9` command, this signal does not talk to the application; it talks directly to the Linux Kernel. It is an "unmaskable" signal, meaning the application cannot block, handle, or ignore it.
* The application is terminated instantly. It is not given any CPU cycles to execute a final "cleanup" line of code.
* The Kernel simply reclaims the memory and resources occupied by the process and removes it from the Process Table.
* Used only when a process is in an unresponsive state, or consuming excessive resources and failing to respond to standard termination signals.

---

### What `systemctl status` Shows?

`systemctl status` is a health report for a service. It tells you:

* **Loaded**: Does the config file exist and is it correct?

* **Active**: Is it currently Running, Stopped, or Failed?

* **Since**: When did the current state start (uptime)?

* **Main PID**: The Process ID (useful for top or kill).

* **Resources**: How much Memory and CPU it is using right now.

* **Logs**: The last 10 lines of the application's output (usually shows the error if it crashed).

---
