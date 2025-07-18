
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from datetime import datetime, timedelta

app = FastAPI(title="WellNest: Health & Wellness To-Do List", description="Organize, track, and improve your daily habits and wellness routines.", version="3.0")
templates = Jinja2Templates(directory="templates")

# In-memory task storage for demo (replace with DB for production)
tasks = []
task_id_counter = 0
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Pre-populate with diverse tasks
def get_initial_tasks():
    return [
        {"id": 0, "category": "mental", "description": "Meditate for 10 minutes under a tree", "deadline": "2025-07-20T09:00:00", "completed": False, "notes": "Try to focus on breathing.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 1, "category": "physical", "description": "Do 25 push-ups and 30 squats", "deadline": "2025-07-19T18:00:00", "completed": False, "notes": "Warm up first.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 2, "category": "nutrition", "description": "Make a smoothie with 5 different greens", "deadline": "2025-07-21T08:00:00", "completed": False, "notes": "Spinach, kale, mint, parsley, celery.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 3, "category": "experimental", "description": "Try cold shower challenge for 7 days", "deadline": "2025-07-25T07:00:00", "completed": False, "notes": "Start with 30 seconds.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 4, "category": "nature", "description": "Take a barefoot walk on grass", "deadline": "2025-07-19T07:00:00", "completed": True, "notes": "Felt refreshing!", "file": None, "created_at": str(datetime.now()), "completed_at": str(datetime.now())},
        {"id": 5, "category": "adventurous", "description": "Try goat yoga in a nearby farm", "deadline": "2025-07-22T10:00:00", "completed": False, "notes": "Book a slot online.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 6, "category": "mental", "description": "Write a gratitude journal entry", "deadline": "2025-07-19T21:00:00", "completed": False, "notes": "Reflect on the day.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 7, "category": "physical", "description": "Go for a sunrise jog in the neighborhood", "deadline": "2025-07-20T06:00:00", "completed": False, "notes": "Set alarm for 5:30am.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 8, "category": "nutrition", "description": "Try going sugar-free for a day", "deadline": "2025-07-23T00:00:00", "completed": False, "notes": "Check all food labels.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
        {"id": 9, "category": "experimental", "description": "Track sleep with a wearable and adjust routine", "deadline": "2025-07-24T23:00:00", "completed": False, "notes": "Analyze sleep data.", "file": None, "created_at": str(datetime.now()), "completed_at": None},
    ]

if not tasks:
    task_id_counter = 0
    tasks.extend(get_initial_tasks())
    task_id_counter = len(tasks)

@app.get("/", include_in_schema=False)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Task CRUD, Completion, Notes, Upload, Search, Analytics ---
@app.get("/tasks/")
def list_tasks(category: str = None, search: str = None, sort: str = None, show: str = "active"):
    filtered = tasks
    if category:
        filtered = [t for t in filtered if t["category"] == category]
    if search:
        filtered = [t for t in filtered if search.lower() in t["description"].lower() or (t["notes"] and search.lower() in t["notes"].lower())]
    if show == "completed":
        filtered = [t for t in filtered if t["completed"]]
    elif show == "archived":
        filtered = [t for t in filtered if t.get("archived")]  # future use
    else:
        filtered = [t for t in filtered if not t["completed"] and not t.get("archived")]
    if sort == "date":
        filtered.sort(key=lambda t: t["deadline"] or "")
    elif sort == "category":
        filtered.sort(key=lambda t: t["category"])
    elif sort == "status":
        filtered.sort(key=lambda t: t["completed"], reverse=True)
    return filtered

@app.post("/tasks/")
async def add_task(
    category: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(None),
    notes: str = Form(None),
    file: UploadFile = File(None)
):
    global task_id_counter
    file_path = None
    if file:
        file_path = os.path.join(uploads_dir, f"{task_id_counter}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    task = {
        "id": task_id_counter,
        "category": category,
        "description": description,
        "deadline": deadline,
        "completed": False,
        "notes": notes,
        "file": file_path,
        "created_at": str(datetime.now()),
        "completed_at": None
    }
    tasks.append(task)
    task_id_counter += 1
    return task

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, category: str = Form(...), description: str = Form(...), deadline: str = Form(None), notes: str = Form(None), file: UploadFile = File(None)):
    for t in tasks:
        if t["id"] == task_id:
            t["category"] = category
            t["description"] = description
            t["deadline"] = deadline
            t["notes"] = notes
            if file:
                file_path = os.path.join(uploads_dir, f"{task_id}_{file.filename}")
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                t["file"] = file_path
            return t
    return JSONResponse(status_code=404, content={"error": "Task not found"})

@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            t["completed"] = True
            t["completed_at"] = str(datetime.now())
            return t
    return JSONResponse(status_code=404, content={"error": "Task not found"})

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            return {"deleted": True}
    return JSONResponse(status_code=404, content={"error": "Task not found"})

# --- Analytics, Streaks, Gamification, Quotes ---
@app.get("/analytics/")
def analytics():
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    by_category = {}
    for t in tasks:
        by_category.setdefault(t["category"], {"total": 0, "completed": 0})
        by_category[t["category"]]["total"] += 1
        if t["completed"]:
            by_category[t["category"]]["completed"] += 1
    # Streak: count consecutive days with at least one completed task
    streak = 0
    today = datetime.now().date()
    for i in range(0, 30):
        day = today - timedelta(days=i)
        if any(t["completed"] and t["completed_at"] and datetime.fromisoformat(t["completed_at"]).date() == day for t in tasks):
            streak += 1
        else:
            break
    # Points: 10 per completed task, 5 per overdue completed, 1 per note
    points = sum(10 for t in tasks if t["completed"]) + sum(5 for t in tasks if t["completed"] and t["deadline"] and datetime.fromisoformat(t["completed_at"]) > datetime.fromisoformat(t["deadline"])) + sum(1 for t in tasks if t["notes"])
    return {"total": total, "completed": completed, "by_category": by_category, "streak": streak, "points": points}

@app.get("/quote/")
def quote():
    import random
    quotes = [
        "Small daily improvements are the key to staggering long-term results.",
        "Wellness is the natural state of my body.",
        "Every day is a fresh start.",
        "You are stronger than you think.",
        "Progress, not perfection.",
        "Consistency is more important than intensity.",
        "Take care of your body. It's the only place you have to live."
    ]
    return {"quote": random.choice(quotes)}

@app.get("/", include_in_schema=False)
def root(request: Request):
    """
    Serve the professional interactive HTML frontend.
    """
    return templates.TemplateResponse("index.html", {"request": request})