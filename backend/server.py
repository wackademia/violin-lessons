import os
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Optional

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

app = FastAPI(title="Virtuoso - Violin Learning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models ───
class PracticeLogCreate(BaseModel):
    date: str
    duration_minutes: int
    notes: Optional[str] = ""
    lesson_id: Optional[str] = None

class BookmarkCreate(BaseModel):
    item_id: str
    item_type: str  # "lesson", "sheet_music", "theory"
    title: str

class ProgressUpdate(BaseModel):
    item_id: str
    item_type: str
    completed: bool

class ScheduleCreate(BaseModel):
    day_of_week: int  # 0-6
    time: str
    duration_minutes: int
    focus_area: Optional[str] = "General Practice"

# ─── Health ───
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Virtuoso Violin API"}

# ─── Lessons ───
@app.get("/api/lessons")
async def get_lessons():
    result = supabase.table("lessons").select("*").order("order").execute()
    return result.data

@app.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    result = supabase.table("lessons").select("*").eq("id", lesson_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return result.data[0]

# ─── Music Theory ───
@app.get("/api/theory")
async def get_theory_topics():
    result = supabase.table("theory").select("*").order("order").execute()
    return result.data

@app.get("/api/theory/{topic_id}")
async def get_theory_topic(topic_id: str):
    result = supabase.table("theory").select("*").eq("id", topic_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Topic not found")
    return result.data[0]

# ─── Sheet Music ───
@app.get("/api/sheet-music")
async def get_sheet_music(difficulty: Optional[str] = None, composer: Optional[str] = None):
    query = supabase.table("sheet_music").select("*")
    if difficulty:
        query = query.eq("difficulty", difficulty)
    if composer:
        query = query.eq("composer", composer)
    result = query.order("order").execute()
    return result.data

@app.get("/api/sheet-music/{piece_id}")
async def get_sheet_music_piece(piece_id: str):
    result = supabase.table("sheet_music").select("*").eq("id", piece_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Piece not found")
    return result.data[0]

# ─── Care & Maintenance ───
@app.get("/api/care-guides")
async def get_care_guides():
    result = supabase.table("care_guides").select("*").order("order").execute()
    return result.data

@app.get("/api/care-guides/{guide_id}")
async def get_care_guide(guide_id: str):
    result = supabase.table("care_guides").select("*").eq("id", guide_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Guide not found")
    return result.data[0]

# ─── Practice Logs ───
@app.get("/api/practice-logs")
async def get_practice_logs():
    result = supabase.table("practice_logs").select("*").order("date", desc=True).execute()
    return result.data

@app.post("/api/practice-logs", status_code=201)
async def create_practice_log(log: PracticeLogCreate):
    log_data = {
        "id": str(uuid.uuid4()),
        "date": log.date,
        "duration_minutes": log.duration_minutes,
        "notes": log.notes,
        "lesson_id": log.lesson_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = supabase.table("practice_logs").insert(log_data).execute()
    return result.data[0]

@app.delete("/api/practice-logs/{log_id}")
async def delete_practice_log(log_id: str):
    result = supabase.table("practice_logs").delete().eq("id", log_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "deleted"}

# ─── Progress ───
@app.get("/api/progress")
async def get_progress():
    result = supabase.table("progress").select("*").execute()
    return result.data

@app.post("/api/progress")
async def update_progress(update: ProgressUpdate):
    existing = supabase.table("progress").select("*").eq("item_id", update.item_id).eq("item_type", update.item_type).execute()
    now = datetime.now(timezone.utc).isoformat()
    if existing.data:
        supabase.table("progress").update({
            "completed": update.completed,
            "updated_at": now
        }).eq("item_id", update.item_id).eq("item_type", update.item_type).execute()
    else:
        supabase.table("progress").insert({
            "id": str(uuid.uuid4()),
            "item_id": update.item_id,
            "item_type": update.item_type,
            "completed": update.completed,
            "updated_at": now
        }).execute()
    
    result = supabase.table("progress").select("*").eq("item_id", update.item_id).eq("item_type", update.item_type).execute()
    return result.data[0]

# ─── Bookmarks ───
@app.get("/api/bookmarks")
async def get_bookmarks():
    result = supabase.table("bookmarks").select("*").order("created_at", desc=True).execute()
    return result.data

@app.post("/api/bookmarks", status_code=201)
async def add_bookmark(bookmark: BookmarkCreate):
    existing = supabase.table("bookmarks").select("*").eq("item_id", bookmark.item_id).eq("item_type", bookmark.item_type).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Already bookmarked")
    bm_data = {
        "id": str(uuid.uuid4()),
        "item_id": bookmark.item_id,
        "item_type": bookmark.item_type,
        "title": bookmark.title,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = supabase.table("bookmarks").insert(bm_data).execute()
    return result.data[0]

@app.delete("/api/bookmarks/{bookmark_id}")
async def remove_bookmark(bookmark_id: str):
    result = supabase.table("bookmarks").delete().eq("id", bookmark_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"status": "deleted"}

# ─── Schedule ───
@app.get("/api/schedule")
async def get_schedule():
    result = supabase.table("schedule").select("*").execute()
    return result.data

@app.post("/api/schedule", status_code=201)
async def create_schedule(entry: ScheduleCreate):
    entry_data = {
        "id": str(uuid.uuid4()),
        "day_of_week": entry.day_of_week,
        "time": entry.time,
        "duration_minutes": entry.duration_minutes,
        "focus_area": entry.focus_area,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = supabase.table("schedule").insert(entry_data).execute()
    return result.data[0]

@app.delete("/api/schedule/{entry_id}")
async def delete_schedule(entry_id: str):
    result = supabase.table("schedule").delete().eq("id", entry_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}

# ─── Stats ───
@app.get("/api/stats")
async def get_stats():
    total_lessons = len(supabase.table("lessons").select("id").execute().data)
    completed_lessons = len(supabase.table("progress").select("id").eq("item_type", "lesson").eq("completed", True).execute().data)
    total_theory = len(supabase.table("theory").select("id").execute().data)
    completed_theory = len(supabase.table("progress").select("id").eq("item_type", "theory").eq("completed", True).execute().data)
    
    logs = supabase.table("practice_logs").select("duration_minutes").execute().data
    total_practice_minutes = sum(log.get("duration_minutes", 0) for log in logs)
    
    # Calculate streak
    practice_dates = supabase.table("practice_logs").select("date").order("date", desc=True).execute().data
    streak = 0
    if practice_dates:
        today = datetime.now(timezone.utc).date()
        dates = sorted(set(d["date"] for d in practice_dates), reverse=True)
        for i, date_str in enumerate(dates):
            try:
                d = datetime.fromisoformat(date_str).date()
            except (ValueError, TypeError):
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
            expected = today if i == 0 else (today - timedelta(days=i))
            if d == expected or (i == 0 and (today - d).days <= 1):
                streak += 1
            else:
                break

    total_sheet_music = len(supabase.table("sheet_music").select("id").execute().data)
    bookmarks_count = len(supabase.table("bookmarks").select("id").execute().data)

    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "total_theory": total_theory,
        "completed_theory": completed_theory,
        "total_practice_minutes": total_practice_minutes,
        "practice_streak": streak,
        "total_sheet_music": total_sheet_music,
        "bookmarks_count": bookmarks_count
    }
