import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to create tables
CREATE_TABLES_SQL = """
-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    level TEXT,
    category TEXT,
    duration_minutes INTEGER,
    video_url TEXT,
    content TEXT,
    "order" INTEGER
);

-- Theory table
CREATE TABLE IF NOT EXISTS theory (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    "order" INTEGER
);

-- Sheet music table
CREATE TABLE IF NOT EXISTS sheet_music (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    composer TEXT,
    difficulty TEXT,
    description TEXT,
    notation TEXT,
    "order" INTEGER
);

-- Care guides table
CREATE TABLE IF NOT EXISTS care_guides (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    "order" INTEGER
);

-- Practice logs table
CREATE TABLE IF NOT EXISTS practice_logs (
    id TEXT PRIMARY KEY,
    date TEXT,
    duration_minutes INTEGER,
    notes TEXT,
    lesson_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Progress table
CREATE TABLE IF NOT EXISTS progress (
    id TEXT PRIMARY KEY,
    item_id TEXT,
    item_type TEXT,
    completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bookmarks table
CREATE TABLE IF NOT EXISTS bookmarks (
    id TEXT PRIMARY KEY,
    item_id TEXT,
    item_type TEXT,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Schedule table
CREATE TABLE IF NOT EXISTS schedule (
    id TEXT PRIMARY KEY,
    day_of_week INTEGER,
    time TEXT,
    duration_minutes INTEGER,
    focus_area TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

# Seed data
LESSONS = [
    {"id": str(uuid.uuid4()), "title": "Getting Started: Parts of the Violin", "description": "Learn the anatomy of your violin and bow", "level": "beginner", "category": "fundamentals", "duration_minutes": 15, "video_url": "https://www.youtube.com/embed/RXFjqghCmGE", "content": "The violin consists of the body, neck, scroll, pegbox, fingerboard, bridge, tailpiece, chinrest, and f-holes. The bow has a stick, hair, frog, and tip.", "order": 1},
    {"id": str(uuid.uuid4()), "title": "Proper Posture and Holding the Violin", "description": "Master the correct stance and violin position", "level": "beginner", "category": "fundamentals", "duration_minutes": 20, "video_url": "https://www.youtube.com/embed/3PoTxPvNfT4", "content": "Stand straight with feet shoulder-width apart. Rest the violin on your collarbone and support it with your chin. Your left hand should form a relaxed C-shape around the neck.", "order": 2},
    {"id": str(uuid.uuid4()), "title": "Holding the Bow Correctly", "description": "Learn the proper bow grip for beautiful tone", "level": "beginner", "category": "bowing", "duration_minutes": 20, "video_url": "https://www.youtube.com/embed/I5qhSCcplio", "content": "The bow hold uses a curved thumb, relaxed fingers, and a bent pinky on top of the stick. Practice the 'bunny ears' exercise to develop flexibility.", "order": 3},
    {"id": str(uuid.uuid4()), "title": "Open String Bowing", "description": "Practice smooth bowing on open strings", "level": "beginner", "category": "bowing", "duration_minutes": 25, "video_url": "https://www.youtube.com/embed/jHDi4cMJTx8", "content": "Start with long, slow bow strokes on each open string (G, D, A, E). Focus on keeping the bow parallel to the bridge and maintaining even pressure.", "order": 4},
    {"id": str(uuid.uuid4()), "title": "First Finger Placement", "description": "Introduction to left hand finger positioning", "level": "beginner", "category": "finger_positioning", "duration_minutes": 25, "video_url": "https://www.youtube.com/embed/vgIVPZ1XSUU", "content": "Place your first finger a whole step above the open string. On the A string, this gives you B. Practice alternating between open A and first finger B.", "order": 5},
    {"id": str(uuid.uuid4()), "title": "Playing Your First Scale: D Major", "description": "Learn the D major scale one octave", "level": "beginner", "category": "technique", "duration_minutes": 30, "video_url": "https://www.youtube.com/embed/oWwp1jm1CtM", "content": "D Major scale: D-E-F#-G-A-B-C#-D. Start on open D string, use fingers 1-2-3, cross to A string, open-1-2-3. Practice slowly with good intonation.", "order": 6},
    {"id": str(uuid.uuid4()), "title": "Vibrato Fundamentals", "description": "Introduction to arm and wrist vibrato", "level": "intermediate", "category": "technique", "duration_minutes": 35, "video_url": "https://www.youtube.com/embed/HvJgg3J9lZM", "content": "Vibrato is an oscillation of pitch that adds warmth to your tone. Start with arm vibrato: rock your arm back and forth while keeping finger contact. Practice on each finger separately.", "order": 7},
    {"id": str(uuid.uuid4()), "title": "Shifting to Third Position", "description": "Learn to shift smoothly between positions", "level": "intermediate", "category": "finger_positioning", "duration_minutes": 40, "video_url": "https://www.youtube.com/embed/YT7LzJpG4AE", "content": "Third position places your first finger where your third finger was in first position. Use guide notes and practice slow, smooth shifts with light thumb pressure.", "order": 8},
    {"id": str(uuid.uuid4()), "title": "Advanced Bowing: Spiccato", "description": "Master the bouncing bow technique", "level": "advanced", "category": "bowing", "duration_minutes": 40, "video_url": "https://www.youtube.com/embed/4mYhKGHl_0I", "content": "Spiccato is a controlled bouncing bow stroke. Find the balance point of your bow, use a relaxed arm, and let gravity help the bow bounce naturally.", "order": 9},
    {"id": str(uuid.uuid4()), "title": "Double Stops and Chords", "description": "Playing two strings simultaneously", "level": "advanced", "category": "technique", "duration_minutes": 45, "video_url": "https://www.youtube.com/embed/5cMjj98qKbk", "content": "Double stops require pressing two strings and bowing both simultaneously. Start with open string combinations, then add fingers. Focus on keeping both strings ringing clearly.", "order": 10},
]

THEORY = [
    {"id": str(uuid.uuid4()), "title": "Reading Music Notation", "description": "Understanding the staff, clef, and notes", "content": "The violin reads treble clef. Lines are E-G-B-D-F (Every Good Boy Does Fine). Spaces are F-A-C-E. Ledger lines extend the staff above and below.", "order": 1},
    {"id": str(uuid.uuid4()), "title": "Rhythm and Time Signatures", "description": "Understanding note values and counting", "content": "Whole note = 4 beats, half note = 2 beats, quarter = 1, eighth = 1/2. Time signatures tell beats per measure (top) and beat unit (bottom). 4/4 is common time.", "order": 2},
    {"id": str(uuid.uuid4()), "title": "Key Signatures", "description": "Sharps, flats, and major/minor keys", "content": "Key signatures indicate which notes are consistently sharp or flat. Circle of fifths: C-G-D-A-E-B-F# (sharps), C-F-Bb-Eb-Ab-Db-Gb (flats). Relative minors are 3 half-steps below.", "order": 3},
    {"id": str(uuid.uuid4()), "title": "Intervals", "description": "Understanding distance between notes", "content": "Intervals measure distance: unison, 2nd, 3rd, 4th, 5th, 6th, 7th, octave. Quality: major, minor, perfect, augmented, diminished. Perfect intervals: unison, 4th, 5th, octave.", "order": 4},
    {"id": str(uuid.uuid4()), "title": "Dynamics and Expression", "description": "Volume and musical expression markings", "content": "Dynamics: pp (very soft), p (soft), mp (medium soft), mf (medium loud), f (loud), ff (very loud). Crescendo = get louder, decrescendo = get softer. Accent marks emphasize notes.", "order": 5},
    {"id": str(uuid.uuid4()), "title": "Tempo Markings", "description": "Understanding speed indications", "content": "Tempo terms: Largo (very slow), Adagio (slow), Andante (walking), Moderato (moderate), Allegro (fast), Presto (very fast). Metronome markings give exact BPM.", "order": 6},
]

SHEET_MUSIC = [
    {"id": str(uuid.uuid4()), "title": "Twinkle Twinkle Little Star", "composer": "Traditional", "difficulty": "beginner", "description": "A classic beginner piece", "notation": "D D A A | B B A - | G G F# F# | E E D -", "order": 1},
    {"id": str(uuid.uuid4()), "title": "Ode to Joy", "composer": "Beethoven", "difficulty": "beginner", "description": "Theme from Symphony No. 9", "notation": "E E F G | G F E D | C C D E | E D D -", "order": 2},
    {"id": str(uuid.uuid4()), "title": "Minuet in G", "composer": "J.S. Bach", "difficulty": "beginner", "description": "A elegant baroque dance", "notation": "D G A B c | D - G - | E c D c B | A - D -", "order": 3},
    {"id": str(uuid.uuid4()), "title": "Canon in D", "composer": "Pachelbel", "difficulty": "intermediate", "description": "The famous wedding piece", "notation": "F# E D C# | B A B C# | D F# A G | F# D F# E", "order": 4},
    {"id": str(uuid.uuid4()), "title": "Air on the G String", "composer": "J.S. Bach", "difficulty": "intermediate", "description": "From Orchestral Suite No. 3", "notation": "D - B - | A G F# E | D C# D E | A - - -", "order": 5},
    {"id": str(uuid.uuid4()), "title": "Spring (Four Seasons)", "composer": "Vivaldi", "difficulty": "intermediate", "description": "Allegro from Spring concerto", "notation": "E E E D C# | D D D C# B | C# D E F# | E - - -", "order": 6},
    {"id": str(uuid.uuid4()), "title": "Meditation from Thais", "composer": "Massenet", "difficulty": "intermediate", "description": "Beautiful romantic intermezzo", "notation": "D - F# - | A - G - | F# E D C# | D - - -", "order": 7},
    {"id": str(uuid.uuid4()), "title": "Czardas", "composer": "Monti", "difficulty": "advanced", "description": "Virtuosic Hungarian dance", "notation": "D E F# G A | B C# D E F# | G - F# E | D - - -", "order": 8},
    {"id": str(uuid.uuid4()), "title": "Introduction and Rondo Capriccioso", "composer": "Saint-Saens", "difficulty": "advanced", "description": "Brilliant showpiece", "notation": "A - C# E | A G# A B | C# B A G# | A - - -", "order": 9},
    {"id": str(uuid.uuid4()), "title": "Violin Concerto in E minor", "composer": "Mendelssohn", "difficulty": "advanced", "description": "First movement theme", "notation": "E - G B | E' D# E' F# | G F# E D# | E - - -", "order": 10},
    {"id": str(uuid.uuid4()), "title": "Zigeunerweisen", "composer": "Sarasate", "difficulty": "advanced", "description": "Gypsy Airs - virtuoso piece", "notation": "C - E G | C' B C' D' | E' D' C' B | C' - - -", "order": 11},
    {"id": str(uuid.uuid4()), "title": "Caprice No. 24", "composer": "Paganini", "difficulty": "advanced", "description": "Theme and variations", "notation": "A - E' C# | A - E' C# | D' C# B A | G# A B C#", "order": 12},
]

CARE_GUIDES = [
    {"id": str(uuid.uuid4()), "title": "Daily Cleaning Routine", "description": "Keep your violin in top condition", "content": "After each practice: 1) Wipe strings with dry cloth to remove rosin. 2) Wipe body with soft cloth. 3) Loosen bow hair slightly. 4) Store in case. Never use water or household cleaners on your violin.", "order": 1},
    {"id": str(uuid.uuid4()), "title": "Rosin Application", "description": "How to apply rosin properly", "content": "New rosin needs 'breaking in' - scratch surface lightly with sandpaper. Apply 3-5 strokes for daily use, more for new hair. Too much rosin creates scratchy sound; too little causes slipping.", "order": 2},
    {"id": str(uuid.uuid4()), "title": "String Care and Replacement", "description": "When and how to change strings", "content": "Replace strings every 3-6 months or when tone degrades. Change one string at a time to maintain bridge position. Wind neatly on pegs, stretch new strings gently. Wipe strings after playing.", "order": 3},
    {"id": str(uuid.uuid4()), "title": "Bridge and Soundpost", "description": "Understanding these critical parts", "content": "The bridge should stand straight, perpendicular to the top. If it leans, have a luthier adjust it. The soundpost inside transfers vibrations - never attempt to adjust it yourself.", "order": 4},
    {"id": str(uuid.uuid4()), "title": "Storage and Travel", "description": "Protecting your instrument", "content": "Always store in a hard case. Maintain 40-60% humidity with a humidifier in dry climates. Avoid extreme temperatures. Never leave in car. Use a good shoulder rest and case straps for travel.", "order": 5},
]

def create_tables():
    """Create tables using Supabase SQL editor (requires manual step or use REST API)"""
    print("Creating tables...")
    # Since we can't run raw SQL directly, we'll try inserting data
    # The tables need to be created via Supabase Dashboard SQL Editor
    # But we can seed data if tables exist
    
def seed_data():
    """Seed the database with initial data"""
    print("Seeding lessons...")
    for lesson in LESSONS:
        try:
            supabase.table("lessons").upsert(lesson).execute()
            print(f"  ✓ {lesson['title']}")
        except Exception as e:
            print(f"  ✗ {lesson['title']}: {e}")
    
    print("\nSeeding theory...")
    for topic in THEORY:
        try:
            supabase.table("theory").upsert(topic).execute()
            print(f"  ✓ {topic['title']}")
        except Exception as e:
            print(f"  ✗ {topic['title']}: {e}")
    
    print("\nSeeding sheet music...")
    for piece in SHEET_MUSIC:
        try:
            supabase.table("sheet_music").upsert(piece).execute()
            print(f"  ✓ {piece['title']}")
        except Exception as e:
            print(f"  ✗ {piece['title']}: {e}")
    
    print("\nSeeding care guides...")
    for guide in CARE_GUIDES:
        try:
            supabase.table("care_guides").upsert(guide).execute()
            print(f"  ✓ {guide['title']}")
        except Exception as e:
            print(f"  ✗ {guide['title']}: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Virtuoso - Supabase Setup")
    print("=" * 50)
    print("\n⚠️  IMPORTANT: You need to create the tables first!")
    print("Copy the SQL below and run it in Supabase SQL Editor:\n")
    print(CREATE_TABLES_SQL)
    print("\n" + "=" * 50)
    print("After creating tables, run this script again to seed data.")
    print("=" * 50)
    
    response = input("\nHave you created the tables? (y/n): ")
    if response.lower() == 'y':
        seed_data()
        print("\n✅ Setup complete!")
    else:
        print("\nPlease create the tables first, then run this script again.")
