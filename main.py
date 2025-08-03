"""
WorkBuddy - Employee Mental Health Tracking App
Main application entry point that coordinates all components.
"""

import os
import sys
import time
import signal
import threading
from datetime import datetime
from typing import Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import DatabaseManager
from tracker.activity_tracker import WindowsActivityTracker
from tracker.notifier import WorkBuddyNotifier
from tracker.wellness_notifier import WellnessNotifier
from tracker.modal_notifier import ModalNotificationManager
from tracker.scheduler import ReminderScheduler
from tracker.focus_session import FocusSessionManager
from tracker.energy_tracker import EnergyTracker
from tracker.soundscape_manager import FocusSoundscapeManager
from tracker.meditation_manager import MeditationManager
from utils.time_utils import format_duration, format_time_for_display


class WorkBuddyApp:
    def __init__(self):
        """Initialize WorkBuddy application."""
        self.db_manager = None
        self.activity_tracker = None
        self.notifier = None
        self.wellness_notifier = None
        self.modal_notifier = None
        self.scheduler = None
        self.focus_manager = None
        self.energy_tracker = None
        self.soundscape_manager = None
        self.meditation_manager = None
        self.is_running = False
        self.start_time = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.shutdown()
        sys.exit(0)
    
    def initialize_components(self) -> bool:
        """Initialize all WorkBuddy components."""
        try:
            # Initialize all WorkBuddy components silently
            self.db_manager = DatabaseManager("data/usage.db")
            self.notifier = WorkBuddyNotifier(self.db_manager)
            self.wellness_notifier = WellnessNotifier(self.db_manager)
            self.modal_notifier = ModalNotificationManager(self.db_manager)
            self.activity_tracker = WindowsActivityTracker(self.db_manager, poll_interval=5)
            self.focus_manager = FocusSessionManager(self.db_manager, self.modal_notifier)
            self.energy_tracker = EnergyTracker(self.db_manager)
            self.soundscape_manager = FocusSoundscapeManager(self.db_manager)
            self.meditation_manager = MeditationManager(self.db_manager)
            self.scheduler = ReminderScheduler(self.db_manager, self.modal_notifier)
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            return False
    
    def start(self) -> None:
        """Start the WorkBuddy application."""
        if self.is_running:
            print("WorkBuddy is already running!")
            return
        
        if not self.initialize_components():
            print("Failed to initialize components. Exiting.")
            return
        
        try:
            self.is_running = True
            self.start_time = datetime.now()
            
            print("╔════════════════════════════════════════════════════════════╗")
            print("║              🎯 WorkBuddy - Wellness Dashboard              ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print(f"📅 {format_time_for_display(self.start_time)}")
            
            # Start background services silently
            self.activity_tracker.start_tracking()
            self.scheduler.start_all_reminders()
            
            print("✅ All systems ready! Background tracking and reminders active.")
            
            # Start interactive dashboard
            self._show_main_menu()
            
        except Exception as e:
            print(f"❌ Error starting WorkBuddy: {e}")
            self.shutdown()
    
    def _show_main_menu(self) -> None:
        """Show the main dashboard menu."""
        while self.is_running:
            try:
                print("\n" + "─" * 60)
                print("🏠 WORKBUDDY DASHBOARD - Choose a Feature Category")
                print("─" * 60)
                print("1️⃣  🎯 Focus & Productivity")
                print("2️⃣  📊 Tracking & Analytics") 
                print("3️⃣  🧘 Wellness & Health")
                print("4️⃣  🎧 Ambient & Soundscapes")
                print("5️⃣  🔧 System & Testing")
                print("6️⃣  ❓ Help & Documentation")
                print("7️⃣  🚪 Exit WorkBuddy")
                print("─" * 60)
                
                choice = input("Select option (1-7): ").strip()
                
                if choice == '1':
                    self._show_focus_menu()
                elif choice == '2':
                    self._show_tracking_menu()
                elif choice == '3':
                    self._show_wellness_menu()
                elif choice == '4':
                    self._show_soundscape_menu()
                elif choice == '5':
                    self._show_system_menu()
                elif choice == '6':
                    self._show_help_menu()
                elif choice == '7' or choice.lower() in ['quit', 'exit', 'q']:
                    break
                else:
                    print("❌ Invalid choice. Please select 1-7.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        self.shutdown()
    
    def _show_focus_menu(self) -> None:
        """Show focus and productivity menu."""
        while True:
            try:
                print("\n" + "─" * 50)
                print("🎯 FOCUS & PRODUCTIVITY")
                print("─" * 50)
                print("1. Start Focus Session (25 min)")
                print("2. Start Custom Focus Session")
                print("3. Start Break Session")
                print("4. Pause Current Session")
                print("5. Resume Session")
                print("6. Stop Current Session")
                print("7. View Focus Statistics")
                print("8. Session Status")
                print("0. ← Back to Main Menu")
                print("─" * 50)
                
                choice = input("Focus> ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._start_focus_session(25)
                elif choice == '2':
                    try:
                        duration = int(input("Enter duration in minutes: "))
                        self._start_focus_session(duration)
                    except ValueError:
                        print("❌ Invalid duration. Please enter a number.")
                elif choice == '3':
                    self._start_break_session()
                elif choice == '4':
                    self._pause_session()
                elif choice == '5':
                    self._resume_session()
                elif choice == '6':
                    self._stop_session()
                elif choice == '7':
                    self._show_focus_stats()
                elif choice == '8':
                    self._show_status()
                else:
                    print("❌ Invalid choice. Please select 0-8.")
                    
            except KeyboardInterrupt:
                break
    
    def _show_tracking_menu(self) -> None:
        """Show tracking and analytics menu."""
        while True:
            try:
                print("\n" + "─" * 50)
                print("📊 TRACKING & ANALYTICS")
                print("─" * 50)
                print("1. Current Status Overview")
                print("2. Today's Usage Summary")
                print("3. App Usage Details")
                print("4. Focus Session Analytics")
                print("5. Energy Level Stats")
                print("6. Meditation Progress")
                print("0. ← Back to Main Menu")
                print("─" * 50)
                
                choice = input("Tracking> ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._show_status()
                elif choice == '2':
                    self._show_summary()
                elif choice == '3':
                    self._show_detailed_usage()
                elif choice == '4':
                    self._show_focus_stats()
                elif choice == '5':
                    self._show_energy_stats()
                elif choice == '6':
                    self._show_meditation_stats()
                else:
                    print("❌ Invalid choice. Please select 0-6.")
                    
            except KeyboardInterrupt:
                break
    
    def _show_wellness_menu(self) -> None:
        """Show wellness and health menu."""
        while True:
            try:
                print("\n" + "─" * 50)
                print("🧘 WELLNESS & HEALTH")
                print("─" * 50)
                print("1. Energy Level Check-in")
                print("2. Quick Mindfulness (5 min)")
                print("3. Breathing Exercise (10 min)")
                print("4. Body Scan Meditation (15 min)")
                print("5. Stress Relief Session (12 min)")
                print("6. Loving-Kindness Practice (12 min)")
                print("7. View Wellness Statistics")
                print("8. Test Wellness Reminders")
                print("0. ← Back to Main Menu")
                print("─" * 50)
                
                choice = input("Wellness> ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._energy_checkin()
                elif choice == '2':
                    self._start_meditation('mindfulness')
                elif choice == '3':
                    self._start_meditation('breathing')
                elif choice == '4':
                    self._start_meditation('body_scan')
                elif choice == '5':
                    self._start_meditation('stress_relief')
                elif choice == '6':
                    self._start_meditation('loving_kindness')
                elif choice == '7':
                    self._show_wellness_stats()
                elif choice == '8':
                    self._test_wellness_notifications()
                else:
                    print("❌ Invalid choice. Please select 0-8.")
                    
            except KeyboardInterrupt:
                break
    
    def _show_soundscape_menu(self) -> None:
        """Show ambient soundscape menu."""
        while True:
            try:
                print("\n" + "─" * 50)
                print("🎧 AMBIENT SOUNDSCAPES")
                print("─" * 50)
                print("1. Open Soundscape Control Panel")
                print("2. Quick Play - Rain Sounds")
                print("3. Quick Play - Ocean Waves") 
                print("4. Quick Play - Forest Ambiance")
                print("5. Quick Play - White Noise")
                print("6. Quick Play - Coffee Shop")
                print("7. Stop All Sounds")
                print("0. ← Back to Main Menu")
                print("─" * 50)
                
                choice = input("Sounds> ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._show_soundscape_control()
                elif choice == '2':
                    self._quick_play_sound('rain')
                elif choice == '3':
                    self._quick_play_sound('ocean')
                elif choice == '4':
                    self._quick_play_sound('forest')
                elif choice == '5':
                    self._quick_play_sound('white_noise')
                elif choice == '6':
                    self._quick_play_sound('coffee_shop')
                elif choice == '7':
                    if self.soundscape_manager:
                        self.soundscape_manager.stop_soundscape()
                        print("🔇 All sounds stopped.")
                else:
                    print("❌ Invalid choice. Please select 0-7.")
                    
            except KeyboardInterrupt:
                break
    
    def _show_system_menu(self) -> None:
        """Show system and testing menu."""
        while True:
            try:
                print("\n" + "─" * 50)
                print("🔧 SYSTEM & TESTING")
                print("─" * 50)
                print("1. Test Basic Notifications")
                print("2. Test Modal Notifications")
                print("3. Test Wellness Reminders")
                print("4. System Information")
                print("5. Database Statistics")
                print("0. ← Back to Main Menu")
                print("─" * 50)
                
                choice = input("System> ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._test_notifications()
                elif choice == '2':
                    self._test_modal_notifications()
                elif choice == '3':
                    self._test_wellness_notifications()
                elif choice == '4':
                    self._show_system_info()
                elif choice == '5':
                    self._show_database_stats()
                else:
                    print("❌ Invalid choice. Please select 0-5.")
                    
            except KeyboardInterrupt:
                break
    
    def _show_help_menu(self) -> None:
        """Show help and documentation menu."""
        while True:
            try:
                print("\n" + "─" * 50)
                print("❓ HELP & DOCUMENTATION")
                print("─" * 50)
                print("1. Quick Start Guide")
                print("2. Feature Overview")
                print("3. Troubleshooting")
                print("4. About WorkBuddy")
                print("5. View Features File")
                print("0. ← Back to Main Menu")
                print("─" * 50)
                
                choice = input("Help> ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._show_quick_start()
                elif choice == '2':
                    self._show_feature_overview()
                elif choice == '3':
                    self._show_troubleshooting()
                elif choice == '4':
                    self._show_about()
                elif choice == '5':
                    self._view_features_file()
                else:
                    print("❌ Invalid choice. Please select 0-5.")
                    
            except KeyboardInterrupt:
                break
    
    def _show_status(self) -> None:
        """Show current application status."""
        print("\n📊 WorkBuddy Status:")
        print("-" * 40)
        
        if self.start_time:
            uptime = datetime.now() - self.start_time
            print(f"Uptime: {format_duration(int(uptime.total_seconds()))}")
        
        # Activity tracker status
        if self.activity_tracker:
            status = self.activity_tracker.get_current_status()
            print(f"Tracking: {'🟢 Active' if status['is_running'] else '🔴 Stopped'}")
            if status['current_app']:
                duration = status['session_duration']
                print(f"Current app: {status['current_app']}")
                print(f"Session time: {format_duration(duration)}")
            print(f"System idle: {'Yes' if status['is_idle'] else 'No'}")
        
        # Scheduler status
        if self.scheduler:
            status = self.scheduler.get_status()
            print(f"Reminders: {'🟢 Active' if status['is_running'] else '🔴 Stopped'}")
            print(f"Active timers: {', '.join(status['active_timers'])}")
            print(f"Work hours: {'Yes' if status['is_work_hours'] else 'No'}")
            print(f"Work day: {'Yes' if status['is_work_day'] else 'No'}")
        
        # Focus session status
        if self.focus_manager:
            focus_status = self.focus_manager.get_status()
            print(f"Focus session: {'🎯 ' + focus_status['state'].title() if focus_status['state'] != 'stopped' else '⭕ Stopped'}")
            if focus_status['state'] != 'stopped':
                print(f"Session type: {focus_status['session_type'].replace('_', ' ').title()}")
                print(f"Time remaining: {focus_status['remaining_display']}")
            print(f"Completed today: {focus_status['completed_today']} sessions")
    
    def _show_summary(self) -> None:
        """Show today's usage summary."""
        print("\n📈 Today's Summary:")
        print("-" * 40)
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            total_time = self.db_manager.get_total_screen_time(today)
            top_apps = self.db_manager.get_top_apps(today, 5)
            
            print(f"Total screen time: {format_duration(total_time)}")
            print(f"Date: {today}")
            
            if top_apps:
                print("\nTop applications:")
                for i, (app_name, duration) in enumerate(top_apps, 1):
                    print(f"  {i}. {app_name}: {format_duration(duration)}")
            else:
                print("\nNo usage data recorded today.")
                
        except Exception as e:
            print(f"Error getting summary: {e}")
    
    def _test_notifications(self) -> None:
        """Test all notification types."""
        print("\n🧪 Testing basic notifications...")
        if self.notifier:
            self.notifier.test_notifications()
        else:
            print("Notifier not initialized!")
    
    def _test_wellness_notifications(self) -> None:
        """Test all wellness notification types."""
        print("\n🌟 Testing wellness notifications...")
        if self.wellness_notifier:
            self.wellness_notifier.test_wellness_notifications()
        else:
            print("Wellness notifier not initialized!")
    
    def _test_modal_notifications(self) -> None:
        """Test modal blocking notifications."""
        print("\n🖥️ Testing modal notifications...")
        if self.modal_notifier:
            def test_callback(action, notification_type):
                print(f"Modal action: {action} for {notification_type}")
            
            print("Testing break reminder modal...")
            result = self.modal_notifier.show_break_reminder(test_callback)
            print(f"Result: {result}")
            
            print("Testing eye strain reminder modal...")
            result = self.modal_notifier.show_eye_strain_reminder(test_callback)
            print(f"Result: {result}")
            
            print("Testing posture reminder modal...")
            result = self.modal_notifier.show_posture_reminder(test_callback)
            print(f"Result: {result}")
            
        else:
            print("Modal notifier not initialized!")
    
    def _energy_checkin(self) -> None:
        """Show energy level check-in."""
        if self.energy_tracker:
            result = self.energy_tracker.show_energy_checkin()
            if result:
                energy_level, notes = result
                self.energy_tracker.log_energy_level(energy_level, notes)
                print(f"✅ Energy level logged: {energy_level}/10")
                if notes:
                    print(f"Notes: {notes}")
            else:
                print("Energy check-in cancelled.")
        else:
            print("Energy tracker not initialized!")
    
    def _show_energy_stats(self) -> None:
        """Show energy level statistics."""
        if not self.energy_tracker:
            print("Energy tracker not initialized!")
            return
        
        stats = self.energy_tracker.get_daily_energy_stats()
        insights = self.energy_tracker.generate_energy_insights()
        
        print("\n🔋 Energy Level Statistics:")
        print("-" * 40)
        print(f"Date: {stats['date']}")
        print(f"Check-ins today: {stats['total_entries']}")
        
        if stats['total_entries'] > 0:
            print(f"Average energy: {stats['avg_energy']}/10")
            print(f"Peak energy: {stats['peak_energy']}/10")
            print(f"Lowest energy: {stats['low_energy']}/10")
            
            if stats['peak_hour'] is not None:
                print(f"Peak energy time: {stats['peak_hour']:02d}:00")
            if stats['low_hour'] is not None:
                print(f"Low energy time: {stats['low_hour']:02d}:00")
        else:
            print("No energy data recorded today.")
        
        print("\n💡 Insights:")
        for insight in insights:
            print(f"  • {insight}")
    
    def _show_soundscape_control(self) -> None:
        """Show soundscape control window."""
        if self.soundscape_manager:
            self.soundscape_manager.show_control_window()
            print("🎧 Soundscape control window opened.")
        else:
            print("Soundscape manager not initialized!")
    
    def _start_meditation(self, session_type: str = 'mindfulness') -> None:
        """Start a meditation session."""
        if not self.meditation_manager:
            print("Meditation manager not initialized!")
            return
        
        available_sessions = self.meditation_manager.get_available_sessions()
        
        if session_type not in available_sessions:
            print(f"Unknown meditation type: {session_type}")
            print(f"Available sessions: {', '.join(available_sessions)}")
            return
        
        def meditation_callback(session, completed):
            if completed:
                print(f"🧘‍♀️ Meditation '{session.name}' completed successfully!")
            else:
                print(f"🧘‍♀️ Meditation '{session.name}' ended early.")
        
        success = self.meditation_manager.start_meditation(session_type, meditation_callback)
        if success:
            print(f"🧘‍♀️ Starting {session_type} meditation...")
        else:
            print(f"Failed to start {session_type} meditation.")
    
    def _show_meditation_stats(self) -> None:
        """Show meditation statistics."""
        if not self.meditation_manager:
            print("Meditation manager not initialized!")
            return
        
        stats = self.meditation_manager.get_meditation_stats()
        streak = self.meditation_manager.get_meditation_streak()
        
        print("\n🧘‍♀️ Meditation Statistics:")
        print("-" * 40)
        print(f"Date: {stats['date']}")
        print(f"Sessions today: {stats['total_sessions']}")
        print(f"Completed: {stats['completed_sessions']}")
        print(f"Completion rate: {stats['completion_rate']:.1f}%")
        
        if stats['total_meditation_time'] > 0:
            total_time = format_duration(stats['total_meditation_time'])
            avg_time = format_duration(int(stats['average_duration'])) if stats['average_duration'] else "0 seconds"
            print(f"Total meditation time: {total_time}")
            print(f"Average session: {avg_time}")
        else:
            print("No meditation sessions completed today.")
        
        print(f"Current streak: {streak} days")
        
        if streak >= 7:
            print("🌟 Amazing! You have a 7+ day meditation streak!")
        elif streak >= 3:
            print("👍 Great job maintaining a meditation practice!")
        elif streak >= 1:
            print("🌱 Good start! Keep building your meditation habit.")
    
    def _start_focus_session(self, duration: int = None) -> None:
        """Start a focus session."""
        if self.focus_manager:
            if self.focus_manager.start_focus_session(duration):
                print(f"🎯 Focus session started! Use 'status' to check progress.")
        else:
            print("Focus manager not initialized!")
    
    def _start_break_session(self) -> None:
        """Start a break session."""
        if self.focus_manager:
            if self.focus_manager.start_break_session():
                print("☕ Break session started! Enjoy your rest.")
        else:
            print("Focus manager not initialized!")
    
    def _pause_session(self) -> None:
        """Pause current session."""
        if self.focus_manager:
            if self.focus_manager.pause_session():
                print("⏸️ Session paused. Use 'resume' to continue.")
        else:
            print("Focus manager not initialized!")
    
    def _resume_session(self) -> None:
        """Resume paused session."""
        if self.focus_manager:
            if self.focus_manager.resume_session():
                print("▶️ Session resumed. Back to work!")
        else:
            print("Focus manager not initialized!")
    
    def _stop_session(self) -> None:
        """Stop current session."""
        if self.focus_manager:
            if self.focus_manager.stop_session(completed=False):
                print("🛑 Session stopped.")
        else:
            print("Focus manager not initialized!")
    
    def _show_focus_stats(self) -> None:
        """Show focus session statistics."""
        if not self.focus_manager:
            print("Focus manager not initialized!")
            return
        
        stats = self.focus_manager.get_daily_stats()
        
        print("\n🎯 Focus Session Statistics:")
        print("-" * 40)
        print(f"Date: {stats['date']}")
        print(f"Total sessions: {stats['total_sessions']}")
        print(f"Completed: {stats['completed_sessions']}")
        print(f"Completion rate: {stats['completion_rate']:.1f}%")
        
        if stats['total_focus_time'] > 0:
            total_time = format_duration(stats['total_focus_time'])
            avg_time = format_duration(int(stats['average_session_length'])) if stats['average_session_length'] else "0 seconds"
            print(f"Total focus time: {total_time}")
            print(f"Average session: {avg_time}")
        else:
            print("No completed focus sessions today.")
        
        # Show current session status
        current_status = self.focus_manager.get_status()
        if current_status['state'] != 'stopped':
            print(f"\nCurrent session: {current_status['session_type'].replace('_', ' ').title()}")
            print(f"Time remaining: {current_status['remaining_display']}")
            print(f"Status: {current_status['state'].title()}")
    
    def _show_help(self) -> None:
        """Show help information."""
        print("\n📚 WorkBuddy Commands:")
        print("-" * 50)
        print("📊 General:")
        print("  status         - Show current status and statistics")
        print("  summary        - Show today's app usage summary")
        print("  help           - Show this help message")
        print("  quit/exit      - Stop WorkBuddy and exit")
        
        print("\n🎯 Focus Sessions (Pomodoro):")
        print("  focus [min]    - Start focus session (default: 25 min)")
        print("  break          - Start break session (auto-detects short/long)")
        print("  pause          - Pause current session")
        print("  resume         - Resume paused session")
        print("  stop           - Stop current session")
        print("  focus-stats    - Show focus session statistics")
        
        print("\n🔋 Energy & Wellness:")
        print("  energy         - Check-in with current energy level")
        print("  energy-stats   - Show energy trends and insights")
        print("  sounds         - Open focus soundscape control")
        print("  meditate [type] - Start meditation (mindfulness, breathing, body_scan, stress_relief, loving_kindness)")
        print("  meditation-stats - Show meditation progress and streak")
        
        print("\n🧪 Testing:")
        print("  test           - Test basic notifications")
        print("  wellness-test  - Test wellness reminders")
        print("  modal-test     - Test modal blocking notifications")
        
        print("\n💡 WorkBuddy Features:")
        print("• Automatic app usage tracking")
        print("• Smart reminders during work hours")
        print("• Pomodoro focus sessions with break management")
        print("• Eye strain prevention (20-20-20 rule)")
        print("• Posture and ergonomic reminders")
        print("• Micro-exercise breaks")
        print("• Mood and wellness check-ins")
        print("• Healthy nutrition suggestions")
    
    # Helper methods for menu functionality
    def _quick_play_sound(self, sound_key: str) -> None:
        """Quick play a specific sound."""
        if self.soundscape_manager:
            success = self.soundscape_manager.play_soundscape(sound_key)
            if success:
                print(f"🎵 Playing {sound_key.replace('_', ' ').title()}")
            else:
                print(f"❌ Failed to play {sound_key}")
        else:
            print("❌ Soundscape manager not available")
    
    def _show_detailed_usage(self) -> None:
        """Show detailed app usage information."""
        self._show_summary()  # For now, use the existing summary
    
    def _show_wellness_stats(self) -> None:
        """Show combined wellness statistics."""
        print("\n📊 Wellness Overview:")
        print("=" * 40)
        
        # Energy stats
        if self.energy_tracker:
            energy_stats = self.energy_tracker.get_daily_energy_stats()
            print(f"Energy Check-ins: {energy_stats['total_entries']}")
            if energy_stats['total_entries'] > 0:
                print(f"Average Energy: {energy_stats['avg_energy']}/10")
        
        # Meditation stats
        if self.meditation_manager:
            meditation_stats = self.meditation_manager.get_meditation_stats()
            streak = self.meditation_manager.get_meditation_streak()
            print(f"Meditation Sessions: {meditation_stats['completed_sessions']}")
            print(f"Meditation Streak: {streak} days")
        
        print()
    
    def _show_system_info(self) -> None:
        """Show system information."""
        import platform
        import sys
        
        print("\n🖥️ System Information:")
        print("=" * 40)
        print(f"OS: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Architecture: {platform.machine()}")
        print(f"WorkBuddy Version: 1.0.0")
        print(f"Database: {self.db_manager.db_path}")
        print()
    
    def _show_database_stats(self) -> None:
        """Show database statistics."""
        try:
            import sqlite3
            import os
            
            print("\n🗄️ Database Statistics:")
            print("=" * 40)
            
            if os.path.exists(self.db_manager.db_path):
                size = os.path.getsize(self.db_manager.db_path)
                print(f"Database Size: {size:,} bytes ({size/1024:.1f} KB)")
                
                with sqlite3.connect(self.db_manager.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get table info
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"{table_name}: {count:,} records")
            else:
                print("Database not found")
            print()
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
    
    def _show_quick_start(self) -> None:
        """Show quick start guide."""
        print("\n🚀 WorkBuddy Quick Start Guide:")
        print("=" * 50)
        print("1. 🎯 Start your first focus session: Dashboard 1 → 1")
        print("2. 🧘 Try a quick meditation: Dashboard 3 → 2")
        print("3. 🔋 Check your energy level: Dashboard 3 → 1") 
        print("4. 🎧 Play ambient sounds: Dashboard 4 → 2")
        print("5. 📊 View your progress: Dashboard 2 → 1")
        print("\n💡 Tips:")
        print("• Use 0 to go back to previous menu")
        print("• All data is stored locally and private")
        print("• Break reminders help maintain wellness")
        print("• Try different meditation types for variety")
        input("\nPress Enter to continue...")
    
    def _show_feature_overview(self) -> None:
        """Show feature overview."""
        print("\n✨ WorkBuddy Features Overview:")
        print("=" * 50)
        print("🎯 FOCUS: Pomodoro sessions with smart break suggestions")
        print("📊 TRACKING: Automatic app usage and productivity analytics")
        print("🧘 WELLNESS: 5 guided meditations + energy tracking")
        print("🎧 SOUNDS: 8 ambient soundscapes with timers")
        print("🔔 REMINDERS: Smart wellness alerts (work hours only)")
        print("📱 INTERFACE: Clean multi-level menu system")
        print("🔒 PRIVACY: All data stored locally, no cloud/tracking")
        print("\n🎪 New in v1.0:")
        print("• Modal blocking notifications")
        print("• Advanced energy insights")
        print("• Meditation streak tracking")
        print("• Enhanced soundscape controls")
        input("\nPress Enter to continue...")
    
    def _show_troubleshooting(self) -> None:
        """Show troubleshooting guide."""
        print("\n🔧 Troubleshooting Guide:")
        print("=" * 40)
        print("❓ COMMON ISSUES:")
        print("• Timer not showing: Check if session is actually running")
        print("• Sounds not playing: Ensure pygame is installed")
        print("• Notifications not working: Check Windows notification settings")
        print("• Energy tracker not saving: Click Submit button and wait")
        print("• Database errors: Try restarting WorkBuddy")
        print("\n🩺 PERFORMANCE:")
        print("• High CPU: Normal during active tracking")
        print("• Memory usage: Restart if over 100MB")
        print("• Audio issues: Close other audio applications")
        print("\n🆘 EMERGENCY FIXES:")
        print("• Force quit: Ctrl+C in terminal")
        print("• Reset data: Delete data/usage.db file")
        print("• Reinstall: Delete workbuddy folder and re-run setup")
        input("\nPress Enter to continue...")
    
    def _show_about(self) -> None:
        """Show about information."""
        print("\n🎯 About WorkBuddy:")
        print("=" * 40)
        print("Version: 1.0.0")
        print("Platform: Windows")
        print("License: MIT")
        print("\n🎨 Designed for:")
        print("• Remote workers")
        print("• Students")
        print("• Developers")
        print("• Anyone seeking work-life balance")
        print("\n💝 Features:")
        print("• 20+ wellness & productivity tools")
        print("• Modal blocking reminders")
        print("• Privacy-first design")
        print("• Comprehensive analytics")
        print("\n🙏 Acknowledgments:")
        print("Built with Python, SQLite, tkinter, pygame")
        print("Meditation content inspired by mindfulness practices")
        print("Sound generation using numpy and wave libraries")
        input("\nPress Enter to continue...")
    
    def _view_features_file(self) -> None:
        """View the features file."""
        import os
        features_path = "FEATURES.md"
        
        if os.path.exists(features_path):
            print(f"\n📄 Opening {features_path}...")
            print("Check the file in your current directory for complete documentation.")
            print("This file contains detailed workflow examples and technical specifications.")
        else:
            print("\n❌ FEATURES.md file not found in current directory.")
            print("The file should contain comprehensive documentation about all WorkBuddy features.")
        
        input("\nPress Enter to continue...")
    
    def shutdown(self) -> None:
        """Shutdown WorkBuddy application gracefully."""
        if not self.is_running:
            return
        
        print("\n🛑 Shutting down WorkBuddy...")
        self.is_running = False
        
        try:
            # Stop activity tracking
            if self.activity_tracker:
                self.activity_tracker.stop_tracking()
                print("✅ Activity tracker stopped")
            
            # Stop reminders
            if self.scheduler:
                self.scheduler.stop_all_reminders()
                print("✅ Reminder scheduler stopped")
            
            # Stop focus sessions
            if self.focus_manager:
                self.focus_manager.stop_session(completed=False)
                print("✅ Focus session manager stopped")
            
            # Clean up old data (keep last 30 days)
            if self.db_manager:
                self.db_manager.cleanup_old_data(30)
                print("✅ Database cleanup completed")
            
            if self.start_time:
                uptime = datetime.now() - self.start_time
                print(f"📊 Session duration: {format_duration(int(uptime.total_seconds()))}")
            
            print("👋 WorkBuddy stopped. Thanks for using our wellness tracker!")
            
        except Exception as e:
            print(f"❌ Error during shutdown: {e}")


def main():
    """Main entry point for WorkBuddy application."""
    print("🎯 WorkBuddy - Employee Mental Health Tracking App")
    print("Version 1.0.0 - Windows Edition")
    print("="*60)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ Error: WorkBuddy is designed for Windows only.")
        print("Windows APIs are required for app tracking functionality.")
        sys.exit(1)
    
    try:
        app = WorkBuddyApp()
        app.start()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 