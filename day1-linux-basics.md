## Day 1 — Linux Basics & Filesystem Navigation

### What is Linux?
Linux is a free, open-sourece operating system known fro its flexibility, stability, and storage security. It is widly used in personal computing, server environments, and enterprise systems because of its performance and customiztion capabilities.
Linux was created by Linux Torvalds in 1991 as a free and open-source operating system kernel.
It was inspired by UNIX and the MINIX operating system.
Most web servers, databases, containers, and cloud machines run on Linux.
In the DevOps and Cloud world, Linux is the default choice because it is stable, secure, open-source, and highly customizable.

---

### What is a Terminal?
The terminal is a text-based interface that allows us to interact directly with the operating system. Instead of clicking buttons, we type commands. This is faster, scriptable, and more powerful than graphical interfaces, especially on servers where GUIs are not available.

DevOps engineers live in the terminal because automation, debugging, and remote server access all depend on it.

#### The "Big Three"
1. Terminal (The Window): This is application you actually see and type into (e.g., GNOME Terminal, or Windows Terminal). It's just the "skin" or te environment.
2. Shell (The Brain): This is the program running inside the terminal that understands your commands. It translates your text into instructions the computer's core(the kernal) can understand.
3. Console (The Hardware): Historically, this was the physical screen and keyboard plugged into a massive mainframe computer.

---

### Basic Commands and What They Do

#### `pwd` Print Working Directory:
pwd command prints the full filename of the current working directory.<br>
Syntax:
	pwd [options]

#### `ls` Lists:
ls command lists the files and directories under currentworking directory.<br>
Syntax:
	ls [options] [directory_or_path]

#### `cd` Change Directory:
cd command is used to change the directory. Essential for navigation in Linux.<br>
Syntax:
	cd [path_or_dirctory]

#### `mkdir` Make Directory:
mkdir command used to creates a new directory.
Syntax:
	mkdir [options] directory_name1 directory_name2...

#### `touch`
touch command used to creates a new empty filein a specific directory. Commonly used to create config or log files quickly.
Syntax:
	touch [options] [path_and_filename]

#### `echo`
echo command used to print text in your command as a terminal output. Often used in scripts and quick file creation.
Syntax:
	echo [options] [text]

#### `cat` concatination:
cat command used to concatenates files and prints it on the standard output.
Syntax:
	cat [file_name]

#### `rm` Remove:
rm command is used to remove/delete the file from the directory. You must have the write permission for the folder or use 'sudo'.
Syntax:
	rm [options] file1 file2...

#### `cp` Copy:
cp command is used to copy files from one location to another. If the destination is an existing file, then the file is overwritten; If the destination is an existing directory, the file is copied into the directory (the directory is not overwritten).
Syntax:
	cp file1 file2 [target_path]

---
