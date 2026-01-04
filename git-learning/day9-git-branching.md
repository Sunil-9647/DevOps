## Day 9 - Git Collaboration & Branching

### Purpose of commands:

#### `git branch`:
The git branch is like a separate workspace where you can make changes and try new ideas without affecting the main project.
Syntax:
	`git branch [<new-branch-name>]`

#### `git switch`:


#### `git merge`:
The git merge command is used to combine the changes from two branches into one. It integrates work from different branches into a single unified history without losing progress.
Syntax:
	 `git merge [<branch>]`


#### `git pull`:
The git pull command is used to fetch and download new content from a remote Git repository and immediately integrate those changes into your current local branch.
Syntax:
	`git pull [<options>] [<repository>]`

---

### What is a branch?
A branch is an independent line of development. Changes made in a branch do not affect the main branch until they are merged. This protects production-ready code from unfinished or broken changes.

---

### Why branches exist?
Branches allow multiple people to work on the same project without interfering with each other. The main branch represents stable code, while feature branches are used for development and experimentation.

---

### What happens during a merge?
A merge combines changes from one branch into another. If Git can apply changes automatically, it performs a fast-forward or clean merge. If there are conflicting changes, Git pauses and asks for manual resolution.

---

### What is a merge conflict?
A merge conflict occurs when the same file is modified differently in two branches. Git cannot decide which change is correct, so it asks the engineer to resolve it. Conflicts are normal in team environments.

---
