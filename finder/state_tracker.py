import sqlite3
import hashlib
import contextlib
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# Valid application status progression:
#   DISCOVERED -> RESUME_GENERATED -> FORM_FILLED -> PENDING_CONFIRM -> SUBMITTED
#                                                                    \-> SKIPPED
# A human (via the extension popup's ConfirmPanel, or the dashboard) always
# reviews a PENDING_CONFIRM application before it becomes SUBMITTED — the
# agent never transitions a job to SUBMITTED itself.

class StateTracker:
    def __init__(self, db_path: str = "applications.db"):
        self.db_path = db_path
        self._init_db()

    @contextlib.contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id      TEXT UNIQUE NOT NULL,
                    company     TEXT NOT NULL,
                    role_title  TEXT NOT NULL,
                    url         TEXT NOT NULL,
                    platform    TEXT NOT NULL,
                    tier        INTEGER NOT NULL,
                    tier_score  INTEGER NOT NULL,
                    stipend_min INTEGER NOT NULL,
                    stipend_raw TEXT,
                    status      TEXT NOT NULL DEFAULT 'DISCOVERED',
                    resume_path TEXT,
                    applied_at  TEXT,
                    created_at  TEXT NOT NULL,
                    jd_text     TEXT
                )
            ''')
            conn.commit()
            self._ensure_column(conn, "applications", "fill_preview", "TEXT")

    @staticmethod
    def _ensure_column(conn: sqlite3.Connection, table: str, column: str, sql_type: str) -> None:
        """Add a column to an existing table if it isn't already there (idempotent migration)."""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cursor.fetchall()}
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
            conn.commit()

    def generate_job_id(self, company: str, role_title: str, url: str) -> str:
        raw = f"{company}|{role_title}|{url}".lower()
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]

    def add_job(self, job: Dict[str, Any]) -> str:
        job_id = job.get('job_id')
        if not job_id:
            job_id = self.generate_job_id(job['company'], job['role_title'], job['url'])
            
        with self._get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO applications (
                        job_id, company, role_title, url, platform, tier, tier_score, 
                        stipend_min, stipend_raw, status, created_at, jd_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job_id,
                    job['company'],
                    job['role_title'],
                    job['url'],
                    job['platform'],
                    job['tier'],
                    job['tier_score'],
                    job['stipend_min'],
                    job.get('stipend_raw', ''),
                    job.get('status', 'DISCOVERED'),
                    datetime.now().isoformat(),
                    job.get('jd_text', '')
                ))
                conn.commit()
            except sqlite3.IntegrityError:
                pass # ignore if exists
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM applications WHERE job_id = ?', (job_id,))
            row = cursor.fetchone()
            if row:
                return self._deserialize_row(dict(row))
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM applications ORDER BY created_at DESC')
            return [self._deserialize_row(dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def _deserialize_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """Parses the fill_preview JSON column back into a dict for callers."""
        raw = row.get("fill_preview")
        if raw:
            try:
                row["fill_preview"] = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                row["fill_preview"] = None
        return row

    def update_status(self, job_id: str, status: str, resume_path: str = None):  # type: ignore
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            updates = ["status = ?"]
            params = [status]
            
            if resume_path is not None:
                updates.append("resume_path = ?")
                params.append(resume_path)
                
            if status in ('FORM_FILLED', 'PENDING_CONFIRM', 'SUBMITTED'):
                updates.append("applied_at = ?")
                params.append(datetime.now().isoformat())

            query = f"UPDATE applications SET {', '.join(updates)} WHERE job_id = ?"
            params.append(job_id)

            cursor.execute(query, tuple(params))
            conn.commit()

    def update_fill_preview(self, job_id: str, fill_preview: Dict[str, Any]) -> None:
        """Persist the {field_label: value} preview of what a form fill wrote, as JSON."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE applications SET fill_preview = ? WHERE job_id = ?',
                (json.dumps(fill_preview), job_id),
            )
            conn.commit()

    def is_duplicate(self, job_id: str) -> bool:
        return self.get_job(job_id) is not None

    def get_daily_count(self) -> int:
        today_prefix = datetime.now().isoformat()[:10] # YYYY-MM-DD
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM applications 
                WHERE (status = 'FORM_FILLED' OR status = 'PENDING_CONFIRM' OR status = 'SUBMITTED') 
                AND applied_at LIKE ?
            ''', (f"{today_prefix}%",))
            return cursor.fetchone()[0]
            
    def close(self):
        pass
