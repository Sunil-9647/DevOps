## Day 3 — Users, Groups & Permissions

### What is a Linux User?
A Linux user represents an identity that owns files and runs processes. Each user has permissions that define what actions they can perform.

### What is a Group?
A group is a collection of users. Groups make it easy to manage users with the same security and access privileges. A user can be part of different groups.

---

### Permission Structure

Permissions are divided into:
- User (owner)
- Group
- Others

Each permission can be:
- Read (r)
- Write (w)
- Execute (x)

---

### Meaning of `rwx`
- Read (r): view file contents
- Write (w): modify file
- Execute (x): run file as a program

---

### Why `777` Is Dangerous
777 in Linux is dangerous because it grants read, write, and execute (rwx) permissions to everyone (owner, group, and all other users), creating huge security holes that let any user or process modify, delete, or even upload malicious scripts (like web shells) leading to data leaks.

---

### Basic Commands and What They Do

#### `whoami`:
whoami command is used to print the user's name from which they are currently logged-in.
Syntax:
	whoami [options]

#### `who`:
who command is used to determine when the system booted last time, a list of logged-in users, and the system's current run level.
Syntax:
	who [options]

#### `w`:
w command is used to display user information like user is and activities on the system. It also gives the knowledge of the system's running time along with the load average.
Syntax:
	w [options]

#### `id`:
id command is used to display user and group names along with their numeric ID's (User ID - UID or Group ID -GID) of the current user or any specified user on the system. This command is particularly useful for system administrations and users who need to verify user identities and associated permissions.
Syntax:
	id [options] [user]

#### `groups`:
groups command is used to display the groups a user belongs to.
Syntax:
	groups [options] [username]

In Linux, permissions aren't just assigned to individual users; they are assigned to groups. Being part of a group (like sudo, docker, or video) gives you the specific "powers" or access rights associated with that group.

#### `chmod` Change Mode:
chmod command is used to manage file and directory permissions-essentially deciding who is allowed to read, write, or execute a file. Whenever you see an error like "Permission denied" or "Command not found" then `chmod` is used to solve the issue.
Syntax:
	chmod [options] [mode] filename

1. Understanding the Permission  Structure:
	* Every file has 3-types of permissions for 3-types of people.
		- Permissions: `r` (Read), `w` (Write), `x` (Execute)
		- Users: `u` (User/Owner), `g` (Group), `o` (Others/Everyone else)

2. The 2-ways to use `chmod`:

	A. Symbolic Mode (easy to remember)
		This uses letters and mathematical symbols to add or remove permissions.
			- `+` adds a permission.
			- `-` removes a permission.
			- `=` sets the permission exactly.

	B. Absolute (Numeric) Mode
		This uses a 3-digit number to set all permissions at once. Each digit represents a person (Owner, Group, Others), and the number is the sum of their permissions.
			- `4` = Read (`r`)
			- `2` = Write (`w`)
			- `1` = Execute (`x`)
			- `0` = No permission
  
#### `chown` Change Owner:
chown command changes what can be done with a file (read/write/execute), `chown` changes who the file belongs to, you almost always need to use `sudo` with this command.
Syntax:
	sudo chown [user]:[group] [file]

1. Changing the owner:
	To change the owner of a file to a user named "john".
		- sudo chown jhon report.txt

2. Changing the group:
	To change only the group (keeping the owner same), use colon before the group name. 
		- sudo chown :developers report.txt

3. Changing both at once:
	This is common way to use the command.
		- sudo chown jhon:developers report.txt

---
