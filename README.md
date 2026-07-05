Here is a short, punchy markdown cheat sheet you can save as a file (like README.md or todo.txt) inside your ~/my-python-stack directory to quickly spin up your project next time.
## 🚀 Stack Start Checklist## 1. Turn on the Engine

podman machine start

## 2. Jump to Project Folder

cd ~/my-bak-stack

## 3. Create the Pod Sandbox

podman pod create --name my-bak-pod -p 8000:8000 -p 5432:5432

## 4. Spin up the Event Store (Postgres DB)

podman run -d \
  --name db \
  --pod my-bak-pod \
  -e POSTGRES_DB=events_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  docker.io/library/postgres:15-alpine

## 5. Launch the Web Application Server

podman run -d \
  --name web \
  --pod my-bak-pod \
  -v "${PWD}/app:/app:Z" \
  -w /app \
  -e INFRASTRUCTURE_FACTORY="eventsourcing.postgres:Factory" \
  -e POSTGRES_DBNAME="events_db" \
  -e POSTGRES_USER="postgres" \
  -e POSTGRES_PASSWORD="postgres" \
  -e POSTGRES_HOST="127.0.0.1" \
  -e POSTGRES_PORT="5432" \
  docker.io/library/python:3.11-slim \
  bash -c "pip install fastapi 'uvicorn[standard]' eventsourcing 'psycopg[binary]' psycopg_pool python-multipart && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

## 6. Watch the Output Logs

podman logs -f web

------------------------------
## 🛑 Control Commands

* Stop everything: podman pod stop my-stack-pod
* Start everything back up: podman pod start my-stack-pod
* Wipe containers to start fresh: podman rm -f db web && podman pod rm my-stack-pod

Would you like to add comments or details to any of these steps before you save it, or should we move on to inspecting how the events are stored in the database?

