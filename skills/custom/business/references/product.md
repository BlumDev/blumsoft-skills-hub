# Product strategy

A consolidated guide for product management (discovery to delivery) and business analysis (data to decisions).

## Part 1: Product management

### Feature prioritization

Gather requests from customer feedback, sales, technical debt, and strategic initiatives. Score them, then balance the portfolio against strategy.

**RICE framework**

```
Score = (Reach × Impact × Confidence) / Effort

Reach:      users affected per quarter
Impact:     Massive 3x | High 2x | Medium 1x | Low 0.5x | Minimal 0.25x
Confidence: High 100% | Medium 80% | Low 50%
Effort:     person-months
```

**Value vs Effort matrix**

```
            Low Effort        High Effort
High Value  QUICK WINS        BIG BETS
            [prioritize]      [strategic]
Low Value   FILL-INS          TIME SINKS
            [maybe]           [avoid]
```

**MoSCoW**: Must Have (critical for launch), Should Have (important, not critical), Could Have (nice to have), Won't Have (out of scope).

Practice: mix quick wins with strategic bets, account for dependencies, buffer ~20% for unexpected work, revisit quarterly, communicate decisions clearly.

### Customer discovery

1. **Interview**: semi-structured format, focus on problems not solutions, record with permission.
2. **Analyze**: extract pain points (with severity), feature requests (with priority), jobs-to-be-done, sentiment, themes, key quotes.
3. **Synthesize**: group similar pain points, find patterns across interviews, map to opportunity areas.
4. **Validate**: form solution hypotheses, test with prototypes, measure actual vs expected behavior.

**Interview guide**

```
Context (5 min):     role, current workflow, tools used
Problem (15 min):    pain points, frequency/impact, current workarounds
Solution (10 min):   reaction to concepts, value perception, willingness to pay
Wrap-up (5 min):     other thoughts, referrals, follow-up permission
```

**Hypothesis template**

```
We believe that [building this feature]
For [these users]
Will [achieve this outcome]
We'll know we're right when [metric]
```

**Opportunity solution tree**: Outcome → Opportunities → Solutions (branch each opportunity into competing solutions).

Tips: ask "why" repeatedly, focus on past behavior over future intentions, avoid leading questions, look for emotional reactions, validate with data.

### PRD development

Choose the format by feature size:

- **Standard PRD**: 11-section format for major features (6-8 weeks), includes technical specs.
- **One-Page PRD**: problem/solution/metrics for smaller features (2-4 weeks).
- **Agile Epic**: sprint-based, user story mapping, acceptance criteria focus.
- **Feature Brief**: lightweight, hypothesis-driven exploration (pre-PRD).

Structure: Problem → Solution → Success Metrics. Always state what's out of scope. Include clear acceptance criteria.

Collaborate with engineering (feasibility), design (experience), sales (market validation), support (operational impact).

Writing PRDs: start with the problem, define success metrics upfront, state out-of-scope explicitly, use visuals (wireframes, flows), keep technical detail in an appendix, version control changes.

### Metrics

**North Star**: identify the #1 value to users, make it measurable, ensure teams can influence it, confirm it leads business success.

**Funnel**: Acquisition → Activation → Retention → Revenue → Referral. Track conversion and drop-off at each step, time between steps, cohort variation.

**Feature success**: Adoption (% using), Frequency (uses per period), Depth (% of capability used), Retention (continued use), Satisfaction (NPS/CSAT).

### Stakeholder management

Identify RACI for decisions, send regular async updates, demo over documentation, address concerns early, learn from failures openly.

### Pitfalls to avoid

- **Solution-first thinking**: jumping to features before understanding the problem.
- **Analysis paralysis**: over-researching without shipping.
- **Feature factory**: shipping without measuring impact.
- **Ignoring technical debt**: no time for platform health.
- **Stakeholder surprise**: not communicating early and often.
- **Metric theater**: optimizing vanity metrics over real value.

## Part 2: Business analysis

Transform complex business data into actionable insights and strategic recommendations. Combine technical proficiency with business acumen to influence executive decision-making.

### Response approach

1. Define business objectives and success criteria.
2. Assess data availability and quality.
3. Design the analytical framework and methodology.
4. Execute analysis with statistical rigor.
5. Create visualizations that tell the data story.
6. Develop actionable recommendations with implementation guidance.
7. Present insights to the target audience.
8. Plan ongoing monitoring and continuous improvement.

### Core capabilities

**Analytics platforms**: dashboards in Tableau, Power BI, Looker, Qlik; cloud warehouses (Snowflake, BigQuery, Databricks); real-time/streaming visualization; self-service BI adoption; custom solutions in Python, R, SQL; automated report generation.

**AI-powered BI**: predictive analytics and forecasting, NLP for sentiment/text, anomaly detection and alerting, automated insight/narrative generation, recommendation engines.

**KPI frameworks**: North Star metrics, OKRs, balanced scorecard, metric hierarchy and dependency mapping, benchmarking against industry standards.

**Financial analysis**: revenue modeling and forecasting, CLV/CAC optimization, cohort and retention modeling, unit economics, scenario and sensitivity analysis, FP&A automation, ROI calculations.

**Customer and market**: segmentation and personas, churn prediction, market sizing (TAM/SAM/SOM), competitive intelligence, product-market-fit validation, customer journey and funnel optimization, voice-of-customer analysis.

**Statistical analysis**: hypothesis testing, A/B test design and analysis, survey/market research, experimental design and causal inference, time series forecasting, multivariate analysis.

**Data management**: governance frameworks, quality assessment, master data management, warehouse and dimensional modeling, ETL/ELT design, lineage and impact analysis, privacy/compliance (GDPR, CCPA).

**Process optimization**: process mining and workflow analysis, operational efficiency measurement, resource allocation and capacity planning, automation opportunity assessment.

### Data storytelling

Translate complex technical concepts for non-technical stakeholders. Use interactive dashboards with strong UX, executive presentation narratives, and accessible visualization (color theory, inclusive design). Balance detail with executive-level summarization.

### Behavioral traits

Focus on business impact and actionable recommendations. Validate assumptions through data-driven testing. Maintain objectivity. Question data quality and methodology rigorously. Consider ethical implications of data use. Collaborate across functional teams.
