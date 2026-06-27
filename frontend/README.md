# PG Manager — Admin Dashboard

Production-grade frontend for Paying Guest (PG) property management. Connects to the PG Management FastAPI backend.

## Features

- JWT authentication (login, signup, token refresh)
- Dashboard with occupancy and payment analytics
- Properties: flats, rooms, beds, and resident assignment via bookings
- Residents management with profile drawer
- Payments tracking with summary stats and status filters
- Role-based permissions from `/me/context`
- Light / dark mode
- Responsive collapsible sidebar
- Loading skeletons and empty states on all data views

## Stack

- React 18 + TypeScript
- Vite
- MUI (Material UI)
- TanStack Query (server state)
- Redux Toolkit (UI state only)
- Axios (API layer)
- React Hook Form
- Recharts

## Getting started

1. Copy environment file and point at your backend:

```bash
cp .env.example .env
```

2. Install and run (backend must be running on port 8000):

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

For local dev, Vite proxies `/auth`, `/me`, and `/api` to `http://localhost:8000`. Set `VITE_API_BASE_URL=` (empty) in `.env` to use the proxy, or `http://localhost:8000` for direct calls.

```bash
npm run build   # production build
npm run preview # preview production build
```

## Project structure

```
src/
  app/              # App shell, router, Redux (UI), providers
  context/          # AuthContext (session)
  features/         # Feature pages (auth, dashboard, properties, …)
  services/         # Pure Axios API functions
  shared/
    components/     # Layout and reusable UI
    hooks/queries/  # TanStack Query hooks
    utils/          # Formatting, theme
    constants/      # API and query keys
    types/          # API TypeScript types
```

## Architecture rules

- **Server state** → TanStack Query only (never Redux)
- **UI state** → Redux (sidebar, theme)
- **API calls** → `services/` only; components use query hooks
- **Auth** → JWT stored in localStorage, auto-refresh on 401

See `.cursor/rules/frontend.mdc` for full conventions.
