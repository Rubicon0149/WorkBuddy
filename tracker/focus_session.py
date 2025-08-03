"""
Focus Session module for WorkBuddy app.
Implements Pomodoro technique and focus session management.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager
from tracker.notifier import WorkBuddyNotifier


class SessionType(Enum):
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class SessionState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"


class FocusSessionManager:
    def __init__(self, db_manager: DatabaseManager, notifier):
        """Initialize focus session manager."""
        self.db_manager = db_manager
        self.notifier = notifier
        self.is_modal_notifier = hasattr(notifier, 'show_modal_notification')
        
        # Pomodoro settings (minutes)
        self.focus_duration = 25  # Standard Pomodoro
        self.short_break_duration = 5
        self.long_break_duration = 15
        self.sessions_until_long_break = 4
        
        # Current session state
        self.current_session_type = SessionType.FOCUS
        self.current_state = SessionState.STOPPED
        self.session_start_time = None
        self.session_end_time = None
        self.remaining_time = 0
        self.timer_thread = None
        self.is_running = False
        
        # Session tracking
        self.completed_focus_sessions = 0
        self.daily_focus_sessions = 0
        self.current_cycle_sessions = 0  # Sessions in current cycle (for long break)
        
        # Database setup
        self._init_focus_tables()
    
    def _init_focus_tables(self) -> None:
        """Initialize focus session tables in database."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Focus sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS focus_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_type TEXT NOT NULL,
                        planned_duration INTEGER NOT NULL,
                        actual_duration INTEGER,
                        completed BOOLEAN DEFAULT FALSE,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Daily focus stats table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_focus_stats (
                        date TEXT PRIMARY KEY,
                        total_focus_time INTEGER DEFAULT 0,
                        completed_sessions INTEGER DEFAULT 0,
                        total_sessions INTEGER DEFAULT 0,
                        average_session_length INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                print("✅ Focus session tables initialized")
                
        except Exception as e:
            print(f"❌ Error initializing focus tables: {e}")
    
    def start_focus_session(self, duration_minutes: int = None) -> bool:
        """Start a new focus session."""
        if self.current_state == SessionState.RUNNING:
            print("❌ A session is already running!")
            return False
        
        duration = duration_minutes or self.focus_duration
        self.current_session_type = SessionType.FOCUS
        self.current_state = SessionState.RUNNING
        self.session_start_time = datetime.now()
        self.session_end_time = self.session_start_time + timedelta(minutes=duration)
        self.remaining_time = duration * 60  # Convert to seconds
        self.is_running = True
        
        # Log session start
        self._log_session_start(SessionType.FOCUS, duration)
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
        
        # Send start notification
        self.notifier.show_console_notification(
            "🎯 Focus Session Started",
            f"Focus time! Working for {duration} minutes. Stay concentrated and avoid distractions."
        )
        
        self.notifier.show_toast_notification(
            "WorkBuddy - Focus Session",
            f"🎯 Focus session started: {duration} minutes\nStay focused and minimize distractions!",
            duration=8
        )
        
        print(f"🎯 Focus session started: {duration} minutes")
        return True
    
    def start_break_session(self, break_type: SessionType = None) -> bool:
        """Start a break session."""
        if self.current_state == SessionState.RUNNING:
            print("❌ End current session before starting a break!")
            return False
        
        # Determine break type
        if break_type is None:
            if self.current_cycle_sessions >= self.sessions_until_long_break:
                break_type = SessionType.LONG_BREAK
                duration = self.long_break_duration
                self.current_cycle_sessions = 0  # Reset cycle
            else:
                break_type = SessionType.SHORT_BREAK
                duration = self.short_break_duration
        else:
            duration = self.long_break_duration if break_type == SessionType.LONG_BREAK else self.short_break_duration
        
        self.current_session_type = break_type
        self.current_state = SessionState.BREAK
        self.session_start_time = datetime.now()
        self.session_end_time = self.session_start_time + timedelta(minutes=duration)
        self.remaining_time = duration * 60
        self.is_running = True
        
        # Log break start
        self._log_session_start(break_type, duration)
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
        
        # Send break notification
        break_emoji = "☕" if break_type == SessionType.SHORT_BREAK else "🌴"
        break_name = "Short Break" if break_type == SessionType.SHORT_BREAK else "Long Break"
        
        self.notifier.show_console_notification(
            f"{break_emoji} {break_name} Started",
            f"Take a {duration}-minute break! Step away from your desk, stretch, hydrate, or relax."
        )
        
        self.notifier.show_toast_notification(
            f"WorkBuddy - {break_name}",
            f"{break_emoji} Break time: {duration} minutes\nStep away from your desk and recharge!",
            duration=10
        )
        
        print(f"{break_emoji} {break_name} started: {duration} minutes")
        return True
    
    def pause_session(self) -> bool:
        """Pause the current session."""
        if self.current_state != SessionState.RUNNING:
            print("❌ No active session to pause!")
            return False
        
        self.current_state = SessionState.PAUSED
        self.is_running = False
        
        print("⏸️ Session paused")
        self.notifier.show_console_notification("⏸️ Session Paused", "Session has been paused. Use 'resume' to continue.")
        return True
    
    def resume_session(self) -> bool:
        """Resume a paused session."""
        if self.current_state != SessionState.PAUSED:
            print("❌ No paused session to resume!")
            return False
        
        self.current_state = SessionState.RUNNING
        self.is_running = True
        
        # Restart timer with remaining time
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
        
        print("▶️ Session resumed")
        self.notifier.show_console_notification("▶️ Session Resumed", "Back to work! Session continues.")
        return True
    
    def stop_session(self, completed: bool = True) -> bool:
        """Stop the current session."""
        if self.current_state == SessionState.STOPPED:
            print("❌ No active session to stop!")
            return False
        
        self.is_running = False
        self.current_state = SessionState.STOPPED
        
        # Log session end
        self._log_session_end(completed)
        
        if completed and self.current_session_type == SessionType.FOCUS:
            self.completed_focus_sessions += 1
            self.daily_focus_sessions += 1
            self.current_cycle_sessions += 1
        
        session_name = self.current_session_type.value.replace('_', ' ').title()
        status = "completed" if completed else "stopped early"
        
        print(f"🛑 {session_name} {status}")
        self.notifier.show_console_notification(
            f"🛑 Session {status.title()}",
            f"{session_name} has been {status}."
        )
        
        return True
    
    def _run_timer(self) -> None:
        """Timer thread that counts down the session."""
        while self.is_running and self.remaining_time > 0:
            time.sleep(1)
            if self.current_state == SessionState.RUNNING or self.current_state == SessionState.BREAK:
                self.remaining_time -= 1
        
        # Session completed naturally
        if self.remaining_time <= 0 and self.is_running:
            self._session_completed()
    
    def _session_completed(self) -> None:
        """Handle session completion."""
        session_type = self.current_session_type
        
        if session_type == SessionType.FOCUS:
            # Focus session completed
            self.completed_focus_sessions += 1
            self.daily_focus_sessions += 1
            self.current_cycle_sessions += 1
            
            # Show modal completion notification if available
            if self.is_modal_notifier:
                def handle_focus_completion(action, notification_type):
                    if action == "start_break":
                        self.start_break_session()
                    elif action == "continue":
                        print("Continuing work without break...")
                
                self.notifier.show_focus_complete(
                    duration_minutes=self.focus_duration,
                    action_callback=handle_focus_completion
                )
            else:
                # Fallback to regular notifications
                break_type = "long break" if self.current_cycle_sessions >= self.sessions_until_long_break else "short break"
                break_emoji = "🌴" if self.current_cycle_sessions >= self.sessions_until_long_break else "☕"
                
                self.notifier.show_console_notification(
                    "🎉 Focus Session Complete!",
                    f"Great job! You completed a {self.focus_duration}-minute focus session.\nReady for a {break_type}?"
                )
                
                if hasattr(self.notifier, 'show_toast_notification'):
                    self.notifier.show_toast_notification(
                        "WorkBuddy - Focus Complete!",
                        f"🎉 Session complete! Time for a {break_type} {break_emoji}",
                        duration=15
                    )
            
        else:
            # Break completed
            if self.is_modal_notifier:
                def handle_break_completion(action, notification_type):
                    if action == "start_focus":
                        self.start_focus_session()
                    elif action == "extend_break":
                        print("Extending break time...")
                
                break_name = "Long Break" if session_type == SessionType.LONG_BREAK else "Short Break"
                message = f"✨ {break_name} Complete!\n\nBreak time is over! Ready to start another focus session?\n\nConsistent work-break cycles improve productivity and reduce fatigue."
                
                self.notifier.show_modal_notification(
                    title=f"{break_name} Complete!",
                    message=message,
                    notification_type="break_complete",
                    action_callback=handle_break_completion
                )
            else:
                # Fallback to regular notifications
                self.notifier.show_console_notification(
                    "✨ Break Complete!",
                    f"Break time is over! Ready to start another focus session?"
                )
                
                if hasattr(self.notifier, 'show_toast_notification'):
                    self.notifier.show_toast_notification(
                        "WorkBuddy - Break Complete!",
                        "✨ Break over! Ready for another focus session? 🎯",
                        duration=10
                    )
        
        # Log completion
        self._log_session_end(completed=True)
        self.current_state = SessionState.STOPPED
        self.is_running = False
    
    def _log_session_start(self, session_type: SessionType, duration: int) -> None:
        """Log session start to database."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO focus_sessions (session_type, planned_duration, start_time)
                    VALUES (?, ?, ?)
                ''', (session_type.value, duration * 60, self.session_start_time.isoformat()))
                conn.commit()
        except Exception as e:
            print(f"Error logging session start: {e}")
    
    def _log_session_end(self, completed: bool) -> None:
        """Log session end to database."""
        try:
            if not self.session_start_time:
                return
            
            end_time = datetime.now()
            actual_duration = int((end_time - self.session_start_time).total_seconds())
            
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE focus_sessions 
                    SET end_time = ?, actual_duration = ?, completed = ?
                    WHERE start_time = ? AND session_type = ?
                ''', (end_time.isoformat(), actual_duration, completed, 
                      self.session_start_time.isoformat(), self.current_session_type.value))
                conn.commit()
        except Exception as e:
            print(f"Error logging session end: {e}")
    
    def get_status(self) -> Dict:
        """Get current focus session status."""
        remaining_minutes = self.remaining_time // 60
        remaining_seconds = self.remaining_time % 60
        
        return {
            "state": self.current_state.value,
            "session_type": self.current_session_type.value,
            "remaining_time": self.remaining_time,
            "remaining_display": f"{remaining_minutes:02d}:{remaining_seconds:02d}",
            "session_start": self.session_start_time.isoformat() if self.session_start_time else None,
            "session_end": self.session_end_time.isoformat() if self.session_end_time else None,
            "completed_today": self.daily_focus_sessions,
            "total_completed": self.completed_focus_sessions,
            "current_cycle": self.current_cycle_sessions,
            "next_break_type": "long" if self.current_cycle_sessions >= self.sessions_until_long_break else "short"
        }
    
    def get_daily_stats(self, date: str = None) -> Dict:
        """Get daily focus session statistics."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get daily session data
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_sessions,
                        SUM(CASE WHEN completed = 1 THEN actual_duration ELSE 0 END) as total_focus_time,
                        AVG(CASE WHEN completed = 1 THEN actual_duration ELSE NULL END) as avg_session_length
                    FROM focus_sessions 
                    WHERE DATE(start_time) = ? AND session_type = 'focus'
                ''', (date,))
                
                result = cursor.fetchone()
                
                return {
                    "date": date,
                    "total_sessions": result[0] or 0,
                    "completed_sessions": result[1] or 0,
                    "total_focus_time": result[2] or 0,
                    "average_session_length": result[3] or 0,
                    "completion_rate": (result[1] / result[0] * 100) if result[0] > 0 else 0
                }
                
        except Exception as e:
            print(f"Error getting daily stats: {e}")
            return {"date": date, "total_sessions": 0, "completed_sessions": 0, 
                   "total_focus_time": 0, "average_session_length": 0, "completion_rate": 0}


if __name__ == "__main__":
    # Test the focus session manager
    from db.database import DatabaseManager
    from tracker.notifier import WorkBuddyNotifier
    
    db = DatabaseManager("../data/usage.db")
    notifier = WorkBuddyNotifier(db)
    focus_manager = FocusSessionManager(db, notifier)
    
    print("Focus Session Manager initialized!")
    print("Status:", focus_manager.get_status()) 