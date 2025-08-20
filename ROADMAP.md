# Community Packing List — Comprehensive Development Roadmap

This roadmap provides a complete development strategy focusing on critical infrastructure fixes, security hardening, UI/UX modernization, and Docker deployment setup. All development follows Django + TypeScript best practices with a security-first approach.

## 🚨 Critical Issues (Immediate Action Required)

### Security Vulnerabilities
- **DEBUG=True in production** - Exposes sensitive information
- **Weak SECRET_KEY** - Uses Django's insecure default
- **Missing security headers** - No HSTS, CSP, secure cookies
- **No rate limiting** - Vulnerable to brute force attacks

### Test Infrastructure Failures
- **22 Django test errors** - Missing URLs, undefined functions
- **8 Django test failures** - Form validation, model issues
- **Jest environment broken** - Missing jest-environment-jsdom
- **ESLint configuration broken** - Missing TypeScript packages

### Code Quality Issues
- **Console.log in production** - Debug code left in TypeScript files
- **Missing type safety** - Any types throughout codebase
- **Inconsistent error handling** - Mix of alert() and Modal.alert()
- **No pre-commit hooks** - No automated quality checks

## Guiding Principles
- **Security first** - All changes must pass security review
- **Test-driven development** - Fix tests before adding features
- **Accessibility first** (keyboard navigation, ARIA, color contrast)
- **Mobile-first responsive layouts**
- **Docker-based deployment** - Consistent environments
- **Progressive enhancement** - Fast, resilient features with graceful fallbacks
- **Clean code** - No console.log, proper types, consistent patterns

## Branch Strategy & Git Workflow

### Branch Naming Convention
- `fix/` - Bug fixes and corrections
- `feat/` - New features
- `perf/` - Performance improvements
- `docs/` - Documentation updates
- `test/` - Test additions/fixes
- `refactor/` - Code refactoring
- `style/` - UI/UX improvements
- `chore/` - Build/config updates
- `security/` - Security fixes

### Recommended Branches for Each Phase
1. **Phase 0 (Today):** `security/critical-fixes` - Security hardening
2. **Phase 0 (Today):** `fix/test-infrastructure` - Fix Jest and Django tests
3. **Phase 1:** `feat/docker-local-deployment` - Docker compose setup
4. **Phase 2:** `style/ui-modernization` - CSS improvements, dark mode
5. **Phase 3:** `feat/complete-features` - Geographic features, auth
6. **Phase 4:** `perf/optimization` - Code splitting, caching

## Phase 0 — Critical Security & Infrastructure Fixes (TODAY - 2 days)
**Branch:** `security/critical-fixes` and `fix/test-infrastructure`

### Security Hardening (URGENT)
- [ ] Generate new SECRET_KEY using Django's get_random_secret_key()
- [ ] Set DEBUG=False for production settings
- [ ] Add SECURE_HSTS_SECONDS = 31536000
- [ ] Enable SECURE_SSL_REDIRECT = True
- [ ] Set SESSION_COOKIE_SECURE = True
- [ ] Set CSRF_COOKIE_SECURE = True
- [ ] Implement rate limiting middleware
- [ ] Add CSP headers configuration
- [ ] Remove .env from git tracking

### Test Infrastructure Restoration
- [ ] Install jest-environment-jsdom
- [ ] Fix ESLint configuration and install missing packages
- [ ] Fix haversine function import in views.py
- [ ] Add missing URL patterns in urls.py
- [ ] Fix Item model nsn_lin field reference
- [ ] Update form validation for price limits
- [ ] Run and fix all Django tests
- [ ] Set up pre-commit hooks

### Development Tooling
- [ ] Remove all console.log statements from production code
- [ ] Replace 'any' types with proper TypeScript types
- [ ] Standardize error handling (use Modal.alert consistently)
- [ ] Configure TypeScript strict mode

## Phase 1 — Docker Local Deployment (Days 3-5)
**Branch:** `feat/docker-local-deployment`

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

- Access Control & Trust Model
  - Restrict creating/editing Stores and Packing Lists to authenticated users.
  - Allow all users to submit Prices, but weight trust by IP history; adjust confidence for low-trust IPs.
  - Display partial IP hash (last 4 chars) for anonymous price submissions in UI tooltips/details.

- Macro View (Time Series)
  - Add Items “Macro” page: time-series charts of average/min/max price per item over selectable ranges (30/90/180 days).
  - Server: expose JSON endpoints using `Item.get_price_history(days=N)`; aggregate per day.
  - UI: simple chart (Chart.js) per item with filters (store, region, confidence).

- Accessibility
  - Ensure all interactive controls have labels and focus states (partially done in `base.html`; verified on items table icons and actions).
  - Trap focus inside modals; verify ESC closes and focus returns to the trigger (already partially implemented).
  - Replace decorative emojis with accessible SVGs + `aria-label` (completed on items page price and link icons).

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
  - Show submitter trust level and masked IP fragment for anonymous prices.

- Print & Export
  - Dedicated print stylesheet for Packing List detail (hide chrome, show checkboxes cleanly).
  - Ensure existing PDF export is discoverable via consistent action placement.

- Theming & Preferences
  - Dark mode toggle (prefers-color-scheme default, persisted in `localStorage`).
  - Macro dashboards: compare multiple items over time; export CSV.

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


