# Pricing & launch

Guide to designing pricing that captures value, then launching to build momentum and convert interest into users. Pricing strategy first, then go-to-market.

---

## Part 1: Pricing

Design pricing, packaging, and monetization that captures value, supports growth, and aligns with customer willingness to pay, without harming conversion, trust, or retention. This covers strategy (research, value metrics, tier design, pricing changes), not implementation of pricing pages or experiments.

### Context to gather

- **Business model:** product type (SaaS, marketplace, service, usage-based), current pricing, target customer (SMB / mid-market / enterprise), GTM motion (self-serve, sales-led, hybrid).
- **Market:** primary value delivered, key alternatives, competitor pricing models, differentiation.
- **Current performance (if existing):** conversion, ARPU/ARR, churn and expansion, qualitative feedback.
- **Objectives:** growth vs. revenue vs. profitability; move up- or downmarket; planned changes.

### The three pricing decisions

Every strategy must answer all three; failure in any one weakens the system:

1. **Packaging** - what is included in each tier?
2. **Value metric** - what customers pay for (users, usage, outcomes)?
3. **Price level** - how much each tier costs.

### Value-based pricing

Anchor to customer-perceived value, not internal cost:

```
Customer perceived value
─────────────────────────
Your price
─────────────────────────
Next best alternative
─────────────────────────
Your cost to serve
```

- Price above the next best alternative.
- Leave customer surplus (value they keep).
- Cost is a floor, not a pricing basis.

### Research methods

- **Van Westendorp (price sensitivity):** four questions (too expensive, too cheap, expensive but acceptable, cheap/good value) yield PMC, PME, OPP, IDP. Use for early pricing, increase validation, segment comparison.
- **Feature value (MaxDiff / Conjoint):** informs packaging, not price levels. Surfaces table-stakes features, differentiators, premium-only features, and low-value candidates to remove.
- **Willingness-to-pay:** Direct WTP (directional only), Gabor-Granger (demand curve), Conjoint (feature + price sensitivity).

### Value metrics

The value metric is what scales price with customer value. Good ones align with value delivered, scale with customer success, are easy to understand, and hard to game.

| Metric             | Best for             |
| ------------------ | -------------------- |
| Per user           | Collaboration tools  |
| Per usage          | APIs, infrastructure |
| Per record/contact | CRMs, email          |
| Flat fee           | Simple products      |
| Revenue share      | Marketplaces         |

Validation test: as customers get more value, do they naturally pay more? If not, the metric is misaligned.

### Tier design

Default to 3 tiers (Good / Better / Best); 2 for simple segmentation, 4+ only for broad markets with careful UX.

- **Good:** entry point, limited usage, removes friction.
- **Better (anchor):** where most customers should land; full core value; best value-per-dollar.
- **Best:** power users / enterprise; advanced controls, scale, support.

Differentiation levers: usage limits, advanced features, support level, security & compliance, customization / integrations.

### Persona-based packaging

1. Define personas (company size, use case, sophistication, budget norms).
2. Map value to tiers so each persona maps cleanly to one tier.
3. Price to segment WTP; avoid one price across fundamentally different buyers.

### Freemium vs. free trial

- **Freemium** works with a large market, viral/network effects, a clear upgrade trigger, and low marginal cost.
- **Free trial** works when value requires setup, price points are higher, B2B evaluation cycles apply, and post-activation usage is sticky.
- **Hybrid:** reverse trials, feature-limited free + premium trial.

### Price increases

Signals: very high conversion, low churn, customers under-paying relative to value, market movement.

Strategies: new customers only; delayed increase for existing; value-tied increase; full plan restructure.

### Price testing

- **Preferred:** new-customer pricing, sales-led experimentation, geographic tests, packaging tests.
- **Avoid:** blind A/B price tests on the same page; surprise customer discovery.

### Enterprise pricing

Introduce when deals exceed ~$10k ARR, custom contracts or security/compliance needs appear, or sales involvement is required. Common structures: volume-discounted per seat, platform fee + usage, outcome-based.

### Output & validation

Produce a **pricing strategy document** (target personas, value metric, tier structure, price rationale, research inputs, risks/tradeoffs) and, if changing pricing, a **change recommendation** (who is affected, expected impact, rollout plan, measurement plan).

Validation checklist: clear value metric; distinct tier personas; research-backed price range; conversion-safe entry tier; expansion path exists; enterprise handled explicitly.

---

## Part 2: Launch & go-to-market

Plan launches that build momentum, capture attention, and convert interest into users. The best companies don't launch once; they launch again and again. A strong launch is not a single moment: get the product into users' hands early, learn from real feedback, make a splash at every stage, and build compounding momentum.

### The ORB framework

Structure launch marketing across three channel types; everything should lead back to owned channels.

