# Growth measurement

A coherent guide for measuring growth across three disciplines: analytics/tracking (trustworthy signals), A/B testing (rigorous experiments), and competitive analysis (market positioning). The thread running through all three: measure for decisions, not curiosity, and validate before you act.

---

## 1. Analytics & tracking

Goal: tracking that produces trustworthy signals which directly support decisions. Do not track everything. Do not optimize dashboards on broken instrumentation. Do not treat GA4 numbers as truth until validated.

### Readiness gate (do this first)

Before adding or changing tracking, score the setup 0-100. This is a diagnostic, not a KPI.

| Category | Weight | Checks |
| --- | --- | --- |
| Decision alignment | 25 | Business questions defined; every event maps to a decision; nothing tracked "just in case" |
| Event model clarity | 20 | Events are meaningful actions; naming consistent; properties carry context not noise |
| Data accuracy & integrity | 20 | Fires reliably; no duplication/inflation; values correct; cross-browser and mobile validated |
| Conversion quality | 15 | Conversions represent real success; counting is intentional; funnel stages distinguishable |
| Attribution & context | 10 | UTMs consistent and complete; source context preserved; cross-domain/device handled |
| Governance | 10 | Documented; ownership clear; changes versioned and monitored |

Verdict bands: 85-100 measurement-ready (safe to optimize/experiment); 70-84 usable with gaps (fix before major decisions); 55-69 unreliable (do not trust yet); <55 broken (stop, remediate first, do not act on this data).

### Core principles

- Track for decisions, not curiosity. If no decision depends on it, do not track it.
- Start with the question, work backwards: what you need to know, what action you will take, what signal proves it. Then design events.
- Events represent meaningful state changes (intent, completion, commitment), not cosmetic clicks or UI noise.
- Data quality beats volume. Fewer accurate events outperform many unreliable ones.

### Event model

Naming pattern: `object_action[_context]`, lowercase, underscores, no spaces, no ambiguity (e.g. `signup_completed`, `pricing_viewed`, `cta_hero_clicked`).

Taxonomy:
- Exposure: `page_view`, `content_viewed`, `pricing_viewed`
- Intent: `cta_clicked`, `form_started`, `demo_requested`
- Completion: `signup_completed`, `purchase_completed`, `subscription_changed`
- System/state: `onboarding_completed`, `feature_activated`, `error_occurred`

Properties carry context: where (page, section), who (user_type, plan), how (method, variant). Avoid PII, free-text fields, and duplicated auto-properties.

### Conversions

A conversion represents real value, completed intent, and irreversible progress (e.g. `signup_completed`, `purchase_completed`, `demo_booked`). Page views, button clicks, and form starts are not conversions. Document counting rules (once per session vs every occurrence) and keep them consistent across tools.

### Implementation, attribution, validation

- GA4/GTM: prefer GA4 recommended events; use GTM for orchestration not logic; push clean dataLayer events; avoid multiple containers; version every publish.
- UTMs: lowercase only, consistent separators, documented centrally, never overwritten client-side. UTMs explain performance, they do not inflate it.
- Validate: real-time verification, duplicate detection, cross-browser, mobile, and consent-state testing. Common failure modes: double firing, missing properties, broken attribution, PII leakage, inflated conversions.
- Privacy: consent before tracking where required, data minimization, deletion support, reviewed retention.

Output: a tracking plan table (Event | Description | Properties | Trigger | Decision supported), a conversions table (Conversion | Event | Counting | Used by), plus the readiness score, key risks, and remediation order.

---

## 2. A/B testing

Goal: make every test valid, rigorous, and safe before a line of code is written. Prevents peeking, enforces statistical power, blocks invalid hypotheses.

### Prerequisites

A clear user problem, access to an analytics source (clean conversions from section 1), and a rough traffic estimate. A valid hypothesis has: an observation/evidence, a single specific change, a directional expectation, a defined audience, and measurable success criteria.

### Hard gates (in order)

1. **Hypothesis lock.** Present the final hypothesis with target audience, primary metric, expected direction, and Minimum Detectable Effect (MDE). Ask explicitly: "Is this the final hypothesis we commit to?" Do not proceed until confirmed.
2. **Assumptions check.** List assumptions about traffic stability, user independence, metric reliability, randomization quality, and external factors (seasonality, campaigns, releases). If weak or violated, warn and recommend delaying or redesigning.
3. **Execution readiness (hard stop).** Proceed only if all are true: hypothesis locked, primary metric frozen, sample size calculated, duration defined, guardrails set, tracking verified. If any is missing, stop and resolve it.

### Test type

Choose the simplest valid test; default to A/B unless there is a clear reason otherwise.
- A/B: single change, two variants
- A/B/n: multiple variants, higher traffic
- Multivariate (MVT): interaction effects, very high traffic
- Split URL: major structural changes

### Metrics

- Primary (mandatory): one metric, tied to the hypothesis, frozen before launch.
- Secondary: context, explains why results occurred; never overrides the primary.
- Guardrail: must not degrade; trigger a stop if significantly negative.

