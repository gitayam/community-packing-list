# Community Packing List - React Frontend

Modern React 19 + TypeScript frontend for the Community Packing List application, deployed on Cloudflare Pages.

## 🚀 Live Demo

- **Production:** https://community-packing-list.pages.dev
- **Latest Deploy:** https://4a186e90.community-packing-list.pages.dev

## 🛠️ Tech Stack

- **React 19** - Latest React with modern patterns
- **TypeScript 5.9** - Type safety
- **Vite 7** - Lightning-fast build tool
- **TanStack Query 5** - Server state management
- **React Router 7** - Client-side routing
- **React Hook Form + Zod** - Form handling & validation
- **Tailwind CSS 4** - Utility-first styling
- **Axios** - HTTP client
- **Cloudflare Pages** - Edge deployment

## ✨ Modern React Features

### Suspense & Error Boundaries
```tsx
<Suspense fallback={<Skeleton />}>
  <DataComponent />
</Suspense>
```

### Skeleton Loading States
- Professional loading UX
- Animated pulse effect
- Card, Table, and List skeletons

### Error Handling
- App-wide ErrorBoundary
- Graceful error recovery
- User-friendly error messages

### React Query
- Automatic retries with exponential backoff
- Optimistic updates
- Cache management
- Devtools integration

## 📁 Project Structure

```
src/
├── components/
│   ├── ErrorBoundary.tsx      # App-wide error handling
│   ├── layout/                # Header, Footer, Layout
│   ├── packing-lists/         # Feature components
│   └── ui/                    # Reusable UI (Button, Input, Card, etc.)
├── pages/
│   ├── HomePage.tsx           # List of packing lists
│   ├── CreateListPage.tsx     # Create new list
│   ├── UploadListPage.tsx     # File upload
│   ├── ListDetailPage.tsx     # List details with items
│   ├── StoreListPage.tsx      # Store management
│   └── NotFoundPage.tsx       # 404 page
├── hooks/
│   ├── usePackingLists.ts     # Packing list queries
│   ├── usePackingListMutations.ts  # CRUD mutations
│   ├── usePrices.ts           # Price queries
│   └── useStores.ts           # Store queries
├── lib/
│   ├── api.ts                 # Axios API client
│   ├── schemas.ts             # Zod validation schemas
│   └── utils.ts               # Utility functions
├── types/
│   └── index.ts               # TypeScript types
└── App.tsx                    # Root component
```

## 🏃 Getting Started

### Prerequisites
- Node.js 18+ (or latest LTS)
- npm or pnpm

### Installation

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Visit http://localhost:5173

### Environment Variables

Create `.env.local`:

```env
VITE_API_URL=http://localhost:8000/api
```

## 🔧 Available Scripts

```bash
# Development
npm run dev              # Start dev server (port 5173)

# Build
npm run build            # TypeScript + Vite production build
npm run preview          # Preview production build

# Deployment
npm run wrangler:dev     # Test with Wrangler locally
npm run wrangler:deploy  # Deploy to Cloudflare Pages

# Linting
npm run lint             # ESLint
```

## 🎨 Military Theme

The app uses a custom military color palette:

```css
--military-olive: #4B5320
--military-navy: #1B365D
--military-khaki: #C3B091
--military-sand: #F4F1DE
--military-dark: #2C2C2C

--status-required: #DC3545
--status-optional: #FFC107
--status-complete: #28A745
--status-pending: #6C757D
```

## 📡 API Integration

### Django Backend

The React app connects to a Django REST API:

**Base URL:** `http://localhost:8000/api` (dev) or configured via `VITE_API_URL`

**Endpoints:**
- `GET /api/packing-lists/` - List all packing lists
- `GET /api/packing-lists/:id/detail_view/` - Get list with items and prices
- `POST /api/packing-lists/` - Create new list
- `POST /api/packing-lists/:id/toggle_packed/` - Toggle item packed status
- `GET /api/stores/` - List all stores
- `POST /api/stores/` - Create store
- `POST /api/votes/` - Vote on price

See [API Documentation](../docs/API.md) for full endpoint list.

## 🚀 Deployment

### Cloudflare Pages

```bash
# Login to Cloudflare
npx wrangler login

# Deploy
npm run wrangler:deploy
```

### Build Settings

- **Build command:** `npm run build`
- **Build output:** `dist`
- **Environment variables:** `VITE_API_URL`

## 🧪 Testing

```bash
# Run tests (when available)
npm run test

# Type checking
npx tsc --noEmit
```

## 📦 Bundle Size

Latest production build:
- **Total:** 461.21 kB
- **Gzipped:** 144.28 kB
- **Build time:** ~1s

## 🎯 Features

- ✅ Create, edit, delete packing lists
- ✅ Upload files (CSV, Excel, PDF)
- ✅ Item management with packed status
- ✅ Price tracking with community voting
- ✅ Store management
- ✅ Search & filter items
- ✅ Section grouping
- ✅ NSN/LIN code support
- ✅ Required item indicators
- ✅ Mobile responsive design

## 🔐 CORS Configuration

The Django backend must allow CORS from:
- `http://localhost:5173` (development)
- `https://community-packing-list.pages.dev` (production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting and type checks
5. Submit a pull request

## 📝 License

See main project LICENSE

## 🙏 Acknowledgments

Built with modern React 19 patterns and deployed on Cloudflare's edge network for maximum performance.

**Migration Date:** October 2025
**Original:** Django templates
**New Stack:** React 19 + TypeScript + Vite + Cloudflare Pages
