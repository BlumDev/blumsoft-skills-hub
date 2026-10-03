# Prompt engineering

Transform raw, unstructured prompts into optimized prompts using established
frameworks (RTF, RISEN, Chain of Thought, RODES, Chain of Density, RACE, RISE,
STAR, SOAP, CLEAR, GROW). Analyze intent, gauge complexity, and select the
framework(s) that maximize output quality.

Work in "magic mode": silently behind the scenes, interacting only when
clarification is critically needed. Deliver polished, ready-to-use prompts
without technical explanations or framework jargon.

## When to use

- The prompt is vague or generic ("help me code Python").
- The user has a complex idea but struggles to articulate it.
- The prompt lacks structure, context, or specific requirements.
- The task needs step-by-step reasoning (debugging, analysis, design).
- The user wants a prompt for a specific task but doesn't know frameworks.
- The user wants to improve an existing prompt.
- The user asks "how do I ask AI to..." or "create a prompt for...".

## Workflow

### Step 1: Analyze intent

Understand what the user truly wants. Detect:

- **Type:** coding, writing, analysis, design, learning, planning, decision,
  creative.
- **Complexity:** simple (one-step), moderate (multi-step), complex (reasoning
  or design).
- **Clarity:** clear vs. ambiguous.
- **Domain:** technical, business, creative, academic, personal.

Identify implicit requirements: examples needed, output format, constraints
(time, resources, scope), exploratory vs. execution-focused.

Detection patterns:

- **Simple:** short (<50 chars), single verb, no context.
- **Complex:** long (>200 chars), multiple requirements, conditional logic.
- **Ambiguous:** generic verbs ("help", "improve"), missing object/context.
- **Structured:** mentions steps, phases, deliverables, stakeholders.

### Step 2: Clarify (conditional)

Ask only if critical information is ambiguous, and never more than 3 questions.

### Step 3: Select framework(s)

Map task characteristics to the optimal framework(s):

| Task type | Framework | Rationale |
|-----------|-----------|-----------|
| Role-based (act as expert, consultant) | **RTF** (Role-Task-Format) | Role + task + output format |
| Step-by-step reasoning (debugging, proof, logic) | **Chain of Thought** | Explicit reasoning steps |
| Structured projects (multi-phase, deliverables) | **RISEN** (Role, Instructions, Steps, End goal, Narrowing) | Structure for complex work |
| Complex design/analysis (systems, architecture) | **RODES** (Role, Objective, Details, Examples, Sense check) | Detail with validation |
| Summarization (compress, synthesize) | **Chain of Density** | Iterative refinement to essentials |
| Communication (reports, presentations, storytelling) | **RACE** (Role, Audience, Context, Expectation) | Audience-aware messaging |
| Investigation/analysis (research, diagnosis) | **RISE** (Research, Investigate, Synthesize, Evaluate) | Systematic analysis |
| Contextual problem-solving with background | **STAR** (Situation, Task, Action, Result) | Context-rich framing |
| Documentation (medical, technical, records) | **SOAP** (Subjective, Objective, Assessment, Plan) | Structured capture |
| Goal-setting (OKRs, objectives, targets) | **CLEAR** (Collaborative, Limited, Emotional, Appreciable, Refinable) | Goal clarity |
| Coaching/development (mentoring, growth) | **GROW** (Goal, Reality, Options, Will) | Developmental structure |

Blending:

- Combine 2-3 frameworks when the task spans multiple types.
- Complex technical project: RODES + Chain of Thought (structure + reasoning).
- Leadership decision: CLEAR + GROW (goal clarity + development).

Selection: primary framework matches the core task; secondary framework(s)
address added complexity. Avoid over-engineering: simple tasks get simple
frameworks. Selection happens silently, never explained to the user.

### Step 4: Generate and validate

Adapt the prompt to the original language (PT in, PT out; EN in, EN out; mixed
defaults to EN). Before finalizing, verify:

- Self-contained (no external context needed).
- Task is specific and measurable.
- Output format is clear.
- No ambiguous language.
- Detail level matches task complexity.

## Critical rules

**Never:**

- Assume information that wasn't provided; ask if critical details are missing.
- Explain which framework was selected or why (keep magic mode invisible).
- Generate generic, one-size-fits-all prompts; always customize.
- Use technical jargon in the final prompt unless the domain is technical.
- Ask more than 3 clarifying questions.
- Include meta-commentary in the output ("This prompt uses...").
- Present output without code-block formatting.
- Mix languages inconsistently.

**Always:**

- Analyze intent before generating.
- Ask clarifying questions only when critical info is ambiguous.
- Select framework(s) by task type and complexity.
- Blend frameworks when it improves quality.
- Adapt prompt length to input complexity.
- Include output format specification.
- Present the final prompt in a clean Markdown code block.
- Make prompts self-contained.
- Use examples in complex prompts to illustrate expected output.

## Examples

### Complex clear prompt: RODES + Chain of Thought (no clarification)

Input: `create prompt for: I need to build a product recommendation system
considering purchase history, user preferences, and market trends`

Process: clear intent, complex ML system design, technical domain. Skip
clarification. Select RODES (complex design) + Chain of Thought (reasoning).

Output:

```
Role: You are a senior machine learning engineer specializing in recommendation systems.

Objective: Design a product recommendation system that combines user purchase history, preferences, and market trends.

Details:
- Input data sources: user transaction logs, preference surveys, market trend APIs
- Algorithm considerations: collaborative filtering, content-based filtering, hybrid approaches
- Performance metrics: precision, recall, diversity, novelty
- Scalability: system must handle 100k+ users
- Real-time constraints: recommendations updated within 500ms

Approach step-by-step:
1. Analyze the three data sources and their relationships
2. Propose 2-3 algorithm approaches with trade-offs analysis
3. Design data pipeline architecture (ingestion, processing, serving)
4. Define evaluation metrics and A/B testing strategy
5. Outline implementation roadmap with phases

Examples:
- Show pseudocode for core recommendation logic
- Illustrate data flow diagram
- Provide sample API response structure

Sense Check: Validate that the proposed solution balances personalization with discovery, scales to production load, and incorporates real-time market trends effectively.

Output format: Technical design document with architecture diagrams, algorithm justification, and implementation roadmap.
```

### Code debugging: Chain of Thought

Input: `optimize prompt: my Python code isn't working, needs debugging`

Process: debugging task needs step-by-step reasoning. Skip clarification (code
provided later). Select Chain of Thought.

Output:

```
You are an expert Python debugger.

Task: Debug the Python code provided by the user by analyzing it step-by-step.

Debugging approach:
1. Read and understand the code's intended purpose
2. Identify the error or unexpected behavior
3. Trace variable states at each execution step
4. Locate the root cause of the issue
5. Propose fix with explanation
6. Suggest preventive measures to avoid similar bugs

For each step, show your reasoning:
- What you're checking
- What you found
- Why it matters

Output format:
- **Issue identified:** [Describe the bug]
- **Root cause:** [Why it's happening]
- **Fix:** [Corrected code with comments]
- **Prevention:** [Best practices to avoid this in the future]

Include a working example to verify the fix.
```
