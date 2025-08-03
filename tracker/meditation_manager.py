"""
Guided Meditation Manager for WorkBuddy app.
Provides various meditation sessions for stress relief and mindfulness.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager


class MeditationSession:
    """Represents a single meditation session."""
    
    def __init__(self, name: str, duration: int, session_type: str, instructions: List[str]):
        """Initialize meditation session."""
        self.name = name
        self.duration = duration  # in minutes
        self.session_type = session_type
        self.instructions = instructions
        self.current_step = 0
        self.is_active = False
        self.start_time = None
        self.step_timings = self._calculate_step_timings()
    
    def _calculate_step_timings(self) -> List[int]:
        """Calculate timing for each step in seconds."""
        total_seconds = self.duration * 60
        steps_count = len(self.instructions)
        
        if steps_count == 0:
            return []
        
        # Distribute time evenly among steps
        step_duration = total_seconds // steps_count
        return [step_duration] * steps_count
    
    def start_session(self):
        """Start the meditation session."""
        self.is_active = True
        self.current_step = 0
        self.start_time = datetime.now()
        print(f"Meditation session started at: {self.start_time}")  # Debug
    
    def get_current_instruction(self) -> str:
        """Get current step instruction."""
        if 0 <= self.current_step < len(self.instructions):
            return self.instructions[self.current_step]
        return "Session complete"
    
    def next_step(self):
        """Move to next step."""
        if self.current_step < len(self.instructions) - 1:
            self.current_step += 1
            return True
        return False
    
    def get_progress(self) -> float:
        """Get session progress (0.0 to 1.0)."""
        if not self.is_active or len(self.instructions) == 0:
            return 0.0
        return (self.current_step + 1) / len(self.instructions)
    
    def get_time_remaining(self) -> int:
        """Get remaining time in seconds."""
        if not self.is_active or not self.start_time:
            return 0
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        total_duration = self.duration * 60
        remaining = total_duration - elapsed
        return max(0, int(remaining))


class MeditationWindow:
    """GUI window for guided meditation sessions."""
    
    def __init__(self, session: MeditationSession, callback=None):
        """Initialize meditation window."""
        self.session = session
        self.callback = callback
        self.is_running = False
        self.timer_thread = None
        
        # Create window
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Setup the meditation window."""
        self.root.title(f"WorkBuddy - {self.session.name}")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 600) // 2
        y = (self.root.winfo_screenheight() - 500) // 2
        self.root.geometry(f"600x500+{x}+{y}")
        
        # Make fullscreen-like experience
        self.root.configure(bg='#1a1a2e')
        self.root.attributes('-topmost', True)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """Create meditation interface widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1a1a2e', padx=40, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Session title
        title_label = tk.Label(main_frame, text=self.session.name,
                              font=("Segoe UI", 20, "bold"),
                              bg='#1a1a2e', fg='#ffffff')
        title_label.pack(pady=(0, 20))
        
        # Session type and duration
        info_label = tk.Label(main_frame, 
                             text=f"{self.session.session_type} • {self.session.duration} minutes",
                             font=("Segoe UI", 12),
                             bg='#1a1a2e', fg='#cccccc')
        info_label.pack(pady=(0, 30))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, 
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=400,
                                           style="Meditation.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=(0, 20))
        
        # Time remaining
        self.time_label = tk.Label(main_frame, text="",
                                  font=("Segoe UI", 14),
                                  bg='#1a1a2e', fg='#ffffff')
        self.time_label.pack(pady=(0, 30))
        
        # Instruction text area
        self.instruction_text = tk.Text(main_frame, 
                                       height=8, width=60,
                                       font=("Segoe UI", 14),
                                       bg='#2d2d44', fg='#ffffff',
                                       wrap=tk.WORD, relief=tk.FLAT,
                                       state=tk.DISABLED,
                                       padx=20, pady=20)
        self.instruction_text.pack(pady=(0, 30))
        
        # Control buttons
        controls_frame = tk.Frame(main_frame, bg='#1a1a2e')
        controls_frame.pack(pady=(20, 0))
        
        self.start_btn = tk.Button(controls_frame, text="🧘‍♀️ Start Meditation",
                                  font=("Segoe UI", 12, "bold"),
                                  bg='#4a90e2', fg='white',
                                  padx=20, pady=10,
                                  relief=tk.FLAT,
                                  command=self.start_meditation)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_btn = tk.Button(controls_frame, text="⏸️ Pause",
                                  font=("Segoe UI", 12),
                                  bg='#f39c12', fg='white',
                                  padx=15, pady=10,
                                  relief=tk.FLAT,
                                  command=self.pause_meditation,
                                  state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(controls_frame, text="⏹️ Stop",
                                 font=("Segoe UI", 12),
                                 bg='#e74c3c', fg='white',
                                 padx=15, pady=10,
                                 relief=tk.FLAT,
                                 command=self.stop_meditation,
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Setup progress bar style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Meditation.Horizontal.TProgressbar",
                       background='#4a90e2',
                       troughcolor='#2d2d44',
                       borderwidth=0,
                       lightcolor='#4a90e2',
                       darkcolor='#4a90e2')
        
        # Initial display
        self.update_display()
    
    def start_meditation(self):
        """Start the meditation session."""
        self.session.start_session()
        self.is_running = True
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start timer thread
        self.timer_thread = threading.Thread(target=self._run_meditation, daemon=True)
        self.timer_thread.start()
    
    def pause_meditation(self):
        """Pause/resume meditation."""
        if self.is_running:
            self.is_running = False
            self.pause_btn.config(text="▶️ Resume")
        else:
            self.is_running = True
            self.pause_btn.config(text="⏸️ Pause")
    
    def stop_meditation(self):
        """Stop meditation session."""
        self.is_running = False
        self.session.is_active = False
        
        # Update UI
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸️ Pause")
        self.stop_btn.config(state=tk.DISABLED)
        
        # Show completion message
        self.show_instruction("Meditation session ended. Thank you for taking time for mindfulness. 🙏")
        
        if self.callback:
            self.callback(completed=False)
    
    def _run_meditation(self):
        """Run meditation timer and progression."""
        step_duration = (self.session.duration * 60) / len(self.session.instructions)
        print(f"Starting meditation: {self.session.duration} minutes, step duration: {step_duration:.1f}s")
        
        # Start a continuous timer update
        self._schedule_timer_update()
        
        for step in range(len(self.session.instructions)):
            if not self.is_running or not self.session.is_active:
                break
            
            self.session.current_step = step
            self.root.after(0, self.update_display)
            
            # Wait for step duration with pause support
            elapsed = 0
            while elapsed < step_duration and self.is_running and self.session.is_active:
                time.sleep(1)
                if self.is_running:
                    elapsed += 1
        
        # Session completed
        if self.is_running and self.session.is_active:
            self.root.after(0, self._session_completed)
    
    def _schedule_timer_update(self):
        """Schedule continuous timer updates."""
        if self.is_running and self.session.is_active:
            self.root.after(0, self.update_display)
            self.root.after(1000, self._schedule_timer_update)  # Update every second
    
    def _session_completed(self):
        """Handle session completion."""
        self.is_running = False
        self.session.is_active = False
        
        # Update UI
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸️ Pause")
        self.stop_btn.config(state=tk.DISABLED)
        
        # Show completion message
        completion_text = """🌟 Meditation Complete! 🌟

