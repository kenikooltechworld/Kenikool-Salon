# Docker Hot Reload Setup

## Problem
Docker containers weren't auto-refreshing when code changes were made. You had to manually stop and restart containers to see changes.

## Solution
Updated `docker-compose.yml` to enable hot-reload for both frontend and backend:

### Frontend (React/Vite)
**Change:** Added `command: npm run dev -- --host 0.0.0.0`

**How it works:**
- Runs Vite dev server instead of production build
- `--host 0.0.0.0` exposes the dev server to Docker network
- Vite automatically detects file changes and hot-reloads in browser
- No container restart needed

**Result:** Changes to React files appear instantly in browser

### Backend (FastAPI)
**Change:** Added `command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

**How it works:**
- `--reload` flag enables auto-reload on file changes
- Uvicorn watches for Python file changes and restarts the app
- `--host 0.0.0.0` exposes API to Docker network
- No container restart needed

**Result:** Changes to Python files are automatically reloaded

## Usage

### Start containers with hot-reload:
```bash
docker-compose up
```

### Make changes:
- Edit React files → See changes instantly in browser (HMR)
- Edit Python files → API automatically reloads

### Stop containers:
```bash
docker-compose down
```

## What's Mounted
- `./backend:/app` - Backend code (watches for changes)
- `./salon:/app` - Frontend code (watches for changes)
- `/app/node_modules` - Named volume to prevent node_modules conflicts

## Performance Notes
- Hot-reload adds slight overhead but is worth it for development
- For production, remove `--reload` flag and use production builds
- If changes aren't detected, check file permissions or try restarting container

## Troubleshooting

**Frontend changes not showing:**
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for errors
- Restart frontend container: `docker-compose restart frontend`

**Backend changes not reloading:**
- Check Docker logs: `docker-compose logs api`
- Ensure Python syntax is correct
- Restart backend container: `docker-compose restart api`

**Volume mount issues on Windows:**
- Use WSL2 backend for Docker Desktop
- Ensure file sharing is enabled in Docker settings
- Try using absolute paths in docker-compose.yml
