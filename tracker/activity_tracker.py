"""
Activity tracker module for WorkBuddy app.
Monitors active windows and tracks application usage on Windows.
"""

import time
import threading
from datetime import datetime
from typing import Optional, Tuple
import ctypes
from ctypes import wintypes, windll
import psutil
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager


class WindowsActivityTracker:
    def __init__(self, db_manager: DatabaseManager, poll_interval: int = 5):
        """Initialize activity tracker with database manager."""
        self.db_manager = db_manager
        self.poll_interval = poll_interval
        self.current_app = None
        self.current_session_id = None
        self.session_start_time = None
        self.is_running = False
        self.thread = None
        self.last_activity_time = time.time()
        self.idle_threshold = 300  # 5 minutes in seconds
    
    def get_active_window_info(self) -> Tuple[Optional[str], Optional[str]]:
        """Get active window title and process name using Windows API."""
        try:
            # Get foreground window handle
            hwnd = windll.user32.GetForegroundWindow()
            if hwnd == 0:
                return None, None
            
            # Get window title
            length = windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return None, None
            
            buffer = ctypes.create_unicode_buffer(length + 1)
            windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
            window_title = buffer.value
            
            # Get process ID
            process_id = wintypes.DWORD()
            windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            
            # Get process name
            try:
                process = psutil.Process(process_id.value)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
            
            return window_title, process_name
        
        except Exception as e:
            print(f"Error getting active window info: {e}")
            return None, None
    
    def get_idle_time(self) -> float:
        """Get system idle time in seconds."""
        try:
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
            
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
            windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
            
            millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
            return millis / 1000.0
        except Exception:
            return 0.0
    
    def is_system_idle(self) -> bool:
        """Check if system has been idle for longer than threshold."""
        idle_time = self.get_idle_time()
        return idle_time > self.idle_threshold
    
    def normalize_app_name(self, window_title: str, process_name: str) -> str:
        """Normalize application name for consistent logging."""
        if not window_title and not process_name:
            return "Unknown"
        
        # Use process name as base, clean up common suffixes
        app_name = process_name.replace('.exe', '') if process_name else 'Unknown'
        
        # Add window title context for better identification
        if window_title:
            # Remove common unnecessary text from window titles
            clean_title = window_title
            common_suffixes = [' - Google Chrome', ' - Mozilla Firefox', ' - Microsoft Edge', 
                             ' - Visual Studio Code', ' - Notepad++']
            
            for suffix in common_suffixes:
                if clean_title.endswith(suffix):
                    clean_title = clean_title[:-len(suffix)]
                    break
            
            # Limit title length
            if len(clean_title) > 50:
                clean_title = clean_title[:47] + "..."
            
            app_name = f"{app_name} ({clean_title})" if clean_title != app_name else app_name
        
        return app_name
    
    def start_session(self, app_name: str) -> None:
        """Start a new tracking session for an application."""
        self.current_app = app_name
        self.session_start_time = datetime.now()
        
        # Log new session start
        self.current_session_id = self.db_manager.log_app_usage(
            app_name=app_name,
            start_time=self.session_start_time.isoformat()
        )
        
        print(f"Started tracking: {app_name}")
    
    def end_session(self) -> None:
        """End current tracking session."""
        if self.current_session_id and self.session_start_time:
            end_time = datetime.now()
            duration = int((end_time - self.session_start_time).total_seconds())
            
            # Only log if duration is meaningful (at least 1 second)
            if duration >= 1:
                self.db_manager.update_app_usage(
                    usage_id=self.current_session_id,
                    end_time=end_time.isoformat(),
                    duration_seconds=duration
                )
                
                print(f"Ended tracking: {self.current_app} (Duration: {duration}s)")
        
        self.current_app = None
        self.current_session_id = None
        self.session_start_time = None
    
    def track_activity(self) -> None:
        """Main tracking loop - runs in separate thread."""
        print("Activity tracker started...")
        
        while self.is_running:
            try:
                # Check if system is idle
                if self.is_system_idle():
                    if self.current_app:
                        print("System idle detected, ending current session")
                        self.end_session()
                    time.sleep(self.poll_interval)
                    continue
                
                # Get current active window
                window_title, process_name = self.get_active_window_info()
                
                if window_title and process_name:
                    app_name = self.normalize_app_name(window_title, process_name)
                    
                    # Check if app changed
                    if app_name != self.current_app:
                        # End previous session
                        if self.current_app:
                            self.end_session()
                        
                        # Start new session
                        self.start_session(app_name)
                
                else:
                    # No active window detected, end current session
                    if self.current_app:
                        print("No active window detected, ending current session")
                        self.end_session()
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"Error in tracking loop: {e}")
                time.sleep(self.poll_interval)
    
    def start_tracking(self) -> None:
        """Start the activity tracking in a separate thread."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.track_activity, daemon=True)
            self.thread.start()
            print("Activity tracking started in background")
    
    def stop_tracking(self) -> None:
        """Stop the activity tracking."""
        if self.is_running:
            self.is_running = False
            # End current session
            if self.current_app:
                self.end_session()
            
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
            
            print("Activity tracking stopped")
    
    def get_current_status(self) -> dict:
        """Get current tracking status."""
        return {
            "is_running": self.is_running,
            "current_app": self.current_app,
            "session_start": self.session_start_time.isoformat() if self.session_start_time else None,
            "session_duration": int((datetime.now() - self.session_start_time).total_seconds()) 
                              if self.session_start_time else 0,
            "is_idle": self.is_system_idle()
        }


if __name__ == "__main__":
    # Test the activity tracker
    db = DatabaseManager("../data/usage.db")
    tracker = WindowsActivityTracker(db, poll_interval=2)
    
    try:
        tracker.start_tracking()
        print("Tracking for 30 seconds... Press Ctrl+C to stop")
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopping tracker...")
    finally:
        tracker.stop_tracking()
        print("Tracker stopped.") 