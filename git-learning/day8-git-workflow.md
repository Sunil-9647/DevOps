## Day 8 - Git Daily Workflow

### Git file status
Every file in Git exists in one of four states:
1. **Untracked**: Files present in the local file system (Working Tree) that have no record in the Git Index.

2. **Modified**: Tracked files where changes have been detected in the Working Tree, but those changes have not yet been moved to the Index.

3. **Staged** (The Index): A state where modified files are marked as part of the next snapshot. The changes are moved to the Git Index.

4. **Committed**: Data that has been securely stored in the local .git directory as a permanent snapshot (Object Database).

---

### Why small commits matter?
+ **Faster Debugging**: Using git bisect to find a bug is instant when a commit only changes 10 lines instead of 500.

+ **Easier Rollbacks**: If a feature breaks production, you can revert only that specific change without losing other unrelated work.

+ **Better Code Reviews**: Teammates can review smaller "chunks" of code more thoroughly, leading to fewer bugs passing through.

+ **Simple Merge Conflicts**: Small changes are less likely to overlap with others' work, making conflicts rare and easy to fix.

+ **Clear Documentation**: Your Git history becomes a readable "story" of the project rather than a list of vague "updates."

---

### Real-World usage
In daily DevOps work, engineers constantly add, modify, stage, and commit files. Git is used multiple times a day, often without thinking, because the workflow becomes natural.

---
