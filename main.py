import json
import os
from datetime import date, datetime
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SP_DATA_PATH = Path(os.environ.get("SP_DATA_PATH", "/sp-data/sync-data.json"))


def load_sp_data() -> dict:
    if not SP_DATA_PATH.exists():
        return {}
    try:
        raw = SP_DATA_PATH.read_text(encoding="utf-8").strip()
        # Strip the pf_2__ prefix SP adds
        if "__" in raw:
            raw = raw.split("__", 1)[1]
        return json.loads(raw)
    except Exception as e:
        print(f"Error loading SP data: {e}")
        return {}


def parse_tasks(data: dict):
    today_str = date.today().isoformat()

    state = data.get("state", {})
    task_entities = state.get("task", {}).get("entities", {})
    project_entities = state.get("project", {}).get("entities", {})

    projects = {pid: p.get("title", "Inbox") for pid, p in project_entities.items()}

    today_tasks = []
    upcoming_tasks = []
    no_date_tasks = []

    for task_id, task in task_entities.items():
        if task.get("parentId"):
            continue
        if task.get("isDone"):
            continue

        title = task.get("title", "Untitled").strip()
        project_id = task.get("projectId")
        project_name = projects.get(project_id, "Inbox") if project_id else "Inbox"

        # SP stores due date as ms timestamp
        due_raw = task.get("dueDate") or task.get("plannedAt")
        due_str = None
        if due_raw:
            try:
                due_str = datetime.utcfromtimestamp(due_raw / 1000).date().isoformat()
            except Exception:
                due_str = None

        entry = {
            "title": title,
            "project_name": project_name,
            "due_str": due_str,
        }

        if due_str:
            if due_str <= today_str:
                today_tasks.append(entry)
            else:
                upcoming_tasks.append(entry)
        else:
            no_date_tasks.append(entry)

    today_tasks.sort(key=lambda t: t["due_str"])
    upcoming_tasks.sort(key=lambda t: t["due_str"])

    return today_tasks, upcoming_tasks, no_date_tasks


def fmt_date(d: str) -> str:
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d")
    except Exception:
        return d


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    data = load_sp_data()
    data_found = bool(data)
    today_tasks, upcoming_tasks, no_date_tasks = parse_tasks(data)
    today_str = date.today().isoformat()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "data_found": data_found,
        "today_tasks": today_tasks,
        "upcoming_tasks": upcoming_tasks,
        "no_date_tasks": no_date_tasks,
        "fmt_date": fmt_date,
        "today_str": today_str,
    })
