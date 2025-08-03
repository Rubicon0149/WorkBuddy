"""
Scheduler module for WorkBuddy app.
Manages periodic reminders for break, hydration, and inspiration notifications.
"""

import threading
import time
import json
import os
import sys
from datetime import datetime, time as dt_time
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker.notifier import WorkBuddyNotifier
from db.database import DatabaseManager


class ReminderScheduler:
    def __init__(self, db_manager: DatabaseManager, notifier):
        """Initialize scheduler with database manager and notifier."""
        self.db_manager = db_manager
        self.notifier = notifier
        self.is_modal_notifier = hasattr(notifier, 'show_modal_notification')
        
        # Default intervals in minutes (must be defined before load_settings)
        self.default_intervals = {
            "break_interval": 45,      # 45 minutes
            "hydration_interval": 120, # 2 hours  
            "inspiration_interval": 180, # 3 hours
            "daily_summary_time": "17:00",  # 5 PM
            "work_start_time": "09:00",     # 9 AM
            "work_end_time": "18:00"        # 6 PM
        }
        
        self.settings = self.load_settings()
        self.timers = {}
        self.is_running = False
        self.start_time = None
    
    def load_settings(self) -> Dict:
        """Load settings from config/settings.json."""
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create settings file with defaults
                settings = self.default_intervals.copy()
                settings.update({
                    "notifications_enabled": True,
                    "sound_enabled": True,
                    "work_days_only": True,
                    "idle_pause_reminders": True
                })
                self.save_settings(settings)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}. Using defaults.")
            return self.default_intervals.copy()
    
    def save_settings(self, settings: Dict) -> None:
        """Save settings to config/settings.json."""
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.json')
        
        try:
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def is_work_hours(self) -> bool:
        """Check if current time is within work hours."""
        try:
            current_time = datetime.now().time()
            work_start = dt_time.fromisoformat(self.settings.get("work_start_time", "09:00"))
            work_end = dt_time.fromisoformat(self.settings.get("work_end_time", "18:00"))
            
            return work_start <= current_time <= work_end
        except Exception:
            return True  # Default to allowing reminders
    
    def is_work_day(self) -> bool:
        """Check if today is a work day (Monday-Friday)."""
        if not self.settings.get("work_days_only", True):
            return True
        
        # 0 = Monday, 6 = Sunday
        return datetime.now().weekday() < 5
    
    def should_send_reminder(self) -> bool:
        """Check if reminders should be sent based on settings."""
        if not self.settings.get("notifications_enabled", True):
            return False
        
        if not self.is_work_day():
            return False
        
        if not self.is_work_hours():
            return False
        
        return True
    
    def schedule_break_reminder(self) -> None:
        """Schedule break reminder."""
        def send_reminder():
            if self.should_send_reminder():
                if self.is_modal_notifier:
                    # Use blocking modal notification
                    def handle_break_action(action, notification_type):
                        if action == "snooze":
                            print("Break reminder snoozed for 5 minutes")
                            # Could implement snooze logic here
                        elif action == "acknowledge":
                            print("Break reminder acknowledged")
                    
                    self.notifier.show_break_reminder(action_callback=handle_break_action)
                else:
                    # Use regular notification
                    self.notifier.send_break_reminder()
            # Reschedule next reminder
            self.schedule_break_reminder()
        
        interval = self.settings.get("break_interval", 45) * 60  # Convert to seconds
        timer = threading.Timer(interval, send_reminder)
        timer.daemon = True
        timer.start()
        self.timers['break'] = timer
        
        print(f"Break reminder scheduled for {self.settings.get('break_interval', 45)} minutes")
    
    def schedule_hydration_reminder(self) -> None:
        """Schedule hydration reminder."""
        def send_reminder():
            if self.should_send_reminder():
                if self.is_modal_notifier:
                    # Use blocking modal notification
                    def handle_hydration_action(action, notification_type):
                        if action == "snooze":
                            print("Hydration reminder snoozed for 5 minutes")
                        elif action == "acknowledge":
                            print("Hydration reminder acknowledged")
                    
                    self.notifier.show_hydration_reminder(action_callback=handle_hydration_action)
                else:
                    # Use regular notification
                    self.notifier.send_hydration_reminder()
            # Reschedule next reminder
            self.schedule_hydration_reminder()
        
        interval = self.settings.get("hydration_interval", 120) * 60  # Convert to seconds
        timer = threading.Timer(interval, send_reminder)
        timer.daemon = True
        timer.start()
        self.timers['hydration'] = timer
        
        print(f"Hydration reminder scheduled for {self.settings.get('hydration_interval', 120)} minutes")
    
    def schedule_inspiration_reminder(self) -> None:
        """Schedule inspiration reminder."""
        def send_reminder():
            if self.should_send_reminder():
                self.notifier.send_inspiration_reminder()
            # Reschedule next reminder
            self.schedule_inspiration_reminder()
        
        interval = self.settings.get("inspiration_interval", 180) * 60  # Convert to seconds
        timer = threading.Timer(interval, send_reminder)
        timer.daemon = True
        timer.start()
        self.timers['inspiration'] = timer
        
        print(f"Inspiration reminder scheduled for {self.settings.get('inspiration_interval', 180)} minutes")
    
    def schedule_daily_summary(self) -> None:
        """Schedule daily summary notification."""
        def send_summary():
            try:
                # Get today's data
                today = datetime.now().strftime('%Y-%m-%d')
                total_time = self.db_manager.get_total_screen_time(today)
                top_apps = self.db_manager.get_top_apps(today, 3)
                
                # Send summary
                self.notifier.send_daily_summary(total_time, top_apps)
                
                # Save to database
                top_apps_str = ", ".join([f"{app[0]} ({app[1]}s)" for app in top_apps])
                self.db_manager.save_daily_summary(today, total_time, top_apps_str)
                
            except Exception as e:
                print(f"Error sending daily summary: {e}")
            
            # Schedule for next day
            self.schedule_daily_summary()
        
        # Calculate seconds until summary time
        now = datetime.now()
        summary_time_str = self.settings.get("daily_summary_time", "17:00")
        
        try:
            summary_time = dt_time.fromisoformat(summary_time_str)
            target_datetime = datetime.combine(now.date(), summary_time)
            
            # If time has passed today, schedule for tomorrow
            if target_datetime <= now:
                target_datetime = target_datetime.replace(day=target_datetime.day + 1)
            
            delay = (target_datetime - now).total_seconds()
            
            timer = threading.Timer(delay, send_summary)
            timer.daemon = True
            timer.start()
            self.timers['daily_summary'] = timer
            
            print(f"Daily summary scheduled for {summary_time_str}")
            
        except Exception as e:
            print(f"Error scheduling daily summary: {e}")
    
    def schedule_eye_strain_reminder(self) -> None:
        """Schedule eye strain (20-20-20) reminder every 20 minutes."""
        def send_reminder():
            if self.should_send_reminder():
                def handle_eye_action(action, notification_type):
                    if action == "snooze":
                        print("Eye strain reminder snoozed for 5 minutes")
                    elif action == "acknowledge":
                        print("Eye strain reminder acknowledged")
                
                self.notifier.show_eye_strain_reminder(action_callback=handle_eye_action)
            # Reschedule next reminder
            self.schedule_eye_strain_reminder()
        
        interval = 20 * 60  # 20 minutes in seconds
        timer = threading.Timer(interval, send_reminder)
        timer.daemon = True
        timer.start()
        self.timers['eye_strain'] = timer
        
        print("Eye strain (20-20-20) reminder scheduled for every 20 minutes")
    
    def schedule_posture_reminder(self) -> None:
        """Schedule posture check reminder every 60 minutes."""
        def send_reminder():
            if self.should_send_reminder():
                def handle_posture_action(action, notification_type):
                    if action == "snooze":
                        print("Posture reminder snoozed for 5 minutes")
                    elif action == "acknowledge":
                        print("Posture reminder acknowledged")
                
                self.notifier.show_posture_reminder(action_callback=handle_posture_action)
            # Reschedule next reminder
            self.schedule_posture_reminder()
        
        interval = 60 * 60  # 60 minutes in seconds
        timer = threading.Timer(interval, send_reminder)
        timer.daemon = True
        timer.start()
        self.timers['posture'] = timer
        
        print("Posture reminder scheduled for every 60 minutes")
    
    def schedule_mood_checkin(self) -> None:
        """Schedule mood check-in every 4 hours."""
        def send_reminder():
            if self.should_send_reminder():
                def handle_mood_action(action, notification_type):
                    if action.startswith("mood_"):
                        mood = action.replace("mood_", "")
                        print(f"Mood logged: {mood}")
                        # Could log mood to database here
                    elif action == "dismiss":
                        print("Mood check-in dismissed")
                
                self.notifier.show_mood_checkin(action_callback=handle_mood_action)
            # Reschedule next reminder
            self.schedule_mood_checkin()
        
        interval = 4 * 60 * 60  # 4 hours in seconds
        timer = threading.Timer(interval, send_reminder)
        timer.daemon = True
        timer.start()
        self.timers['mood_checkin'] = timer
        
        print("Mood check-in scheduled for every 4 hours")
    
    def start_all_reminders(self) -> None:
        """Start all reminder schedules."""
        if self.is_running:
            print("Scheduler is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        print("Starting WorkBuddy reminder scheduler...")
        
        # Schedule all reminders
        self.schedule_break_reminder()
        self.schedule_hydration_reminder() 
        self.schedule_inspiration_reminder()
        self.schedule_daily_summary()
        
        # Schedule wellness reminders if modal notifier available
        if self.is_modal_notifier:
            self.schedule_eye_strain_reminder()
            self.schedule_posture_reminder()
            self.schedule_mood_checkin()
        
        print(f"All reminders started at {self.start_time.strftime('%H:%M:%S')}")
    
    def stop_all_reminders(self) -> None:
        """Stop all reminder schedules."""
        if not self.is_running:
            print("Scheduler is not running")
            return
        
        self.is_running = False
        
        # Cancel all timers
        for timer_name, timer in self.timers.items():
            if timer and timer.is_alive():
                timer.cancel()
                print(f"Stopped {timer_name} reminder")
        
        self.timers.clear()
        print("All reminders stopped")
    
    def update_settings(self, new_settings: Dict) -> None:
        """Update scheduler settings and restart reminders."""
        self.settings.update(new_settings)
        self.save_settings(self.settings)
        
        if self.is_running:
            print("Restarting reminders with new settings...")
            self.stop_all_reminders()
            time.sleep(1)  # Give timers time to cancel
            self.start_all_reminders()
    
    def get_status(self) -> Dict:
        """Get current scheduler status."""
        active_timers = [name for name, timer in self.timers.items() 
                        if timer and timer.is_alive()]
        
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "active_timers": active_timers,
            "settings": self.settings,
            "is_work_hours": self.is_work_hours(),
            "is_work_day": self.is_work_day()
        }
    
    def send_test_reminders(self) -> None:
        """Send test reminders immediately."""
        print("Sending test reminders...")
        
        if self.should_send_reminder():
            self.notifier.send_break_reminder()
            time.sleep(2)
            self.notifier.send_hydration_reminder()
            time.sleep(2)
            self.notifier.send_inspiration_reminder()
            
            # Test daily summary with sample data
            sample_apps = [("Test App", 3600), ("Browser", 1800), ("Editor", 900)]
            self.notifier.send_daily_summary(6300, sample_apps)
        else:
            print("Reminders disabled due to settings or time constraints")


if __name__ == "__main__":
    # Test the scheduler
    from db.database import DatabaseManager
    from tracker.notifier import WorkBuddyNotifier
    
    db = DatabaseManager("../data/usage.db")
    notifier = WorkBuddyNotifier(db)
    scheduler = ReminderScheduler(db, notifier)
    
    try:
        # Test reminders
        scheduler.send_test_reminders()
        
        # Show status
        status = scheduler.get_status()
        print(f"\nScheduler Status: {status}")
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error during test: {e}")
