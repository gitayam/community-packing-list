# Community Packing List — Product & UX/UI Roadmap

This roadmap focuses on elevating usability, accessibility, and visual quality while keeping performance and maintainability at the forefront. All development should follow the Docker-only workflow and Django + TypeScript best practices in this repo.

## Guiding Principles
- Accessibility first (keyboard navigation, ARIA, color contrast)
- Mobile-first responsive layouts
- Don’t ship unnecessary data to the client (server-side filtering/pagination)
- Consistent components and design tokens (CSS custom properties already in use)
- Progressive enhancement: fast, resilient features with graceful fallbacks

## Phase 1 — Foundation and Quick Wins (1–2 sprints)

- Navigation & IA
  - Add global quick search entry in the header to find Lists, Items, and Stores.
  - Improve current active/hover states (already partially implemented) to be consistent across all routes.

- Visual Consistency
  - DONE: Replace emojis with SVGs in `packing_list_detail.html` actions and indicators.
  - IN PROGRESS: Remove inline styles from `home.html`, `lists.html`, `items.html`; utilities added in `src/styles/main.css`.
  - IN PROGRESS: Normalize button variants to `.btn` system on `home.html`, `lists.html`, `packing_list_detail.html`.
  - DONE: Standardized bulk actions UI (hidden class toggle) and removed inline styles from `lists.html` and `items.html`.

- Modal Unification
  - NEXT: Use `src/components/Modal.ts` everywhere (price/edit item modals on items and packing list pages).
  - NEXT: Extract duplicated modal logic from templates into TypeScript helpers; prefer data attributes over inline `onclick`.

- Items & Lists Usability
  - DONE: Server-side pagination for Items and Lists; keep filters in querystring for shareable URLs.
  - DONE: Persist Card/Table view selection for Items via `localStorage`.
  - Add empty states and loading states where missing.

- Accessibility
  - Ensure all interactive controls have labels and focus states (partially done in `base.html`).
  - Trap focus inside modals; verify ESC closes and focus returns to the trigger (already partially implemented).
  - Replace decorative emojis with accessible SVGs + `aria-label`.

- Acceptance
  - No inline styles remain in the noted templates.
  - All modals are driven by the shared Modal component.
  - Core pages pass axe DevTools checks for critical issues.

## Phase 2 — Featureful UX (4–6 weeks)

- Global Search
  - Header search with typeahead across Lists, Items, Stores (server endpoint + minimal JSON).
  - Keyboard support: Arrow to navigate results, Enter to go.

- Store UX Improvements
  - Map view (Leaflet) on Stores page and in price context where applicable.
  - Improve base-radius filter controls and feedback messages.

- Price Details & Voting
  - Convert price details popup into a reusable component; mobile-friendly layout.
  - Optimistic vote updates with clear undo and error feedback.

- Print & Export
  - Dedicated print stylesheet for Packing List detail (hide chrome, show checkboxes cleanly).
  - Ensure existing PDF export is discoverable via consistent action placement.

- Theming & Preferences
  - Dark mode toggle (prefers-color-scheme default, persisted in `localStorage`).

- Performance
  - Webpack code-splitting by route; lazy-load page scripts (detail, form, store list).
  - Image optimization for item images (sizes, lazy loading attributes).

- Acceptance
  - TTI not regressed; route JS bundles < 200KB gz each.
  - Lighthouse: Performance 90+, Accessibility 95+ on key pages.

## Phase 3 — Quality, Research, and Scaling (6–12 weeks)

- Usability polish from user feedback (empty states, microcopy, error messages).
- Saved filters and shareable views (querystring presets; persist last-used filters).
- Basic onboarding cues on first visit (inline tips, dismissible).
- E2E smoke tests (Playwright in Docker) for core flows: create list, add item, add price, vote, filter.

## Implementation Notes (by area)

- Templates (`packing_lists/templates/packing_lists/`)
  - Replace inline `style="…"` with utility classes defined in `src/styles/main.css`.
  - Use `{% static %}` SVG icons consistently, replacing emojis in action buttons.
  - Keep `{% url %}` names in templates; avoid hardcoded paths.

- TypeScript (`src/`)
  - Centralize modal and toast/notification helpers; avoid template-defined scripts.
  - Persist UI preferences (view mode, column toggles) via `localStorage`.
  - Add debounce for search inputs; throttle expensive DOM operations.

- Backend (Django)
  - Add paginated endpoints for Items/Lists views; maintain filters via query parameters.
  - Add minimal JSON endpoints for global search and price details.
  - Ensure CSRF and form validation remain intact for AJAX flows.

- Tooling & CI
  - Webpack code-splitting; dynamic imports per route.
  - Add Playwright container and CI job (Docker) for E2E smoke tests.

## Milestone Checklist

- Phase 1
  - [ ] Inline styles removed; templates rely on classes
  - [ ] SVG icons replace emojis across pages
  - [ ] Shared Modal component used for all modals
  - [ ] Pagination for Items and Lists
  - [ ] Axe passes for critical issues

- Phase 2
  - [ ] Header global search (Lists/Items/Stores)
  - [ ] Map view for stores (Leaflet)
  - [ ] Reusable price details component
  - [ ] Dark mode
  - [ ] Route-level code-splitting

- Phase 3
  - [ ] Saved filters / shareable views
  - [ ] Onboarding cues
  - [ ] E2E smoke tests in Docker CI

## Dependencies to Consider
- Leaflet (map), small icon set (inline SVGs), Playwright (Dockerized), axe-core (dev checks)

## Out of Scope (for now)
- Complex user account features and collaboration workflows beyond current data model.