Congratulations on completing your meditation session.

You've taken an important step for your mental well-being.

Benefits you may experience:
• Reduced stress and anxiety
• Improved focus and clarity
• Enhanced emotional balance
• Better sleep quality

Consider making meditation a regular practice for lasting benefits.

Namaste 🙏"""
        
        self.show_instruction(completion_text)
        
        if self.callback:
            self.callback(completed=True)
    
    def update_display(self):
        """Update the meditation display."""
        # Update progress
        progress = self.session.get_progress() * 100
        self.progress_var.set(progress)
        
        # Update time remaining
        remaining = self.session.get_time_remaining()
        mins, secs = divmod(remaining, 60)
        self.time_label.config(text=f"Time remaining: {mins:02d}:{secs:02d}")
        
        # Update instruction
        instruction = self.session.get_current_instruction()
        self.show_instruction(instruction)
    
    def show_instruction(self, text: str):
        """Display instruction text."""
        self.instruction_text.config(state=tk.NORMAL)
        self.instruction_text.delete(1.0, tk.END)
        self.instruction_text.insert(1.0, text)
        self.instruction_text.config(state=tk.DISABLED)
    
    def on_close(self):
        """Handle window close."""
        self.stop_meditation()
        self.root.destroy()
    
    def show(self):
        """Show the meditation window."""
        self.root.mainloop()


class MeditationManager:
    """Manages meditation sessions and tracks progress."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize meditation manager."""
        self.db_manager = db_manager
        self.current_session = None
        self.available_sessions = self._load_meditation_sessions()
        self.init_meditation_tables()
    
    def init_meditation_tables(self):
        """Initialize meditation tracking tables."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Meditation sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meditation_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_name TEXT NOT NULL,
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
                
                # Daily meditation stats
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_meditation_stats (
                        date TEXT PRIMARY KEY,
                        total_meditation_time INTEGER DEFAULT 0,
                        completed_sessions INTEGER DEFAULT 0,
                        total_sessions INTEGER DEFAULT 0,
                        streak_days INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                print("✅ Meditation tracking tables initialized")
                
        except Exception as e:
            print(f"❌ Error initializing meditation tables: {e}")
    
    def _load_meditation_sessions(self) -> Dict[str, MeditationSession]:
        """Load available meditation sessions."""
        sessions = {}
        
        # Breathing meditation
        breathing_instructions = [
            "Welcome to your breathing meditation. Find a comfortable seated position.",
            "Close your eyes gently or soften your gaze downward.",
            "Begin by taking three deep breaths. Inhale slowly through your nose...",
            "...and exhale completely through your mouth. Let go of any tension.",
            "Now return to your natural breathing rhythm. Don't try to control it.",
            "Simply observe each breath as it flows in and out naturally.",
            "When your mind wanders, gently bring your attention back to your breath.",
            "Notice the sensation of air entering your nostrils...",
            "...and the feeling of your chest and belly rising and falling.",
            "If thoughts arise, acknowledge them without judgment and return to breathing.",
            "Continue focusing on this rhythm of breath for the remaining time.",
            "Your breath is your anchor to the present moment.",
            "When you're ready, slowly open your eyes and return to your day."
        ]
        
        sessions['breathing'] = MeditationSession(
            "Mindful Breathing", 10, "Breathing Meditation", breathing_instructions
        )
        
        # Body scan meditation
        body_scan_instructions = [
            "Welcome to body scan meditation. Lie down or sit comfortably.",
            "Close your eyes and take a few deep, settling breaths.",
            "Begin by noticing your body as a whole, resting and supported.",
            "Now bring attention to the top of your head. Notice any sensations.",
            "Slowly move your awareness down to your forehead, eyes, and cheeks.",
            "Continue to your jaw, neck, and shoulders. Notice any tension.",
            "If you find tension, breathe into that area and let it soften.",
            "Move your attention down your arms to your hands and fingertips.",
            "Bring awareness to your chest and heart area. Notice your breathing.",
            "Continue down to your stomach, lower back, and hips.",
            "Scan down your thighs, knees, calves, and feet.",
            "Take a moment to feel your entire body from head to toe.",
            "Wiggle your fingers and toes, then slowly open your eyes."
        ]
        
        sessions['body_scan'] = MeditationSession(
            "Body Scan Relaxation", 15, "Body Awareness", body_scan_instructions
        )
        
        # Stress relief meditation
        stress_relief_instructions = [
            "This meditation will help release stress and tension from your day.",
            "Sit comfortably and close your eyes. Take three deep breaths.",
            "With each exhale, imagine releasing stress and worry.",
            "Bring to mind any stress you're carrying from today.",
            "Don't judge these stresses, simply acknowledge them.",
            "Now imagine a warm, golden light surrounding you.",
            "This light represents peace, calm, and healing energy.",
            "As you breathe in, draw this peaceful light into your body.",
            "As you breathe out, release any stress or negative energy.",
            "Continue this visualization, breathing in peace, breathing out stress.",
            "Feel the warm light dissolving tension throughout your body.",
            "You are safe, supported, and capable of handling whatever comes.",
            "Carry this sense of peace with you as you return to your day."
        ]
        
        sessions['stress_relief'] = MeditationSession(
            "Stress Relief", 12, "Stress Management", stress_relief_instructions
        )
        
        # Quick mindfulness meditation
        mindfulness_instructions = [
            "This is a quick mindfulness check-in for busy moments.",
            "Sit comfortably and close your eyes if possible.",
            "Take three conscious breaths to center yourself.",
            "Notice five things you can hear around you right now.",
            "Notice four things you can feel (chair, clothes, temperature).",
            "Notice three things you can smell in your environment.",
            "Bring attention to two tastes you might notice in your mouth.",
            "Finally, even with eyes closed, notice what you can see (light, darkness).",
            "This is mindfulness - being fully present in this moment.",
            "You can return to this awareness anytime during your day.",
            "Take one final deep breath and slowly open your eyes."
        ]
        
        sessions['mindfulness'] = MeditationSession(
            "Quick Mindfulness", 5, "Mindfulness Practice", mindfulness_instructions
        )
        
        # Loving-kindness meditation
        loving_kindness_instructions = [
            "This meditation cultivates compassion for yourself and others.",
            "Sit comfortably and bring to mind an image of yourself.",
            "Silently repeat: 'May I be happy. May I be healthy. May I be at peace.'",
            "Feel the intention of these words, sending kindness to yourself.",
            "Now bring to mind someone you love dearly.",
            "Send them the same wishes: 'May you be happy, healthy, and at peace.'",
            "Next, think of a neutral person - someone you neither love nor dislike.",
            "Extend the same loving wishes to them with genuine intention.",
            "Now bring to mind someone with whom you have difficulty.",
            "This may be challenging, but try to wish them well too.",
            "Finally, expand to include all beings everywhere.",
            "'May all beings be happy, healthy, and live with ease.'",
            "Rest in this feeling of universal loving-kindness."
        ]
        
        sessions['loving_kindness'] = MeditationSession(
            "Loving-Kindness", 12, "Compassion Practice", loving_kindness_instructions
        )
        
        return sessions
    
    def get_available_sessions(self) -> List[str]:
        """Get list of available meditation sessions."""
        return list(self.available_sessions.keys())
    
    def start_meditation(self, session_key: str, callback=None) -> bool:
        """Start a meditation session."""
        if session_key not in self.available_sessions:
            print(f"Session '{session_key}' not found")
            return False
        
        session = self.available_sessions[session_key]
        self.current_session = session
        
        # Log session start
        self._log_session_start(session)
        
        # Create and show meditation window
        def meditation_callback(completed: bool):
            self._log_session_end(session, completed)
            if callback:
                callback(session, completed)
        
        meditation_window = MeditationWindow(session, meditation_callback)
        meditation_window.show()
        
        return True
    
    def _log_session_start(self, session: MeditationSession):
        """Log meditation session start."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO meditation_sessions 
                    (session_name, session_type, planned_duration, start_time)
                    VALUES (?, ?, ?, ?)
                ''', (session.name, session.session_type, session.duration * 60, 
                         datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            print(f"Error logging meditation start: {e}")
    
    def _log_session_end(self, session: MeditationSession, completed: bool):
        """Log meditation session completion."""
        try:
            import sqlite3
            end_time = datetime.now()
            actual_duration = 0
            
            if session.start_time:
                actual_duration = int((end_time - session.start_time).total_seconds())
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Update the latest session record
                cursor.execute('''
                    UPDATE meditation_sessions 
                    SET end_time = ?, actual_duration = ?, completed = ?
                    WHERE id = (
                        SELECT id FROM meditation_sessions 
                        WHERE session_name = ? AND session_type = ? AND end_time IS NULL
                        ORDER BY start_time DESC
                        LIMIT 1
                    )
                ''', (end_time.isoformat(), actual_duration, completed,
                     session.name, session.session_type))
                
                conn.commit()
                
            print(f"Meditation session logged: {session.name} ({'completed' if completed else 'stopped'})")
            
        except Exception as e:
            print(f"Error logging meditation end: {e}")
    
    def get_meditation_stats(self, date: str = None) -> Dict:
        """Get meditation statistics for a date."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_sessions,
                        SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_sessions,
                        SUM(CASE WHEN completed = 1 THEN actual_duration ELSE 0 END) as total_time,
                        AVG(CASE WHEN completed = 1 THEN actual_duration ELSE NULL END) as avg_duration
                    FROM meditation_sessions 
                    WHERE DATE(start_time) = ?
                ''', (date,))
                
                result = cursor.fetchone()
                
                return {
                    "date": date,
                    "total_sessions": result[0] or 0,
                    "completed_sessions": result[1] or 0,
                    "total_meditation_time": result[2] or 0,
                    "average_duration": result[3] or 0,
                    "completion_rate": (result[1] / result[0] * 100) if result[0] > 0 else 0
                }
                
        except Exception as e:
            print(f"Error getting meditation stats: {e}")
            return {"date": date, "total_sessions": 0, "completed_sessions": 0,
                   "total_meditation_time": 0, "average_duration": 0, "completion_rate": 0}
    
    def get_meditation_streak(self) -> int:
        """Get current meditation streak in days."""
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get dates with completed sessions, ordered by date descending
                cursor.execute('''
                    SELECT DISTINCT DATE(start_time) as session_date
                    FROM meditation_sessions 
                    WHERE completed = 1
                    ORDER BY session_date DESC
                ''')
                
                dates = [row[0] for row in cursor.fetchall()]
                
                if not dates:
                    return 0
                
                # Calculate streak
                streak = 0
                current_date = datetime.now().date()
                
                for date_str in dates:
                    session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    if session_date == current_date or session_date == current_date - timedelta(days=streak):
                        streak += 1
                        current_date = session_date
                    else:
                        break
                
                return streak
                
        except Exception as e:
            print(f"Error calculating meditation streak: {e}")
            return 0


if __name__ == "__main__":
    # Test meditation manager
    from db.database import DatabaseManager
    
    db = DatabaseManager("../data/usage.db")
    meditation_manager = MeditationManager(db)
    
    print("Meditation Manager initialized!")
    print(f"Available sessions: {meditation_manager.get_available_sessions()}")
    
    # Test starting a session
    def session_callback(session, completed):
        print(f"Session {session.name} {'completed' if completed else 'stopped'}")
    
    # Start a quick mindfulness session for testing
    meditation_manager.start_meditation('mindfulness', session_callback) 