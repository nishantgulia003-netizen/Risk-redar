# RiskRadar frontend

The dashboard expects the FastAPI service to be available at `VITE_API_BASE_URL`.

```bash
npm install
cp .env.example .env
npm run dev
```

Start the backend separately (normally `docker compose up` from `backend/`). The default development URL is `http://localhost:8000`.
