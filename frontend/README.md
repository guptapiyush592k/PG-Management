# PG Manager — Admin Dashboard

Production-grade frontend for Paying Guest (PG) property management. Built with React, TypeScript, Tailwind CSS, and Material UI.

## Features

- Dashboard with occupancy & payment analytics
- Flats, rooms, beds, and tenant management
- Payments tracking with status filters
- WhatsApp notification UI (mock)
- Reports with charts and export actions
- Settings (profile, notifications, theme, security)
- Light / dark mode
- Responsive collapsible sidebar

## Stack

- React 18 + TypeScript
- Vite
- Tailwind CSS + MUI
- React Router
- Redux Toolkit (UI + entity state)
- React Hook Form
- Recharts

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

```bash
npm run build   # production build
npm run preview # preview production build
```

## Project structure

```
src/
  app/           # App shell, router, Redux store, slices, providers
  components/    # Shared layout & UI components
  modules/       # Feature pages (dashboard, flats, rooms, …)
  mock-data/     # Mock JSON datasets (split by domain)
  services/      # mockApi delay helper
  types/         # TypeScript types
  hooks/         # Custom hooks (dispatch, mock fetch)
  lib/           # Utilities, theme, selectors
```

All data is mock-only; no backend or authentication is implemented.
