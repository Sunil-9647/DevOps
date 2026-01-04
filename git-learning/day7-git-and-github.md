## Day 7 — Git & GitHub Basics

### Purpose of commands:

#### `git init`:
The git init command creates a new, empty Git repository in the current or specified directory. Basically a **.git** directory with subdirectories for objects, refs/heads, refs/tags, and template files.
Syntax:
	`git init`

#### `git status`:
The git status command is used to display the current state of the working directory and the staging area. 
Syntax:
	`git status`

#### `git add`:
The git add command is used to move changes from your working directory to the staging area (or "index"), preparing them to be included in the next commit.
Syntax:
	`git add <filename>`

#### `git commit`:
The git commit command is used to save a snapshot of your staged changes to the local repository's history.
Syntax:
	`git commit -m "commit message"`

#### `git log`:
The git log command is used to view the history of committed changes in a Git repository.
Syntax:
	`git log [options]`

#### `git push`:
The git push command is used to upload local repository content (commits) to a remote repository.
Syntax:
	`git push <remote> <branch>`

---

### What is git?
Git is a free, open-source **Distributed Version Control System** (DVCS) used to track changes in your files.

### What is commit?
A commit is a "save point" or snapshot of your entire project at a specific moment in time. It is a fundamental building block of the project's history, allowing you to track changes, understand why they were made, and revert to previous states if necessary. 

---

### Difference between Working directiory and Revository
* The Working Directory is the physical folder on your computer where you can see, edit, and delete files.
- **Your project folder** (e.g., Documents/MyProject).

* The Repository is the hidden database where Git stores every version of every file you have ever committed.
- **The hidden folder** *.git* folder inside your project.

---

### Why Git is important in DevOps?
1. The Automation Trigger:
- A git push automatically starts the build and test process.
- Faster releases and fewer manual errors.

2. Infrastructure as Code (IaC):
- Server and network settings are written as code and stored in Git.
- You can "version control" your entire data center and track every change.

3. Faster Recovery (Rollbacks):
- If a new update breaks the site, you simply revert to a previous commit.
- Drastically reduces downtime during a crisis.

4. GitOps & The "Source of Truth":
- Tools monitor Git; if the live server changes, Git automatically corrects it.
- Prevents "configuration drift" where servers become inconsistent.

5. Team Collaboration:
- Using Pull Requests, both Dev and Ops teams can review code before it goes live.
- Better security and higher code quality.

---
