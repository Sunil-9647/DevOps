## Day 5 — Disk, Memory & Logs

### Basic Commands and What They Do

#### `df` Disk Free:
df command is used to display information about the file systems on your Linux system. It provides a snapshot of disk usage, showing the total space, used space, available space, and the percentage of use for each mounted file system.
Syntax:
	df [options] filename

#### `du` Disk Usage:
du command is used to analyze and report on disk usage within directories and files. Whether you’re trying to manage disk space efficiently, or simply gain insights into storage consumption.
Syntax:
	du [options] filename

#### `free`:
free command is used to displays the total amount of free space available along with the amount of memory used and swap memory in the system.
Syntax:
	free [options]

#### `journalctl`:
journalctl command is used to view and manage system logs maintained by the systemd-journald service. It provides a centralized and efficient way to access and analyze log data.
Syntax:
	journalctl [options] [matches]

---

### Difference between `df` and `du`

* `du` (disk usage): reports the space used by files and directories by walking the filesystem tree and summing file sizes (optionally including metadata and accounting for hard links and sparse files). It shows usage from the file level.
* `df` (disk free): reports filesystem-level free and used space from the filesystem superblock (metadata kept by the filesystem). It shows how much space the filesystem has available to all files.

---

### Why disk full breaks applications?
A full disk breaks apps because they run out of the necessary space to perform basic operations like saving files, writing temporary data, updating, or accessing virtual memory, leading to crashes, errors, and system slowdowns.

---

### Meaning of Free, Available, Swap

* **Free**: Memory that is currently not being used at all by the system or applications.

* **Avialible**: Memory that is immediately ready for new applications, combining truly free memory with memory used for cache and buffers that can be quickly reclaimed.

* **Swap**: A designated area on your hard disk or SSD that acts as an extension of RAM when physical RAM fills up.

---

### Why logs grow uncontrollably?
When an application enters an error loop—constantly crashing and restarting while writing dozens of lines of text per second—it rapidly fills that allocated space because the operating system lacks a "speed limit" on how fast logs can be generated.

Consequently, the disk fills up not because of a system failure, but because the default "safety cap" is set far too high for a system experiencing a high-frequency error.

---

