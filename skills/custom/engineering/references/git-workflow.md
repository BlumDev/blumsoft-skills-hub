# Git workflow (worktrees & finishing a branch)

Isolate feature work in a git worktree during development, then land or clean it up
when the work is done and tests pass.

## Part 1: Using worktrees during development

Worktrees create isolated workspaces sharing the same repository, so you can work on
multiple branches simultaneously without switching. Use one when starting feature work
that needs isolation, or before executing an implementation plan.

**Core principle:** systematic directory selection + safety verification = reliable isolation.

### Directory selection

Follow this priority order:

1. **Existing directory.** Prefer `.worktrees/` (hidden); fall back to `worktrees/`.
   If both exist, `.worktrees/` wins.
   ```bash
   ls -d .worktrees 2>/dev/null
   ls -d worktrees 2>/dev/null
   ```
2. **CLAUDE.md preference.** If specified, use it without asking.
   ```bash
   grep -i "worktree.*director" CLAUDE.md 2>/dev/null
   ```
3. **Ask the user** only if neither exists: project-local `.worktrees/` (hidden) or a
   global location like `~/.config/superpowers/worktrees/<project-name>/`.

### Safety verification

For project-local directories (`.worktrees` / `worktrees`), verify the directory is
ignored before creating the worktree, to avoid committing worktree contents:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

If not ignored: add the line to `.gitignore`, commit it, then proceed. Global
directories need no verification (outside the project entirely).

### Creation steps

```bash
# Detect project name
project=$(basename "$(git rev-parse --show-toplevel)")

# Create worktree with new branch and enter it
git worktree add "<location>/<branch-name>" -b "<branch-name>"
cd "<location>/<branch-name>"
```

Then run setup auto-detected from project files, and verify a clean baseline:

```bash
[ -f package.json ]     && npm install          # Node
[ -f Cargo.toml ]       && cargo build          # Rust
[ -f requirements.txt ] && pip install -r requirements.txt   # Python
[ -f pyproject.toml ]   && poetry install
[ -f go.mod ]           && go mod download      # Go

# Verify clean baseline with the project-appropriate command
npm test / cargo test / pytest / go test ./...
```

If baseline tests fail, report and ask whether to proceed or investigate. If they pass,
report the worktree path, the passing test count, and that it's ready to implement.

### Red flags

- Never create a project-local worktree without verifying it's ignored.
- Never skip baseline test verification, or proceed past failing tests without asking.
- Never assume the directory location when ambiguous; follow priority: existing > CLAUDE.md > ask.
- Auto-detect setup from project files; don't hardcode setup commands.

## Part 2: Finishing a development branch

Once implementation is complete and tests pass, decide how to integrate the work.

**Core principle:** verify tests, present options, execute the choice, clean up.

### Step 1: Verify tests

Run the project's test suite. If tests fail, stop and report failures, do not present
options. Cannot merge or PR until tests pass.

### Step 2: Determine base branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or confirm with the user (e.g. "This branch split from main, correct?").

### Step 3: Present exactly these 4 options

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

Keep them concise; don't add explanation.

### Step 4: Execute the choice

**Option 1 — Merge locally:**
```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
<test command>            # verify tests on merged result
git branch -d <feature-branch>
```
Then clean up the worktree.

**Option 2 — Push and create PR:**
```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```
Keep the worktree.

**Option 3 — Keep as-is:** report "Keeping branch <name>. Worktree preserved at <path>."
Keep the worktree.

**Option 4 — Discard:** confirm first. List what will be permanently deleted (branch,
commits, worktree) and require the user to type `discard`. Only then:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```
Then clean up the worktree.

### Step 5: Clean up the worktree

For options 1 and 4 only, remove the worktree:

```bash
git worktree list | grep $(git branch --show-current)
git worktree remove <worktree-path>
```

Keep the worktree for options 2 and 3.

### Quick reference

| Option | Merge | Push | Keep worktree | Cleanup branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | yes | -   | -   | yes |
| 2. Create PR     | -   | yes | yes | -   |
| 3. Keep as-is    | -   | -   | yes | -   |
| 4. Discard       | -   | -   | -   | yes (force) |

### Red flags

- Never proceed with failing tests, or merge without verifying tests on the result.
- Never delete work without typed `discard` confirmation.
- Never force-push without an explicit request.
- Clean up the worktree only for options 1 and 4.