**Owned** - you control the channel (email list, blog, podcast, branded community, website). Compounds over time, no algorithm or pay-to-play, direct relationship. Start with 1-2 based on audience: thin industry content → blog; want direct updates → email; engagement matters → community.

**Rented** - visibility you don't control (social, app stores, YouTube, Reddit). Algorithms and rules shift. Pick 1-2 platforms where your audience is active and use them to drive traffic to owned channels. Tactics: X threads → newsletter; LinkedIn posts → gated content/email; marketplace listings → site. Rented channels give speed, not stability.

**Borrowed** - tap someone else's audience to shortcut getting noticed (guest content, collaborations, speaking, influencer partnerships). Be proactive: list industry leaders your audience follows, pitch win-win collaborations, find audience overlap (SparkToro, Listen Notes), set up affiliate/referral incentives. Gives instant credibility, but only works if you convert borrowed attention into owned relationships.

*Examples:* Superhuman built demand via an invite-only waitlist and 1:1 onboarding (owned). Notion drove Twitter/YouTube/Reddit virality but funneled it into signups + email (rented → owned). TRMNL sent a free e-ink display to YouTuber Snazzy Labs, whose unpaid review drove 500K+ views and $500K+ in sales (borrowed).

### Five-phase launch

1. **Internal** - recruit early users 1:1 to test free; collect feedback; prototype just needs to demo. Goal: validate core functionality with friendly users.
2. **Alpha** - landing page with early-access signup; announce it exists; invite individually; MVP working in production. Goal: first external validation, initial waitlist.
3. **Beta** - work the early-access list (some free, some paid); start teaser marketing; recruit friends, investors, influencers to test and share. Add a coming-soon/waitlist page, "Beta" dashboard sticker, email invites, experimental-feature toggle. Goal: build buzz, refine with broader feedback.
4. **Early access** - leak details (screenshots, GIFs, demos); gather quantitative + qualitative data; run user research (incentivize with credits); optionally a PMF survey. Expand by throttling invites in batches (5-10%) or inviting all under an "early access" frame. Goal: validate at scale.
5. **Full launch** - open self-serve signups; start charging; announce GA everywhere. Touchpoints: customer emails, in-app popups/tours, website banner, "New" dashboard sticker, blog post, social, Product Hunt / BetaList / Hacker News. Goal: maximum visibility and conversion.

### Product Hunt

Powerful for reaching early adopters but not magic; requires preparation. Pros: tech-savvy audience, credibility bump (especially Product of the Day), potential PR and backlinks. Cons: very competitive, short-lived spikes, heavy pre-launch planning.

- **Before:** build relationships with supporters/communities; optimize the listing (tagline, visuals, short demo video); study successful launches; provide value in communities before pitching; prep the team for all-day engagement.
- **Launch day:** treat as an all-day event; respond to every comment in real time; spark discussion; rally your audience; direct traffic to your site to capture signups.
- **After:** follow up with everyone who engaged; convert traffic into email signups; sustain with post-launch content.

*Examples:* SavvyCal optimized onboarding and built influencer relationships in advance → #2 Product of the Month. Reform studied past launches, polished its tagline/visuals/demo, engaged communities first → #1 Product of the Day.

### Post-launch product marketing

The work continues after the announcement: educate new users with an automated onboarding email sequence; reinforce the launch in your roundup email for those who missed it; publish comparison pages against competitors; add dedicated feature sections across the site; offer a no-code interactive demo (e.g., Navattic) so visitors can explore before signing up. It is easier to build on momentum than to restart.

### Ongoing launches

Don't rely on a single event. Size the effort to the update:

- **Major** (new features, overhauls): full multi-channel campaign (blog, email, in-app, social).
- **Medium** (integrations, UI enhancements): targeted announcement (segment email, in-app banner).
- **Minor** (fixes, tweaks): changelog and release notes signaling steady improvement.

Space out releases to maintain momentum, reuse high-performing tactics, keep engaging via email/social/in-app, and signal active development; even small changelog updates build retention and word-of-mouth.

### Launch checklist

**Pre-launch:** landing page with clear value prop; email capture/waitlist; early-access list built; owned channels established; rented presence optimized; borrowed opportunities identified; Product Hunt listing prepared (if using); launch assets created (screenshots, demo video, GIFs); onboarding flow ready; analytics in place.

**Launch day:** announcement email; blog post published; social posts scheduled/posted; Product Hunt live (if using); in-app announcement; website banner active; team ready to engage; monitor for issues.

**Post-launch:** onboarding sequence active; follow up with engaged prospects; roundup email includes announcement; comparison pages published; interactive demo created; gather and act on feedback; plan the next launch moment.

### Questions to ask

What are you launching (new product, major feature, minor update)? Current audience size and engagement? Which owned channels do you have? Timeline? Have you launched before (what worked)? Considering Product Hunt, and what's your prep status?
