# SKYGRID INDIA — Vercel-ready starter

A simulation-only urban air mobility dashboard. This package is configured to serve the static frontend and FastAPI API from a **single Vercel project**.

## Important limitations

- This is a hackathon/demo simulation, not certified aviation software or real flight-control software.
- The fleet telemetry is synthetic.
- Configure a hosted PostgreSQL database in Vercel before using incident history or simulation writes. Without `DATABASE_URL`, the app starts safely and `/health` plus `/api/fleet` work, while database-backed endpoints return HTTP 503 with setup guidance.
- Deployment must be verified in your own Vercel account; account permissions, platform limits, and database credentials cannot be pre-tested from this ZIP.

## Repository structure

```text
api/index.py               Vercel Python entry point
backend/app/main.py        FastAPI routes and static frontend serving
backend/app/database.py    SQLAlchemy database configuration
backend/app/models.py      Incident model
frontend/                  HTML, CSS and JavaScript dashboard
vercel.json                Vercel Python function routing
requirements.txt           Dependencies installed for Vercel
```

## Deploy via GitHub → Vercel

1. Extract the ZIP.
2. Create a GitHub repository.
3. Upload the *contents* of this folder to the repository root (not an extra enclosing folder).
4. In Vercel, choose **Add New → Project**, import that repository, and keep the project root as the repository root.
5. Keep the preset as **FastAPI** and the Root Directory as `./`. Deploy this as a single FastAPI application; do not choose the multi-service import flow for this `vercel.json`.
6. Open `https://YOUR-DEPLOYMENT.vercel.app/`. Test `/health`, `/docs`, and `/api/fleet` first.
7. If Vercel's Python runtime still shows `vc_handler` / `vercel_runtime` import errors, open the deployment's build/runtime logs; that is a platform/runtime configuration issue and may require redeploying with Vercel's current FastAPI preset.

## Persistent database setup

1. Create a hosted PostgreSQL database from a provider of your choice.
2. In Vercel → Project → Settings → Environment Variables, add `DATABASE_URL` using the provider's connection string.
3. If your provider supplies a `postgres://` or `postgresql://` URL, the application normalizes it to the psycopg SQLAlchemy driver.
4. Redeploy after setting environment variables.
5. Test `POST /api/simulate/tick` from `/docs`, then refresh `/api/incidents`.

Never commit database passwords or `.env` files to GitHub.

## Local run (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///./skygrid_local.db"
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/docs`.

## Troubleshooting

- **404**: confirm `vercel.json`, `api/index.py`, and root `requirements.txt` were committed at the repository root.
- **500**: inspect Vercel Function Logs; check Python dependencies and `DATABASE_URL`.
- **Database unavailable**: confirm the database allows connections from the hosted application and the connection string is valid.
- **Frontend opens but API fails**: this package uses same-origin relative requests (`/health`, `/api/...`) so it does not need a hard-coded localhost URL.
