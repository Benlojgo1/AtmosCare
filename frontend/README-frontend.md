# AtmosCare Frontend (Vite + React + Tailwind)

## Prereqs
- Node.js 18+
- npm 9+

## Install
```bash
cd frontend
npm install
```

If you previously ran `npm i` at the project root by accident, remove any stray `node_modules` and run it inside `frontend/`.

## Run
```bash
npm run dev
```
Vite will print a local URL.

## Common Fixes
- **"Cannot find module 'react'"** → You likely didn't run `npm install` inside `frontend/`.
- **Vite plugin missing** → We added `@vitejs/plugin-react` to devDependencies.
- **Types not found** → Ensure `@types/react` and `@types/react-dom` installed (already in package.json). Re-run `npm i`.
- **Port busy** → Start Vite on another port: `npm run dev -- --port 5174`.
- **Backend URL** → Create `.env` in `frontend/` or root: `VITE_API_BASE=http://localhost:8000`.
