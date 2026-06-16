# Frontend development (React / Next.js)

## General web development

Build pages in this order:

1. **Content and message hierarchy** - decide what matters before markup.
2. **Semantic HTML** - structure with meaningful elements, not `div` soup.
3. **Mobile-first styling** - start small, layer up with breakpoints.
4. **Accessibility and responsiveness** - check both before shipping.
5. **Refactor** - tidy for clarity and maintainability.

Optimize for performance, accessibility, semantics, and conversion.

## React patterns

Performance guidelines ordered by impact. Apply when writing, reviewing, or refactoring components.

### Eliminate waterfalls (critical)

- Move `await` into the branch that actually uses the value.
- `Promise.all()` for independent operations; partial-dependency helpers for mixed cases.
- In API routes, start promises early and await late.
- Use Suspense boundaries to stream content.

### Bundle size (critical)

- Import directly; avoid barrel files.
- `next/dynamic` for heavy components.
- Defer third-party scripts (analytics, logging) until after hydration.
- Load modules conditionally, only when the feature activates.
- Preload on hover/focus for perceived speed.

### Re-render optimization

- Don't subscribe to state only used inside callbacks.
- Memoize expensive work into separate components.
- Use primitive dependencies in effects.
- Subscribe to derived booleans, not raw values.
- Functional `setState` for stable callbacks; pass a function to `useState` for expensive initial values.
- `startTransition` for non-urgent updates.

### Rendering performance

- Animate a wrapping `div`, not the SVG element; reduce SVG coordinate precision.
- `content-visibility` for long lists.
- Hoist static JSX outside components.
- Ternary over `&&` for conditional rendering.

### JavaScript performance

- Build a `Map`/`Set` for repeated lookups (O(1)); cache property and storage reads in loops.
- Combine multiple filter/map passes into one loop.
- Return early; hoist `RegExp` creation outside loops.
- `toSorted()` for immutable sorts; loop for min/max instead of sorting.

## Next.js (App Router)

### Server vs Client Components

Server Components are the default. Use them for data fetching, layout, and static content. Switch to a Client Component (`'use client'`) only when you need `useState`, `useEffect`, or event handlers (forms, buttons, interactive UI). When you need both, split: Server parent, Client child.

### Data fetching

| Need | Pattern |
|------|---------|
| Static (cached at build) | default `fetch` |
| Time-based refresh (ISR) | `revalidate: N` |
| Dynamic (every request) | `no-store` |
| Database | Server Component fetch |
| User input | Client state + server action |

- Use `React.cache()` for per-request deduplication, an LRU cache for cross-request.
- Minimize data passed to Client Components (serialization cost).
- Restructure components to parallelize fetches; use `after()` for non-blocking work.
- Client-side: SWR for automatic request deduplication; deduplicate global event listeners.

### Routing

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout |
| `loading.tsx` | Loading state |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 |

Organize routes with groups `(name)` (no URL impact), parallel routes `@slot`, and intercepting routes `(.)` for modal overlays.

### API routes (Route Handlers)

GET reads, POST creates, PUT/PATCH updates, DELETE removes. Validate input with Zod, return proper status codes, handle errors gracefully, and prefer the Edge runtime where possible.

### Server Actions

For form submissions, data mutations, and revalidation triggers. Mark with `'use server'`, validate all inputs, return typed responses, handle errors.

### Performance

- **Images:** `next/image`, `priority` for above-fold, blur placeholder, responsive sizes.
- **Bundles:** dynamic imports for heavy components; route-based code splitting is automatic.

### Metadata

Static export for fixed metadata, `generateMetadata` for dynamic per-route. Essentials: title (50-60 chars), description (150-160 chars), Open Graph images, canonical URL.

### Caching

Control caching at three layers: request (`fetch` options), data (`revalidate`/tags), and full route (route config). Revalidate by time (`revalidate: 60`), on-demand (`revalidatePath`/`revalidateTag`), or disable with `no-store`.

### Anti-patterns

| Don't | Do |
|-------|-----|
| `'use client'` everywhere | Server by default |
| Fetch in Client Components | Fetch on the server |
| Skip loading states | Use `loading.tsx` |
| Ignore error boundaries | Use `error.tsx` |
| Large client bundles | Dynamic imports |

### Project structure

```
app/
├── (marketing)/        # route group
│   └── page.tsx
├── (dashboard)/
│   ├── layout.tsx
│   └── page.tsx
├── api/
│   └── [resource]/
│       └── route.ts
└── components/
    └── ui/
```