### Sample size & duration

Define upfront: baseline rate, MDE, significance (typically 95%), power (typically 80%). Estimate required sample size per variant and expected duration. Do not proceed without a realistic sample size estimate.

### Running, analysis, decisions

During the test: monitor technical health, document external factors. Do not stop early on good-looking results, change variants mid-test, add traffic sources, or redefine success.

When analyzing: do not generalize beyond the tested population, do not claim causality beyond the tested change, do not override guardrail failures, and separate statistical significance from business judgment.

| Result | Action |
| --- | --- |
| Significant positive | Consider rollout |
| Significant negative | Reject variant, document learning |
| Inconclusive | More traffic or a bolder change |
| Guardrail failure | Do not ship, even if primary wins |

### Documentation & refusal

Record (in a shared, searchable place): hypothesis, variants, metrics, sample size vs achieved, results, decision, learnings, follow-ups.

Refuse to proceed if: baseline rate is unknown and cannot be estimated, traffic cannot detect the MDE, the primary metric is undefined, multiple variables change without proper design, or the hypothesis cannot be stated clearly. Explain why and recommend next steps.

Non-negotiables: one hypothesis per test, one primary metric, commit before launch, no peeking, learning over winning, statistical rigor first. A/B testing is about learning the truth with confidence, not proving ideas right.

---

## 3. Competitive analysis

Goal: understand competitive dynamics, identify differentiation, and craft defensible positioning. Start broad (industry), then narrow (rivals), then act (positioning and strategy).

### Porter's Five Forces

Assess industry attractiveness by scoring each force 1-5.

| Force | High when | Key factors |
| --- | --- | --- |
| New entrants | Low barriers, easy entry | Capital, scale, switching costs, brand, regulation, distribution, network effects |
| Supplier power | Few suppliers, critical inputs | Concentration, substitutes, switching costs, forward-integration threat |
| Buyer power | Few large customers, standardized product | Concentration, volume, differentiation, price sensitivity, backward-integration threat |
| Substitutes | Many alternatives, low switching cost | Alternative solutions, price-performance, switching cost |
| Rivalry | Many competitors, slow growth, commoditized | Competitor count, growth rate, differentiation, exit barriers |

Summarize as a scorecard (Force | Intensity 1-5 | Impact | Key factors) and state an overall attractiveness verdict.

### Blue Ocean: four actions

Find uncontested space via value innovation (lower cost + higher value at once):
- Eliminate: factors the industry takes for granted
- Reduce: factors well below industry standard
- Raise: factors well above standard
- Create: factors the industry never offered

Map your offering vs competitors on a strategy canvas across the key competing factors; validate that the combination opens new market space.

### Positioning

Plot competitors on the 2 dimensions that matter most to customers (e.g. price vs features, simple vs complex, SMB vs enterprise, self-serve vs high-touch). Identify white space, then validate it reflects a real customer need.

Differentiate on product (features, performance, UX, integrations), service (support, onboarding, response time), brand (trust, thought leadership, community), or price (premium, value, transparent, flexible).

Positioning statement:
```
For [target customer]
Who [need or opportunity]
Our product is [category]
That [key benefit]
Unlike [primary alternative]
Our product [primary differentiation]
```

### Competitive intelligence

Sources: public (websites, blogs, press, job postings, G2/Capterra reviews, Glassdoor, SEC and patent filings) and direct (customer interviews, win/loss analysis, sales feedback, demos/trials).

Profile each key competitor: company overview (founding, funding, size, stage), product (features, target, pricing, stack, launches), go-to-market (sales model, marketing, channels, partnerships), strengths, weaknesses, and inferred strategy/next moves.

### Pricing

Tiers: premium (top 25%, superior product, strong brand, enterprise), mid-market (middle 50%, balanced value, broad), value (bottom 25%, basic, self-serve, high volume). Build a comparison matrix (Competitor | Entry | Mid | Enterprise | Model) and ask: are we competitive, what does our price signal, are there packaging gaps?

### Strategy & sustainable advantage

Market entry: direct competition, niche focus (specialist vs generalist), disruptive innovation (low end then upmarket), or platform play (network effects). Pick a beachhead: a specific reachable segment with acute pain, limited competition, and willingness to pay that can expand later.

Sustainable advantages: network effects, switching costs, economies of scale, brand, proprietary technology, regulatory licenses. Test each: can competitors copy it in under 2 years, does it matter to customers, do we execute it better than anyone, is it durable? If any answer is no, it is not sustainable.

### Monitoring cadence

- Weekly: product release notes, news mentions
- Monthly: win/loss review, positioning-map updates
- Quarterly: deep competitive review, strategy adjustment
- Annually: major strategy and market-trend reassessment

---

## How the three connect

Clean tracking (section 1) is the prerequisite for trustworthy A/B tests (section 2): a test is only as valid as its conversion definitions. Competitive analysis (section 3) sets the strategic direction; analytics and experiments tell you whether your moves are working. Run the loop: define the decision, validate the signal, test the change, read the market, repeat.
