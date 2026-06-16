# UI/UX

Design intelligence for building and reviewing UI: styles, palettes, typography, layout, hierarchy, and interaction. Default stack is `html-tailwind` unless the user specifies React, Next.js, Vue, Svelte, SwiftUI, React Native, or Flutter.

## Workflow

When asked to design, build, review, fix, or improve UI:

1. **Read the requirement.** Extract product type (SaaS, e-commerce, portfolio, dashboard, landing page), style keywords (minimal, playful, professional, elegant, dark mode), industry, and stack.
2. **Assemble a design system.** Pick a style, a font pairing, and a color palette that fit the product and industry. Style + typography + color together form the system.
3. **Structure the page.** For landing pages, choose a hero strategy and section order. For dashboards, pick chart types.
4. **Apply UX rules and the pre-delivery checklist** below before shipping.

## Color palettes by product type

Each palette defines Primary, Secondary, CTA, Background, Text, and Border. Choose by industry tone:

- **SaaS / fintech:** cool, trustworthy. Indigo/blue primary (`#4F46E5`, `#2563EB`), slate neutrals, a single high-contrast CTA (often amber or emerald). Crisp borders (`#E2E8F0`).
- **E-commerce:** energetic, conversion-focused. Warm CTA (orange/red), neutral product background so imagery dominates, strong price/discount contrast.
- **Healthcare:** calm, clean. Teal/blue-green primary, generous white space, soft borders, high text contrast for readability.
- **Beauty / wellness / spa:** soft, elegant. Muted rose, sand, mauve, deep plum accents; low-saturation backgrounds; thin borders.
- **Service / professional:** authoritative. Navy or charcoal primary, restrained accent, conservative neutrals.

Always set body text to a near-black (`#0F172A` slate-900) and muted text no lighter than `#475569` (slate-600). Keep one dominant CTA color per screen so the primary action stays obvious.

## UI styles

Pick one dominant style and apply it consistently. Common styles and their signatures:

- **Minimalism:** lots of white space, limited palette, strong type hierarchy, few effects. Default for professional/B2B.
- **Glassmorphism:** frosted translucent panels (`backdrop-blur`), subtle borders, layered depth. In light mode use `bg-white/80` or higher (never `bg-white/10`).
- **Neumorphism:** soft extruded surfaces with dual light/dark shadows. Low contrast; use sparingly and check accessibility.
- **Claymorphism:** chunky rounded shapes, soft inflated shadows, playful pastel palettes. Good for friendly consumer apps.
- **Brutalism:** raw, high-contrast, visible borders, monospace accents, bold blocks. For editorial/portfolio statements.
- **Bento grid:** modular card grid of varied sizes packed into a clean layout. Strong for feature overviews and dashboards.
- **Flat design:** no skeuomorphic depth, solid fills, clear icons. Reliable and fast.
- **Skeuomorphism:** real-world textures and depth. Niche; use only when the brand calls for it.
- **Dark mode:** dark neutral background, raised surfaces a step lighter, restrained saturated accents, never pure-black-on-pure-white.

For each style, keep effects (shadow, blur, gradient, radius) consistent across all components.

## Typography

Pair a display/heading font with a readable body font, both available on Google Fonts. Match the pairing to the style:

- **Elegant / luxury:** serif display (Playfair Display, Cormorant) + clean sans body (Inter, Work Sans).
- **Professional / modern:** geometric or neutral sans throughout (Inter, Manrope, IBM Plex Sans), differentiated by weight and size.
- **Playful:** rounded sans (Poppins, Quicksand, Baloo) with a friendly body.
- **Editorial:** strong serif headings (Fraunces, Libre Baskerville) + grotesque body.

Establish a clear type scale (e.g. 12/14/16/20/24/32/48) and use weight and size, not color alone, to signal hierarchy.

## Landing page structure

Build pages around a single conversion goal. Common section order:

1. **Hero** — headline, subhead, one primary CTA. Choose hero-centric (one big promise) or feature-forward depending on product complexity.
2. **Social proof** — logos, ratings, or testimonials placed early to build trust.
3. **Features / benefits** — bento grid or alternating rows; lead with benefits, not specs.
4. **Testimonials / case studies** — concrete outcomes.
5. **Pricing** — clear tiers, highlight the recommended plan.
6. **Final CTA** — repeat the primary action.

Keep one primary CTA style throughout; secondary actions visually subordinate.

## Charts (dashboards / analytics)

Match chart type to intent:

- **Trend over time:** line or area chart.
- **Comparison across categories:** bar/column chart.
- **Part-to-whole:** stacked bar or, sparingly, pie/donut (avoid for many slices).
- **Distribution:** histogram or box plot.
- **Relationship:** scatter plot.
- **Flow / drop-off:** funnel chart.
- **Timeline / schedule:** Gantt.

Use a charting library appropriate to the stack (e.g. Recharts/Chart.js for React, ECharts for heavy dashboards). Label axes, keep a restrained categorical palette, and ensure color is not the only differentiator.

## Common rules for professional UI

Frequently overlooked issues that make UI look unprofessional.

### Icons and visual elements

- Use SVG icon sets (Heroicons, Lucide, Simple Icons); never use emojis (🎨 🚀 ⚙️) as UI icons.
- Use a fixed viewBox (24x24) with consistent sizing (`w-6 h-6`); do not mix icon sizes randomly.
- Use correct official brand logos (verify SVG from Simple Icons); do not guess logo paths.

### Interaction and cursor

- Add `cursor-pointer` to every clickable/hoverable element.
- Provide visible hover feedback via color, shadow, or border changes.
- Use smooth `transition-colors duration-200`; avoid instant changes or anything over ~500ms.
- Prefer color/opacity transitions on hover; avoid scale transforms that shift layout.
- Show visible focus states for keyboard navigation.

### Light / dark mode contrast

- Glass cards in light mode: `bg-white/80` or higher, never `bg-white/10`.
- Body text in light mode: `#0F172A` (slate-900); muted text no lighter than `#475569` (slate-600).
- Borders: use `border-gray-200` in light mode; `border-white/10` is invisible on light backgrounds.
- Test both modes before delivery.

### Layout and spacing

- Floating navbars need edge spacing (`top-4 left-4 right-4`), not flush `top-0 left-0 right-0`.
- Account for fixed navbar height so content is not hidden behind it.
- Use one consistent container width (`max-w-6xl` or `max-w-7xl`); do not mix.

## Pre-delivery checklist

**Visual quality**
- No emojis as icons; all icons from one consistent set.
- Brand logos verified correct.
- Hover states cause no layout shift.
- Use theme colors directly (`bg-primary`), not `var()` wrappers.

**Interaction**
- All clickable elements have `cursor-pointer`.
- Hover states give clear feedback; transitions 150-300ms.
- Focus states visible for keyboard navigation.

**Light / dark mode**
- Light-mode text meets 4.5:1 contrast minimum.
- Glass/transparent elements visible in light mode; borders visible in both modes.

**Layout**
- Floating elements spaced from edges; no content hidden behind fixed navbars.
- Responsive at 320px, 768px, 1024px, 1440px; no horizontal scroll on mobile.

**Accessibility**
- All images have alt text; all form inputs have labels.
- Color is never the only indicator; `prefers-reduced-motion` respected.
