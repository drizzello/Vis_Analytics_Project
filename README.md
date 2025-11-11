# Visual Analytics Project

Interactive dashboard for inspecting fishing vessel activity.The repo contains:

- `backend/` – FastAPI service exposing the analytics APIs.
- `frontend/` – Vue 3 single-page app that consumes those APIs.
- `Python_EDA/` & `backend/data/` – exploratory notebooks and parquet datasets used by the service.

Below is the minimal setup required to run everything locally.

---

## 1. Prerequisites

| Tool    | Version (tested)    |
| ------- | ------------------- |
| Python  | 3.14.0              |
| Node.js | 22.15.1 (with npm) |
| pip     | latest              |

You also need the parquet datasets already checked into `backend/data/`.

---

## 2. Backend (FastAPI)

1. **Create and activate a virtual environment**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  
   ```
2. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r ../requirements.txt
   ```
3. **Start the API**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The service boots on `http://127.0.0.1:8000`. API docs: `http://127.0.0.1:8000/docs`.

> **Note:** The API reads Parquet files directly from `backend/data/`. Keep that folder alongside the backend when deploying.

---

## 3. Frontend (Vue 3 + Vite)

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```
2. **Run the dev server**
   ```bash
   npm run dev -- --host
   ```

   Vite prints a local URL (default `http://127.0.0.1:5173`). The app expects the API at `http://127.0.0.1:8000`, so keep the backend running.

### Building for production

```bash
npm run build
npm run preview
```

`dist/` contains the static assets you can upload to any static host.

---

## 4. Common Issues & Tips

- **Missing data**: ensure `backend/data/*.parquet` exists; otherwise the loaders will raise errors.
- **Port conflicts**: change ports via `--port` in the `uvicorn` command and `npm run dev -- --port 5173`.
- **CORS**: `backend/main.py` already allows `http://localhost:5173`. Adjust `allow_origins` if you serve the frontend from another origin.

---
