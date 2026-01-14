# utils/database.py
import sqlite3
from contextlib import contextmanager
from pathlib import Path

class Database:
    def __init__(self, db_path='data/bot.db'):
        self.db_path = db_path
        # Создаём директорию если не существует
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with self.get_connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP,
                    is_banned BOOLEAN DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS subscriptions (
                    user_id INTEGER PRIMARY KEY,
                    plan TEXT DEFAULT 'free',
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    generations_used INTEGER DEFAULT 0,
                    invoice_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                
                CREATE TABLE IF NOT EXISTS generations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_generations_user 
                ON generations(user_id, created_at);
            ''')
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # === User methods ===
    def get_user(self, user_id: int):
        with self.get_connection() as conn:
            return conn.execute(
                'SELECT * FROM users WHERE user_id = ?', 
                (user_id,)
            ).fetchone()
    
    def create_user(self, user_id: int, username: str = None):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR IGNORE INTO users (user_id, username, last_active)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username))
    
    def update_user_activity(self, user_id: int):
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE users SET last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
    
    def ban_user(self, user_id: int, banned: bool = True):
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE users SET is_banned = ?
                WHERE user_id = ?
            ''', (banned, user_id))
    
    def is_banned(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        return user['is_banned'] if user else False
    
    # === Subscription methods ===
    def get_subscription(self, user_id: int):
        with self.get_connection() as conn:
            return conn.execute(
                'SELECT * FROM subscriptions WHERE user_id = ?',
                (user_id,)
            ).fetchone()
    
    def set_subscription(self, user_id: int, plan: str, end_date: str, invoice_id: str = None):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO subscriptions (user_id, plan, start_date, end_date, invoice_id)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    plan = excluded.plan,
                    start_date = CURRENT_TIMESTAMP,
                    end_date = excluded.end_date,
                    generations_used = 0,
                    invoice_id = excluded.invoice_id
            ''', (user_id, plan, end_date, invoice_id))
    
    def increment_generations(self, user_id: int):
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE subscriptions 
                SET generations_used = generations_used + 1
                WHERE user_id = ?
            ''', (user_id,))
    
    # === Generation logging ===
    def log_generation(self, user_id: int, gen_type: str, success: bool = True):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO generations (user_id, type, success)
                VALUES (?, ?, ?)
            ''', (user_id, gen_type, success))
    
    def get_user_generations_today(self, user_id: int) -> int:
        with self.get_connection() as conn:
            result = conn.execute('''
                SELECT COUNT(*) as count FROM generations
                WHERE user_id = ? AND DATE(created_at) = DATE('now')
            ''', (user_id,)).fetchone()
            return result['count'] if result else 0
    
    # === Stats ===
    def get_total_users(self) -> int:
        with self.get_connection() as conn:
            result = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()
            return result['count'] if result else 0
    
    def get_active_users_today(self) -> int:
        with self.get_connection() as conn:
            result = conn.execute('''
                SELECT COUNT(*) as count FROM users
                WHERE DATE(last_active) = DATE('now')
            ''').fetchone()
            return result['count'] if result else 0
    
    def get_generations_today(self) -> int:
        with self.get_connection() as conn:
            result = conn.execute('''
                SELECT COUNT(*) as count FROM generations
                WHERE DATE(created_at) = DATE('now')
            ''').fetchone()
            return result['count'] if result else 0
    
    def get_paid_users(self) -> int:
        with self.get_connection() as conn:
            result = conn.execute('''
                SELECT COUNT(*) as count FROM subscriptions
                WHERE plan != 'free' AND end_date > CURRENT_TIMESTAMP
            ''').fetchone()
            return result['count'] if result else 0
