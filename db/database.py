"""
Database module for WorkBuddy app.
Handles SQLite database operations for app usage tracking.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "data/usage.db"):
        """Initialize database manager with SQLite database."""
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create app_usage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_seconds INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create daily_summary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_summary (
                    date TEXT PRIMARY KEY,
                    total_screen_time INTEGER,
                    top_apps TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create reminders_log table to track when reminders were sent
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reminder_type TEXT NOT NULL,
                    sent_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def log_app_usage(self, app_name: str, start_time: str, end_time: str = None, 
                     duration_seconds: int = None) -> int:
        """Log application usage to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO app_usage (app_name, start_time, end_time, duration_seconds)
                VALUES (?, ?, ?, ?)
            ''', (app_name, start_time, end_time, duration_seconds))
            conn.commit()
            return cursor.lastrowid
    
    def update_app_usage(self, usage_id: int, end_time: str, duration_seconds: int) -> None:
        """Update app usage record with end time and duration."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE app_usage 
                SET end_time = ?, duration_seconds = ?
                WHERE id = ?
            ''', (end_time, duration_seconds, usage_id))
            conn.commit()
    
    def get_daily_usage(self, date: str = None) -> List[Tuple]:
        """Get app usage for a specific date (default: today)."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT app_name, SUM(duration_seconds) as total_duration
                FROM app_usage 
                WHERE DATE(start_time) = ?
                AND duration_seconds IS NOT NULL
                GROUP BY app_name
                ORDER BY total_duration DESC
            ''', (date,))
            return cursor.fetchall()
    
    def get_total_screen_time(self, date: str = None) -> int:
        """Get total screen time for a date (in seconds)."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(duration_seconds)
                FROM app_usage 
                WHERE DATE(start_time) = ?
                AND duration_seconds IS NOT NULL
            ''', (date,))
            result = cursor.fetchone()
            return result[0] if result[0] else 0
    
    def get_top_apps(self, date: str = None, limit: int = 3) -> List[Tuple]:
        """Get top N apps by usage time for a date."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT app_name, SUM(duration_seconds) as total_duration
                FROM app_usage 
                WHERE DATE(start_time) = ?
                AND duration_seconds IS NOT NULL
                GROUP BY app_name
                ORDER BY total_duration DESC
                LIMIT ?
            ''', (date, limit))
            return cursor.fetchall()
    
    def save_daily_summary(self, date: str, total_screen_time: int, top_apps: str) -> None:
        """Save daily summary to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO daily_summary (date, total_screen_time, top_apps)
                VALUES (?, ?, ?)
            ''', (date, total_screen_time, top_apps))
            conn.commit()
    
    def log_reminder(self, reminder_type: str) -> None:
        """Log when a reminder was sent."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders_log (reminder_type)
                VALUES (?)
            ''', (reminder_type,))
            conn.commit()
    
    def get_active_session(self) -> Optional[Tuple]:
        """Get the current active session (latest record without end_time)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, app_name, start_time
                FROM app_usage 
                WHERE end_time IS NULL
                ORDER BY id DESC
                LIMIT 1
            ''')
            return cursor.fetchone()
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up old data beyond specified days."""
        cutoff_date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM app_usage 
                WHERE DATE(start_time) < DATE(?, '-{} days')
            '''.format(days_to_keep), (cutoff_date,))
            
            cursor.execute('''
                DELETE FROM reminders_log 
                WHERE DATE(sent_at) < DATE(?, '-{} days')
            '''.format(days_to_keep), (cutoff_date,))
            
            conn.commit()


if __name__ == "__main__":
    # Test the database
    db = DatabaseManager("../data/usage.db")
    print("Database initialized successfully!")
    
    # Test logging
    test_id = db.log_app_usage("Test App", datetime.now().isoformat())
    print(f"Test record created with ID: {test_id}")
    
    # Test updating
    db.update_app_usage(test_id, datetime.now().isoformat(), 60)
    print("Test record updated successfully!") 