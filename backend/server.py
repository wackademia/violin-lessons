import os
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional, List

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await seed_data()
    yield
    client.close()

app = FastAPI(title="Virtuoso - Violin Learning API", lifespan=lifespan)

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
    lessons = await db.lessons.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return lessons

@app.get("/api/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    lesson = await db.lessons.find_one({"id": lesson_id}, {"_id": 0})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

# ─── Music Theory ───
@app.get("/api/theory")
async def get_theory_topics():
    topics = await db.theory.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return topics

@app.get("/api/theory/{topic_id}")
async def get_theory_topic(topic_id: str):
    topic = await db.theory.find_one({"id": topic_id}, {"_id": 0})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

# ─── Sheet Music ───
@app.get("/api/sheet-music")
async def get_sheet_music(difficulty: Optional[str] = None, composer: Optional[str] = None):
    query = {}
    if difficulty:
        query["difficulty"] = difficulty
    if composer:
        query["composer"] = composer
    music = await db.sheet_music.find(query, {"_id": 0}).sort("order", 1).to_list(200)
    return music

@app.get("/api/sheet-music/{piece_id}")
async def get_sheet_music_piece(piece_id: str):
    piece = await db.sheet_music.find_one({"id": piece_id}, {"_id": 0})
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")
    return piece

# ─── Care & Maintenance ───
@app.get("/api/care-guides")
async def get_care_guides():
    guides = await db.care_guides.find({}, {"_id": 0}).sort("order", 1).to_list(50)
    return guides

@app.get("/api/care-guides/{guide_id}")
async def get_care_guide(guide_id: str):
    guide = await db.care_guides.find_one({"id": guide_id}, {"_id": 0})
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide

# ─── Practice Logs ───
@app.get("/api/practice-logs")
async def get_practice_logs():
    logs = await db.practice_logs.find({}, {"_id": 0}).sort("date", -1).to_list(365)
    return logs

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
    await db.practice_logs.insert_one(log_data)
    log_data.pop("_id", None)
    return log_data

@app.delete("/api/practice-logs/{log_id}")
async def delete_practice_log(log_id: str):
    result = await db.practice_logs.delete_one({"id": log_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "deleted"}

# ─── Progress ───
@app.get("/api/progress")
async def get_progress():
    progress = await db.progress.find({}, {"_id": 0}).to_list(500)
    return progress

@app.post("/api/progress")
async def update_progress(update: ProgressUpdate):
    existing = await db.progress.find_one(
        {"item_id": update.item_id, "item_type": update.item_type}
    )
    if existing:
        await db.progress.update_one(
            {"item_id": update.item_id, "item_type": update.item_type},
            {"$set": {"completed": update.completed, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    else:
        progress_data = {
            "id": str(uuid.uuid4()),
            "item_id": update.item_id,
            "item_type": update.item_type,
            "completed": update.completed,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.progress.insert_one(progress_data)
    
    result = await db.progress.find_one(
        {"item_id": update.item_id, "item_type": update.item_type},
        {"_id": 0}
    )
    return result

# ─── Bookmarks ───
@app.get("/api/bookmarks")
async def get_bookmarks():
    bookmarks = await db.bookmarks.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return bookmarks

@app.post("/api/bookmarks", status_code=201)
async def add_bookmark(bookmark: BookmarkCreate):
    existing = await db.bookmarks.find_one(
        {"item_id": bookmark.item_id, "item_type": bookmark.item_type}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already bookmarked")
    bm_data = {
        "id": str(uuid.uuid4()),
        "item_id": bookmark.item_id,
        "item_type": bookmark.item_type,
        "title": bookmark.title,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.bookmarks.insert_one(bm_data)
    bm_data.pop("_id", None)
    return bm_data

@app.delete("/api/bookmarks/{bookmark_id}")
async def remove_bookmark(bookmark_id: str):
    result = await db.bookmarks.delete_one({"id": bookmark_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"status": "deleted"}

# ─── Schedule ───
@app.get("/api/schedule")
async def get_schedule():
    schedule = await db.schedule.find({}, {"_id": 0}).to_list(50)
    return schedule

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
    await db.schedule.insert_one(entry_data)
    entry_data.pop("_id", None)
    return entry_data

@app.delete("/api/schedule/{entry_id}")
async def delete_schedule(entry_id: str):
    result = await db.schedule.delete_one({"id": entry_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"status": "deleted"}

# ─── Stats ───
@app.get("/api/stats")
async def get_stats():
    total_lessons = await db.lessons.count_documents({})
    completed_lessons = await db.progress.count_documents({"item_type": "lesson", "completed": True})
    total_theory = await db.theory.count_documents({})
    completed_theory = await db.progress.count_documents({"item_type": "theory", "completed": True})
    total_practice_minutes = 0
    logs = await db.practice_logs.find({}, {"_id": 0, "duration_minutes": 1}).to_list(1000)
    for log in logs:
        total_practice_minutes += log.get("duration_minutes", 0)
    
    # Calculate streak
    practice_dates = await db.practice_logs.find({}, {"_id": 0, "date": 1}).sort("date", -1).to_list(365)
    streak = 0
    if practice_dates:
        today = datetime.now(timezone.utc).date()
        dates = sorted(set(d["date"] for d in practice_dates), reverse=True)
        for i, date_str in enumerate(dates):
            try:
                d = datetime.fromisoformat(date_str).date()
            except (ValueError, TypeError):
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
            expected = today if i == 0 else (today - __import__('datetime').timedelta(days=i))
            if d == expected or (i == 0 and (today - d).days <= 1):
                streak += 1
            else:
                break

    total_sheet_music = await db.sheet_music.count_documents({})
    bookmarks_count = await db.bookmarks.count_documents({})

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


# ─── Seed Data ───
async def seed_data():
    # Only seed if empty
    existing = await db.lessons.count_documents({})
    if existing > 0:
        return

    # ── Lessons ──
    lessons = [
        {
            "id": "lesson-1",
            "title": "Getting to Know Your Violin",
            "description": "Learn the parts of the violin, how to hold it, and basic setup.",
            "level": "beginner",
            "order": 1,
            "duration_minutes": 15,
            "category": "fundamentals",
            "youtube_id": "xXFqK2JCNzs",
            "content": [
                {"type": "text", "value": "Welcome to your violin journey! The violin is one of the most expressive instruments in the world. Before we make any sound, let's understand the instrument itself."},
                {"type": "heading", "value": "Parts of the Violin"},
                {"type": "text", "value": "The violin consists of several key parts: the scroll (decorative top), pegs (for tuning), fingerboard (where you press strings), strings (G, D, A, E from lowest to highest), bridge (supports strings), f-holes (sound holes), chin rest, and tailpiece."},
                {"type": "heading", "value": "Holding the Violin"},
                {"type": "text", "value": "Place the violin on your left collarbone. The chin rest should sit comfortably under your jaw (not your chin). Your left hand supports the neck - don't grip it tightly. The shoulder rest helps distribute weight evenly."},
                {"type": "tip", "value": "A shoulder rest is highly recommended for beginners. It prevents tension in your neck and shoulder."},
                {"type": "heading", "value": "Holding the Bow"},
                {"type": "text", "value": "The bow hold is crucial. Place your thumb bent on the underside of the stick, near the frog. Your fingers drape over the top naturally. Keep your hand relaxed - think of holding a small bird: firm enough not to let it fly away, gentle enough not to hurt it."}
            ]
        },
        {
            "id": "lesson-2",
            "title": "Your First Notes: Open Strings",
            "description": "Learn to play open strings with proper bowing technique.",
            "level": "beginner",
            "order": 2,
            "duration_minutes": 20,
            "category": "bowing",
            "youtube_id": "QpM1bPqUKRE",
            "content": [
                {"type": "text", "value": "Now that you know how to hold the violin and bow, let's make some music! We'll start with open strings - playing each string without pressing any fingers down."},
                {"type": "heading", "value": "The Four Open Strings"},
                {"type": "text", "value": "From lowest to highest: G (thickest string), D, A, E (thinnest string). Each string produces a different pitch when bowed."},
                {"type": "heading", "value": "Proper Bowing"},
                {"type": "text", "value": "Place the bow between the bridge and fingerboard, roughly in the middle. Draw the bow straight across the string, perpendicular to the strings. Use the full length of the bow. Apply gentle, consistent pressure."},
                {"type": "exercise", "value": "Practice Exercise: Bow each open string 4 times with whole bows. G-G-G-G, D-D-D-D, A-A-A-A, E-E-E-E. Focus on producing a clean, even tone."},
                {"type": "tip", "value": "If the sound is scratchy, you may be pressing too hard or bowing too close to the bridge. If it's airy/weak, add a little more weight from your arm."}
            ]
        },
        {
            "id": "lesson-3",
            "title": "First Finger Placement",
            "description": "Introduction to using your first finger (index) on all strings.",
            "level": "beginner",
            "order": 3,
            "duration_minutes": 25,
            "category": "finger_positioning",
            "youtube_id": "HnVuJuCPmPE",
            "content": [
                {"type": "text", "value": "After mastering open strings, it's time to add your first finger. This opens up a whole new world of notes!"},
                {"type": "heading", "value": "Finger Numbering"},
                {"type": "text", "value": "In violin, we number our left hand fingers: 1 = Index, 2 = Middle, 3 = Ring, 4 = Pinky. The thumb stays behind the neck and does NOT press strings."},
                {"type": "heading", "value": "First Finger Notes"},
                {"type": "text", "value": "When you place your first finger on each string: G string + 1st finger = A, D string + 1st finger = E, A string + 1st finger = B, E string + 1st finger = F#"},
                {"type": "exercise", "value": "Exercise: Alternate between open string and first finger. Open G - A (1st finger), Open D - E (1st finger). Do this slowly, 4 times each."},
                {"type": "tip", "value": "Press firmly with the tip of your finger, close to the nail. Your finger should be curved like a little hammer. Flat fingers produce unclear tones."}
            ]
        },
        {
            "id": "lesson-4",
            "title": "Bow Control & Dynamics",
            "description": "Master bow speed, pressure, and contact point for expressive playing.",
            "level": "beginner",
            "order": 4,
            "duration_minutes": 20,
            "category": "bowing",
            "youtube_id": "Kdh2yP-NR4I",
            "content": [
                {"type": "text", "value": "Great music isn't just about playing the right notes - it's about HOW you play them. Bow control is the key to expression on the violin."},
                {"type": "heading", "value": "Three Elements of Tone"},
                {"type": "text", "value": "1. Bow Speed: Faster bow = louder, more energetic. Slower bow = softer, more intimate. 2. Bow Pressure: More weight = stronger, fuller tone. Less weight = lighter, airier sound. 3. Contact Point: Near the bridge = brighter, more intense. Near the fingerboard = warmer, softer."},
                {"type": "exercise", "value": "Dynamic Exercise: Play an open A string starting very softly (piano), gradually getting louder (crescendo) to forte, then back to piano (decrescendo). Use the full bow."},
                {"type": "tip", "value": "Think of your arm weight flowing through the bow into the string. Don't press with your hand - let gravity and arm weight do the work."}
            ]
        },
        {
            "id": "lesson-5",
            "title": "Simple Melodies: Twinkle Twinkle",
            "description": "Play your first complete song using open strings and first finger.",
            "level": "beginner",
            "order": 5,
            "duration_minutes": 30,
            "category": "repertoire",
            "youtube_id": "pckHaykMrGk",
            "content": [
                {"type": "text", "value": "Congratulations! You now have enough skills to play your first melody. Twinkle Twinkle Little Star is a classic first piece for every violinist."},
                {"type": "heading", "value": "The Melody on A String"},
                {"type": "text", "value": "Using the A string: A-A-E-E-F#-F#-E (half note). That's 'Twinkle, twinkle, little star.' Using first and second fingers on the A string, you can play the entire melody."},
                {"type": "heading", "value": "Suzuki Variation: Mississippi Stop Stop"},
                {"type": "text", "value": "The Suzuki method teaches this melody with rhythm variations. The first variation uses the rhythm: 'Mississippi Stop Stop' (four sixteenths + two eighths). This builds both bow control and rhythm."},
                {"type": "exercise", "value": "Learn the first line slowly, note by note. Then try connecting the notes smoothly. Aim for 4 repetitions before moving to the next line."},
                {"type": "tip", "value": "Don't rush! Speed comes naturally with practice. Focus on clean, beautiful sound first."}
            ]
        },
        {
            "id": "lesson-6",
            "title": "Second and Third Fingers",
            "description": "Expand your range with second and third finger patterns.",
            "level": "beginner",
            "order": 6,
            "duration_minutes": 25,
            "category": "finger_positioning",
            "youtube_id": "lJ4n8h0BFNM",
            "content": [
                {"type": "text", "value": "Now let's add your second (middle) and third (ring) fingers. This gives you access to a full octave scale on each string."},
                {"type": "heading", "value": "D Major Scale"},
                {"type": "text", "value": "On the D string: D (open), E (1st finger), F# (2nd finger), G (3rd finger). On the A string: A (open), B (1st finger), C# (2nd finger), D (3rd finger). Together: D-E-F#-G-A-B-C#-D - a full D Major scale!"},
                {"type": "exercise", "value": "Practice the D Major scale ascending and descending, 4 times. Use one bow per note, maintaining steady tempo."},
                {"type": "tip", "value": "Keep fingers curved and close to the strings even when not pressing. This is called 'finger readiness' and speeds up your playing."}
            ]
        },
        {
            "id": "lesson-7",
            "title": "Shifting to Third Position",
            "description": "Introduction to left hand shifting and third position.",
            "level": "intermediate",
            "order": 7,
            "duration_minutes": 30,
            "category": "technique",
            "youtube_id": "k-2980HBGok",
            "content": [
                {"type": "text", "value": "Until now, you've played in 'first position' where your first finger sits near the scroll. Shifting to third position moves your entire hand higher up the fingerboard, giving access to higher notes."},
                {"type": "heading", "value": "The Shift"},
                {"type": "text", "value": "In third position, your first finger sits where your third finger was in first position. The shift should be a smooth gliding motion of the entire hand - don't just reach with your fingers."},
                {"type": "exercise", "value": "Shifting Exercise: On the A string, play B (1st finger, 1st position), then shift to D (1st finger, 3rd position). Repeat 10 times, focusing on a smooth slide."},
                {"type": "tip", "value": "Your thumb should travel with your hand. Don't anchor it in place. Think of your thumb and first finger as a unit."}
            ]
        },
        {
            "id": "lesson-8",
            "title": "Vibrato Fundamentals",
            "description": "Learn the basics of vibrato for expressive, warm tone.",
            "level": "intermediate",
            "order": 8,
            "duration_minutes": 35,
            "category": "technique",
            "youtube_id": "iEG8_mOSn8c",
            "content": [
                {"type": "text", "value": "Vibrato is the gentle oscillation of pitch that gives the violin its singing, warm quality. It's one of the most beautiful and personal aspects of violin playing."},
                {"type": "heading", "value": "Types of Vibrato"},
                {"type": "text", "value": "Arm vibrato: Motion originates from the forearm. Broader, slower oscillation. Wrist vibrato: Motion from the wrist. Quicker, more refined. Finger vibrato: Very subtle, from the finger itself. Advanced technique."},
                {"type": "heading", "value": "Starting with Arm Vibrato"},
                {"type": "text", "value": "Place your second finger firmly on the A string. Rock your forearm back and forth gently, allowing the fingertip to roll on the string. The pitch should oscillate slightly below and back to the target note."},
                {"type": "exercise", "value": "Vibrato Prep: Without the bow, practice the rocking motion on each finger. Start with 2nd finger (easiest), then 1st, 3rd. Use a metronome at 60 BPM, one rock per beat."},
                {"type": "tip", "value": "Vibrato takes weeks or months to develop. Be patient! Start slow and exaggerated, then gradually make it smoother and narrower."}
            ]
        },
        {
            "id": "lesson-9",
            "title": "Double Stops & Chords",
            "description": "Playing two strings simultaneously for harmonic richness.",
            "level": "advanced",
            "order": 9,
            "duration_minutes": 30,
            "category": "technique",
            "youtube_id": "FhKIwf0PJ30",
            "content": [
                {"type": "text", "value": "Double stops involve playing two strings at once. This technique creates harmony and is used extensively in advanced repertoire."},
                {"type": "heading", "value": "Basic Double Stops"},
                {"type": "text", "value": "Start with open string combinations: G+D, D+A, A+E. Apply even bow pressure across both strings. The bow must contact both strings simultaneously with a flat hair angle."},
                {"type": "exercise", "value": "Exercise: Play open G+D together for 4 whole bows. Then D+A, then A+E. Focus on both strings sounding equally."},
                {"type": "tip", "value": "Double stops require more bow weight than single notes. Adjust your contact point closer to the bridge for better resonance."}
            ]
        },
        {
            "id": "lesson-10",
            "title": "Spiccato & Advanced Bowing",
            "description": "Master off-the-string techniques for virtuosic passages.",
            "level": "advanced",
            "order": 10,
            "duration_minutes": 35,
            "category": "bowing",
            "youtube_id": "FqxKFaFLI1o",
            "content": [
                {"type": "text", "value": "Spiccato is a bouncing bow stroke where the bow leaves the string between notes. It's essential for fast passages in concertos and orchestral music."},
                {"type": "heading", "value": "The Bounce Point"},
                {"type": "text", "value": "Every bow has a natural bounce point, usually around the middle or slightly below. Find it by dropping your bow gently on the string and letting it bounce naturally."},
                {"type": "exercise", "value": "Spiccato Exercise: Start with short detaché strokes, gradually lifting the bow until it bounces. Practice on open strings at various speeds."},
                {"type": "tip", "value": "Spiccato uses the natural elasticity of the bow stick. Don't force the bounce - control it with subtle wrist movements."}
            ]
        }
    ]
    await db.lessons.insert_many(lessons)

    # ── Music Theory ──
    theory_topics = [
        {
            "id": "theory-1",
            "title": "Reading Musical Notation",
            "description": "Learn the treble clef, staff, and note names for violin.",
            "order": 1,
            "category": "notation",
            "content": [
                {"type": "text", "value": "The violin reads music in the treble clef (also called the G clef). The staff has 5 lines and 4 spaces, each representing a different note."},
                {"type": "heading", "value": "Lines of the Treble Clef"},
                {"type": "text", "value": "From bottom to top: E, G, B, D, F. Remember: 'Every Good Boy Does Fine.'"},
                {"type": "heading", "value": "Spaces of the Treble Clef"},
                {"type": "text", "value": "From bottom to top: F, A, C, E. They spell the word 'FACE.'"},
                {"type": "heading", "value": "Ledger Lines"},
                {"type": "text", "value": "Notes above or below the staff use short additional lines called ledger lines. Middle C sits on one ledger line below the treble clef staff."},
                {"type": "tip", "value": "Practice identifying notes daily using flashcards or apps. Speed in reading notes directly translates to easier sight-reading."}
            ]
        },
        {
            "id": "theory-2",
            "title": "Rhythm & Note Values",
            "description": "Understand whole notes, half notes, quarters, eighths, and more.",
            "order": 2,
            "category": "rhythm",
            "content": [
                {"type": "text", "value": "Rhythm is the foundation of music. Each note shape tells you how long to hold it."},
                {"type": "heading", "value": "Basic Note Values"},
                {"type": "text", "value": "Whole note (4 beats): Open oval, no stem. Half note (2 beats): Open oval with stem. Quarter note (1 beat): Filled oval with stem. Eighth note (1/2 beat): Filled oval with stem and flag. Sixteenth note (1/4 beat): Two flags."},
                {"type": "heading", "value": "Dotted Notes"},
                {"type": "text", "value": "A dot after a note adds half its value. A dotted half note = 3 beats. A dotted quarter = 1.5 beats."},
                {"type": "exercise", "value": "Clap these rhythms: 1) Four quarter notes. 2) Two half notes. 3) One whole note. 4) Eight eighth notes. All should take the same total time in 4/4."},
                {"type": "tip", "value": "Use a metronome! It's the single most important practice tool for developing steady rhythm."}
            ]
        },
        {
            "id": "theory-3",
            "title": "Key Signatures",
            "description": "Learn major and minor key signatures most common in violin music.",
            "order": 3,
            "category": "keys",
            "content": [
                {"type": "text", "value": "A key signature tells you which notes are consistently sharp or flat throughout a piece. It appears at the beginning of each line of music."},
                {"type": "heading", "value": "Common Violin Keys"},
                {"type": "text", "value": "G Major: 1 sharp (F#) - Very common, the violin's natural key. D Major: 2 sharps (F#, C#) - Extremely common. A Major: 3 sharps (F#, C#, G#) - Bright and brilliant. C Major: No sharps or flats - Simple but less resonant on violin."},
                {"type": "heading", "value": "Minor Keys"},
                {"type": "text", "value": "Each major key has a relative minor. G Major → E minor. D Major → B minor. A Major → F# minor. Minor keys share the same key signature as their relative major."},
                {"type": "tip", "value": "Violin repertoire heavily favors sharp keys (G, D, A, E major) because the open strings resonate in these keys. Flat keys are less common but still important."}
            ]
        },
        {
            "id": "theory-4",
            "title": "Time Signatures",
            "description": "Understand 4/4, 3/4, 6/8, and other time signatures.",
            "order": 4,
            "category": "rhythm",
            "content": [
                {"type": "text", "value": "Time signatures appear at the start of a piece and define the rhythmic framework."},
                {"type": "heading", "value": "Common Time Signatures"},
                {"type": "text", "value": "4/4 (Common Time): 4 quarter note beats per measure. Most common. 3/4 (Waltz Time): 3 quarter beats. Used in waltzes and minuets. 2/4 (March Time): 2 quarter beats. Brisk and march-like. 6/8 (Compound Duple): 6 eighth notes grouped as 2 groups of 3. Lilting feel."},
                {"type": "heading", "value": "Conducting Patterns"},
                {"type": "text", "value": "4/4: Down-Left-Right-Up. 3/4: Down-Right-Up. Understanding these helps when playing in orchestras or with accompaniment."},
                {"type": "exercise", "value": "Listen to: A Strauss Waltz (3/4), A Sousa March (2/4), A Gigue by Bach (6/8). Feel the difference in pulse."}
            ]
        },
        {
            "id": "theory-5",
            "title": "Musical Symbols & Dynamics",
            "description": "Interpret expression markings, dynamics, and articulation.",
            "order": 5,
            "category": "expression",
            "content": [
                {"type": "text", "value": "Musical symbols tell you HOW to play, not just WHAT to play. They are the soul of musical interpretation."},
                {"type": "heading", "value": "Dynamic Markings"},
                {"type": "text", "value": "pp (pianissimo): Very soft. p (piano): Soft. mp (mezzo piano): Moderately soft. mf (mezzo forte): Moderately loud. f (forte): Loud. ff (fortissimo): Very loud. Crescendo (<): Gradually louder. Decrescendo (>): Gradually softer."},
                {"type": "heading", "value": "Articulation for Violin"},
                {"type": "text", "value": "Legato (slur): Smooth, connected notes in one bow stroke. Staccato (dot): Short, separated notes. Accent (>): Emphasized note. Tenuto (-): Full value, slightly stressed. Pizzicato (pizz.): Pluck the string. Arco: Return to bowing after pizzicato."},
                {"type": "tip", "value": "Dynamics on violin are controlled primarily by bow speed and weight. Practice scales at every dynamic level to build control."}
            ]
        },
        {
            "id": "theory-6",
            "title": "Intervals & Ear Training",
            "description": "Recognize intervals by ear and understand their role in violin music.",
            "order": 6,
            "category": "ear_training",
            "content": [
                {"type": "text", "value": "An interval is the distance between two notes. Recognizing intervals is crucial for tuning, intonation, and sight-reading."},
                {"type": "heading", "value": "Common Intervals"},
                {"type": "text", "value": "Unison (same note), Minor 2nd (half step), Major 2nd (whole step), Minor 3rd, Major 3rd, Perfect 4th, Perfect 5th (violin open strings are all perfect 5ths apart!), Octave."},
                {"type": "heading", "value": "Interval Songs"},
                {"type": "text", "value": "Major 2nd: 'Happy Birthday' (first two notes). Major 3rd: 'Oh When the Saints'. Perfect 4th: 'Here Comes the Bride'. Perfect 5th: 'Twinkle Twinkle' (first to third note). Octave: 'Somewhere Over the Rainbow'."},
                {"type": "exercise", "value": "Play intervals on your violin starting from open A: A-B (2nd), A-C# (3rd), A-D (4th), A-E (5th). Sing each interval before playing it."}
            ]
        }
    ]
    await db.theory.insert_many(theory_topics)

    # ── Sheet Music ──
    sheet_music = [
        {"id": "sm-1", "title": "Twinkle, Twinkle, Little Star", "composer": "Traditional", "difficulty": "beginner", "order": 1, "genre": "folk", "key": "A Major", "time_signature": "4/4", "description": "The quintessential beginner piece. Uses open strings and first finger on A and E strings.", "notes": "A A E E F# F# E - D D C# C# B B A", "attribution": "Traditional melody, public domain"},
        {"id": "sm-2", "title": "Ode to Joy", "composer": "Beethoven", "difficulty": "beginner", "order": 2, "genre": "classical", "key": "D Major", "time_signature": "4/4", "description": "From Symphony No. 9. A beautiful melody using first position notes on D and A strings.", "notes": "F# F# G A A G F# E D D E F# F# E E", "attribution": "Ludwig van Beethoven, Symphony No. 9, public domain"},
        {"id": "sm-3", "title": "Minuet in G", "composer": "Bach", "difficulty": "beginner", "order": 3, "genre": "classical", "key": "G Major", "time_signature": "3/4", "description": "A graceful dance from the Notebook for Anna Magdalena Bach. Lovely for developing 3/4 time feel.", "notes": "D-G-A-B-C | D-G-G | E-C-D-E-F# | G-G-G", "attribution": "J.S. Bach (attr. Christian Petzold), public domain"},
        {"id": "sm-4", "title": "Lightly Row", "composer": "Traditional", "difficulty": "beginner", "order": 4, "genre": "folk", "key": "D Major", "time_signature": "4/4", "description": "A simple Suzuki method piece that teaches even bow strokes and basic first position notes.", "notes": "E C# C# - D B B - A B C# D E E E", "attribution": "Traditional German folk song, public domain"},
        {"id": "sm-5", "title": "Allegro (Suzuki Book 1)", "composer": "Shinichi Suzuki", "difficulty": "beginner", "order": 5, "genre": "educational", "key": "D Major", "time_signature": "4/4", "description": "An energetic piece that introduces faster bow changes and string crossings.", "notes": "D-E-F#-G | A-A-A | B-C#-D-E | A-A", "attribution": "Adapted from Suzuki Violin School, educational arrangement"},
        {"id": "sm-6", "title": "Spring (Four Seasons)", "composer": "Vivaldi", "difficulty": "intermediate", "order": 6, "genre": "classical", "key": "E Major", "time_signature": "4/4", "description": "The iconic opening theme from Vivaldi's Spring concerto. Features running sixteenth notes and joyful energy.", "notes": "E-E-E | D#-E-F#-E | E-E-E | D#-E-F#-E", "attribution": "Antonio Vivaldi, The Four Seasons, Op. 8 No. 1, public domain"},
        {"id": "sm-7", "title": "Ave Maria", "composer": "Bach/Gounod", "difficulty": "intermediate", "order": 7, "genre": "classical", "key": "C Major", "time_signature": "4/4", "description": "Gounod's melody over Bach's Prelude in C. A beautiful lyrical piece perfect for developing vibrato and tone.", "notes": "C-E-G-C | E-G-C-E | F-A-C-F | E-G-C-E", "attribution": "J.S. Bach / Charles Gounod, public domain"},
        {"id": "sm-8", "title": "Humoresque", "composer": "Dvorak", "difficulty": "intermediate", "order": 8, "genre": "classical", "key": "G-flat Major", "time_signature": "2/4", "description": "A playful, charming piece with dotted rhythms and expressive slides. Great for intermediate players.", "notes": "Gb-Ab-Bb-Cb | Db-Db-Eb | Db-Cb-Bb-Ab", "attribution": "Antonin Dvorak, Humoresque No. 7, public domain"},
        {"id": "sm-9", "title": "Meditation from Thais", "composer": "Massenet", "difficulty": "intermediate", "order": 9, "genre": "classical", "key": "D Major", "time_signature": "4/4", "description": "One of the most beautiful violin solos ever written. Requires expressive vibrato and controlled dynamics.", "notes": "A-D-F#-A | G-F#-E-D | A-G-F#-E", "attribution": "Jules Massenet, Thais, public domain"},
        {"id": "sm-10", "title": "Violin Concerto in A minor, 1st mvt", "composer": "Bach", "difficulty": "advanced", "order": 10, "genre": "classical", "key": "A minor", "time_signature": "2/4", "description": "A magnificent Baroque concerto. Features fast passages, string crossings, and Baroque ornamentation.", "notes": "A-C-E-A | G#-A-B-C | D-E-F-E | D-C-B-A", "attribution": "J.S. Bach, Violin Concerto No. 1, BWV 1041, public domain"},
        {"id": "sm-11", "title": "Violin Romance No. 2", "composer": "Beethoven", "difficulty": "advanced", "order": 11, "genre": "classical", "key": "F Major", "time_signature": "4/4", "description": "A lyrical, singing melody that showcases beautiful tone production and phrasing. Elegant and deeply moving.", "notes": "F-A-C-F | E-F-G-A | Bb-A-G-F", "attribution": "Ludwig van Beethoven, Romance No. 2, Op. 50, public domain"},
        {"id": "sm-12", "title": "Czardas", "composer": "Monti", "difficulty": "advanced", "order": 12, "genre": "classical", "key": "D minor", "time_signature": "4/4", "description": "A fiery Hungarian-style showpiece with slow, expressive sections and blazing fast virtuosic passages.", "notes": "D-F-A-D | C#-D-E-F | G-F-E-D", "attribution": "Vittorio Monti, Czardas, public domain"}
    ]
    await db.sheet_music.insert_many(sheet_music)

    # ── Care Guides ──
    care_guides = [
        {
            "id": "care-1",
            "title": "Daily Violin Cleaning",
            "description": "Essential daily care routine to keep your violin in top condition.",
            "order": 1,
            "icon": "sparkles",
            "content": [
                {"type": "text", "value": "Cleaning your violin after every practice session prevents rosin buildup and maintains the varnish."},
                {"type": "step", "value": "1. Use a soft, dry microfiber cloth to wipe the strings from scroll to bridge."},
                {"type": "step", "value": "2. Gently wipe the body of the violin, especially under the strings where rosin dust settles."},
                {"type": "step", "value": "3. Wipe the stick of the bow (not the hair!) with a separate clean cloth."},
                {"type": "step", "value": "4. Loosen the bow hair slightly (2-3 turns of the screw) before storing."},
                {"type": "warning", "value": "Never use alcohol, furniture polish, or water on your violin. These can damage the varnish irreparably."},
                {"type": "tip", "value": "Keep separate cloths for the body and strings. Rosin on the body cloth can smear the varnish."}
            ]
        },
        {
            "id": "care-2",
            "title": "Rosin Application Guide",
            "description": "How to properly apply rosin to your bow for optimal sound.",
            "order": 2,
            "icon": "wand",
            "content": [
                {"type": "text", "value": "Rosin creates friction between the bow hair and strings, which is what produces sound. Too little = weak, airy tone. Too much = scratchy, harsh sound."},
                {"type": "step", "value": "1. Tighten the bow to playing tension."},
                {"type": "step", "value": "2. Hold the rosin in one hand, bow in the other."},
                {"type": "step", "value": "3. Draw the bow slowly across the rosin from frog to tip, 3-5 times."},
                {"type": "step", "value": "4. For a new bow or new rosin, you may need 10-20 strokes initially."},
                {"type": "tip", "value": "High-quality rosin makes a significant difference. Dark rosin is softer and grippier (better for cold/dry climates). Light rosin is harder (better for warm/humid climates)."}
            ]
        },
        {
            "id": "care-3",
            "title": "String Replacement",
            "description": "Step-by-step guide to safely replace violin strings.",
            "order": 3,
            "icon": "wrench",
            "content": [
                {"type": "text", "value": "Violin strings lose their brilliance over time. Replace them every 3-6 months depending on how often you play."},
                {"type": "warning", "value": "Always replace strings ONE AT A TIME. Removing all strings at once can cause the sound post inside the violin to fall."},
                {"type": "step", "value": "1. Start with one string. Slowly unwind the peg until the string is loose."},
                {"type": "step", "value": "2. Remove the old string from the peg and tailpiece."},
                {"type": "step", "value": "3. Thread the new string through the tailpiece fine tuner (or hole)."},
                {"type": "step", "value": "4. Insert the other end into the peg hole and wind carefully, keeping tension even."},
                {"type": "step", "value": "5. Tune the string. New strings stretch and will go out of tune frequently for 1-2 days."},
                {"type": "step", "value": "6. Repeat for each remaining string."},
                {"type": "tip", "value": "Apply peg paste/chalk to pegs that slip. A tiny amount of pencil graphite in the nut and bridge grooves helps strings glide smoothly."}
            ]
        },
        {
            "id": "care-4",
            "title": "Bridge Care & Positioning",
            "description": "Maintain proper bridge alignment and positioning.",
            "order": 4,
            "icon": "ruler",
            "content": [
                {"type": "text", "value": "The bridge is held in place only by string tension and is NOT glued. It can shift over time and needs regular checking."},
                {"type": "step", "value": "1. Check that the bridge feet sit flat on the violin's top."},
                {"type": "step", "value": "2. The bridge should be centered between the inner notches of the f-holes."},
                {"type": "step", "value": "3. The back of the bridge (scroll side) should be perpendicular to the top of the violin."},
                {"type": "step", "value": "4. When tuning, strings can pull the bridge forward. Periodically check and gently push it back."},
                {"type": "warning", "value": "If the bridge falls, do not panic. Loosen the strings slightly, then carefully stand the bridge back up. If unsure, take it to a luthier."},
                {"type": "tip", "value": "A warped or badly fitted bridge significantly affects sound quality. A professional bridge fitting costs $30-80 and is well worth it."}
            ]
        },
        {
            "id": "care-5",
            "title": "Storage & Environment",
            "description": "Best practices for storing your violin safely.",
            "order": 5,
            "icon": "home",
            "content": [
                {"type": "text", "value": "Proper storage protects your violin from damage caused by temperature, humidity, and physical impact."},
                {"type": "step", "value": "1. Always store your violin in its case when not playing."},
                {"type": "step", "value": "2. Keep the case in a temperature-stable environment (65-75°F / 18-24°C)."},
                {"type": "step", "value": "3. Maintain humidity between 40-60%. Use a case humidifier in dry climates."},
                {"type": "step", "value": "4. Never leave your violin in a car, direct sunlight, or near heat sources."},
                {"type": "step", "value": "5. Close and latch the case properly. Many violins break from falling out of improperly closed cases."},
                {"type": "warning", "value": "Extreme temperature changes can crack the wood. If bringing your violin in from the cold, let it warm up gradually in the closed case for 15-20 minutes."},
                {"type": "tip", "value": "A quality hard case with good padding is one of the best investments you can make. It protects your instrument from bumps, falls, and climate changes."}
            ]
        }
    ]
    await db.care_guides.insert_many(care_guides)

    print("Database seeded successfully!")
