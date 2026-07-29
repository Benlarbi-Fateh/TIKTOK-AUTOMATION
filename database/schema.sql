PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    language TEXT DEFAULT 'fr',
    category TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    normalized_title TEXT,
    summary TEXT,
    source_url TEXT,
    source_name TEXT,
    published_at TEXT,
    collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
    category TEXT,
    viral_score INTEGER DEFAULT 0,
    originality_score INTEGER DEFAULT 0,
    affiliate_score INTEGER DEFAULT 0,
    final_score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new',
    fingerprint TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    title TEXT,
    hook TEXT,
    script_text TEXT NOT NULL,
    description TEXT,
    hashtags TEXT,
    scenes_json TEXT,
    sources_json TEXT,
    uncertainties_json TEXT,
    status TEXT DEFAULT 'draft',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (topic_id)
        REFERENCES topics(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER NOT NULL,
    project_folder TEXT,
    audio_path TEXT,
    subtitle_path TEXT,
    final_video_path TEXT,
    platform_id TEXT,
    status TEXT DEFAULT 'prepared',
    published_at TEXT,

    FOREIGN KEY (script_id)
        REFERENCES scripts(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    measured_at TEXT DEFAULT CURRENT_TIMESTAMP,
    hours_after_publish INTEGER,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    followers_gained INTEGER DEFAULT 0,
    average_watch_time REAL,
    completion_rate REAL,
    link_clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,

    FOREIGN KEY (video_id)
        REFERENCES videos(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_topics_status
ON topics(status);

CREATE INDEX IF NOT EXISTS idx_topics_final_score
ON topics(final_score);

CREATE INDEX IF NOT EXISTS idx_scripts_status
ON scripts(status);

CREATE INDEX IF NOT EXISTS idx_videos_status
ON videos(status);