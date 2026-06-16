# Planning & ideation

Turn ideas into validated designs through collaborative dialogue, then into
detailed implementation plans. Brainstorm first, write the plan second.

## Part 1: Brainstorming ideas into designs

Use before any creative work (new features, components, behavior changes).
Explore intent, requirements, and design before touching code.

### Understand the idea

- Check the current project state first (files, docs, recent commits).
- Ask questions one at a time; never overwhelm with several at once.
- Prefer multiple-choice questions, but open-ended is fine.
- If a topic needs more exploration, split it into multiple single questions.
- Focus on purpose, constraints, and success criteria.

### Explore approaches

- Propose 2-3 approaches with their trade-offs.
- Present them conversationally, leading with your recommendation and reasoning.

### Present the design

- Once you understand what you're building, present the design in sections of
  200-300 words.
- After each section, check whether it looks right so far.
- Cover architecture, components, data flow, error handling, and testing.
- Go back and clarify whenever something doesn't make sense.

### After the design

- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md` and
  commit it.
- To continue into implementation, set up an isolated worktree, then move to
  Part 2 to create the implementation plan.

### Key principles

- One question at a time.
- Multiple choice preferred.
- YAGNI ruthlessly: remove unnecessary features from every design.
- Always explore alternatives before settling.
- Validate incrementally, section by section.
- Stay flexible: revisit and clarify as needed.

## Part 2: Writing implementation plans

Use when you have a spec or requirements for a multi-step task, before touching
code. Run this in the dedicated worktree from Part 1.

Write the plan assuming the engineer has zero context for the codebase: a
skilled developer who knows almost nothing about the toolset, the problem
domain, or good test design. Document everything they need: which files to
touch, the actual code, how to test it, and relevant docs. Deliver the whole
plan as bite-sized tasks. DRY, YAGNI, TDD, frequent commits.

Save plans to `docs/plans/YYYY-MM-DD-<feature-name>.md`.

### Bite-sized task granularity

Each step is one action (2-5 minutes), for example:

- Write the failing test.
- Run it to confirm it fails.
- Implement the minimal code to pass.
- Run the tests and confirm they pass.
- Commit.

### Plan document header

Every plan starts with:

```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

### Task structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

### Remember

- Exact file paths always.
- Complete code in the plan, not "add validation".
- Exact commands with expected output.
- DRY, YAGNI, TDD, frequent commits.
