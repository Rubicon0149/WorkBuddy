"""
Energy Level Tracking module for WorkBuddy app.
Allows users to self-report energy levels and provides analytics.
"""

import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager


class EnergyTrackingWindow:
    """Energy level self-reporting window."""
    
    def __init__(self, db_manager: DatabaseManager, callback=None):
        """Initialize energy tracking window."""
        self.db_manager = db_manager
        self.callback = callback
        self.energy_level = 5  # Default to neutral
        self.notes = ""
        self.submitted = False
        
        # Create window
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Setup the energy tracking window."""
        self.root.title("WorkBuddy - Energy Level Check")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"500x400+{x}+{y}")
        
        # Make modal
        self.root.transient()
        self.root.grab_set()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        self.root.configure(bg='#f0f0f0')
        self.root.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Ensure window is brought to front
        self.root.lift()
        self.root.after(1, lambda: self.root.focus_force())
    
    def create_widgets(self):
        """Create the energy tracking widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🔋 Energy Level Check", 
                              font=("Segoe UI", 18, "bold"),
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instruction_text = """How are you feeling right now? 
Rate your current energy level on a scale of 1-10:

1-2: Very Low Energy (exhausted, need rest)
3-4: Low Energy (tired, sluggish)
5-6: Moderate Energy (neutral, ok)
7-8: High Energy (alert, focused)
9-10: Very High Energy (energized, peak performance)"""
        
        instruction_label = tk.Label(main_frame, text=instruction_text,
                                   font=("Segoe UI", 11), justify=tk.LEFT,
                                   bg='#f0f0f0', fg='#555555')
        instruction_label.pack(pady=(0, 20))
        
        # Energy level frame
        energy_frame = ttk.Frame(main_frame)
        energy_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Energy level label
        self.energy_label = tk.Label(energy_frame, text=f"Energy Level: {self.energy_level}/10", 
                                    font=("Segoe UI", 14, "bold"),
                                    bg='#f0f0f0', fg='#333333')
        self.energy_label.pack(pady=(0, 10))
        
        # Energy level slider
        self.energy_slider = tk.Scale(energy_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                     length=400, font=("Segoe UI", 10),
                                     bg='#f0f0f0', fg='#333333',
                                     highlightthickness=0, bd=0,
                                     command=self.on_slider_change)
        self.energy_slider.set(5)
        self.energy_slider.pack()
        
        # Emoji indicators
        emoji_frame = ttk.Frame(energy_frame)
        emoji_frame.pack(fill=tk.X, pady=(5, 0))
        
        emojis = ["😴", "😔", "😐", "🙂", "😊", "⚡", "🚀", "🌟", "💪", "🔥"]
        for i, emoji in enumerate(emojis, 1):
            emoji_label = tk.Label(emoji_frame, text=emoji, font=("Segoe UI Emoji", 12),
                                 bg='#f0f0f0')
            emoji_label.pack(side=tk.LEFT, padx=15)
        
        # Notes section
        notes_label = tk.Label(main_frame, text="Optional Notes (what's affecting your energy?):",
                              font=("Segoe UI", 11, "bold"),
                              bg='#f0f0f0', fg='#333333')
        notes_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.notes_text = tk.Text(main_frame, height=4, width=50, font=("Segoe UI", 10),
                                 wrap=tk.WORD, bg='white', fg='#333333')
        self.notes_text.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Make buttons more prominent
        submit_btn = tk.Button(button_frame, text="✅ Submit Energy Level", 
                              command=self.on_submit,
                              font=("Segoe UI", 11, "bold"),
                              bg='#4CAF50', fg='white',
                              padx=20, pady=8,
                              relief=tk.FLAT)
        submit_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", 
                              command=self.on_cancel,
                              font=("Segoe UI", 11),
                              bg='#f44336', fg='white',
                              padx=20, pady=8,
                              relief=tk.FLAT)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key and make submit button default
        self.root.bind('<Return>', lambda e: self.on_submit())
        submit_btn.focus_set()  # Give focus to submit button
    
    def on_slider_change(self, value):
        """Handle slider value change."""
        self.energy_level = int(value)
        self.energy_label.config(text=f"Energy Level: {self.energy_level}/10")
        
        # Change color based on energy level
        if self.energy_level <= 2:
            color = "#ff4444"  # Red
        elif self.energy_level <= 4:
            color = "#ff8800"  # Orange
        elif self.energy_level <= 6:
            color = "#ffcc00"  # Yellow
        elif self.energy_level <= 8:
            color = "#44aa44"  # Green
        else:
            color = "#0088ff"  # Blue
        
        self.energy_label.config(fg=color)
    
    def on_submit(self):
        """Handle submit button."""
        try:
            self.notes = self.notes_text.get(1.0, tk.END).strip()
            self.submitted = True
            print(f"Energy level submitted: {self.energy_level}/10")  # Debug output
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error in submit: {e}")
    
    def on_cancel(self):
        """Handle cancel button."""
        try:
            self.submitted = False
            print("Energy check-in cancelled")  # Debug output
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error in cancel: {e}")
    
    def show(self) -> Optional[Tuple[int, str]]:
        """Show the energy tracking window and return result."""
        self.root.mainloop()
        
        if self.submitted:
            return (self.energy_level, self.notes)
        return None


class EnergyTracker:
    """Manages energy level tracking and analytics."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize energy tracker."""
        self.db_manager = db_manager
        self.init_energy_tables()
    
    def init_energy_tables(self):
        """Initialize energy tracking tables."""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Energy levels table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS energy_levels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        energy_level INTEGER NOT NULL,
                        notes TEXT,
                        timestamp TEXT NOT NULL,
                        date TEXT NOT NULL,
                        hour INTEGER NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Energy patterns table for analytics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS energy_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        avg_energy REAL,
                        peak_energy INTEGER,
                        low_energy INTEGER,
                        peak_hour INTEGER,
                        low_hour INTEGER,
                        total_entries INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                print("✅ Energy tracking tables initialized")
                
        except Exception as e:
            print(f"❌ Error initializing energy tables: {e}")
    
    def log_energy_level(self, energy_level: int, notes: str = "") -> bool:
        """Log an energy level entry."""
        try:
            now = datetime.now()
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO energy_levels (energy_level, notes, timestamp, date, hour)
                    VALUES (?, ?, ?, ?, ?)
                ''', (energy_level, notes, now.isoformat(), 
                     now.strftime('%Y-%m-%d'), now.hour))
                conn.commit()
            
            print(f"Energy level logged: {energy_level}/10")
            return True
            
        except Exception as e:
            print(f"Error logging energy level: {e}")
            return False
    
    def show_energy_checkin(self) -> Optional[Tuple[int, str]]:
        """Show energy check-in window."""
        window = EnergyTrackingWindow(self.db_manager)
        return window.show()
    
    def get_daily_energy_stats(self, date: str = None) -> Dict:
        """Get daily energy statistics."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get daily stats
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_entries,
                        AVG(energy_level) as avg_energy,
                        MAX(energy_level) as peak_energy,
                        MIN(energy_level) as low_energy
                    FROM energy_levels 
                    WHERE date = ?
                ''', (date,))
                
                result = cursor.fetchone()
                
                if result[0] == 0:  # No entries
                    return {
                        "date": date,
                        "total_entries": 0,
                        "avg_energy": 0,
                        "peak_energy": 0,
                        "low_energy": 0,
                        "peak_hour": None,
                        "low_hour": None
                    }
                
                # Get peak and low hours
                cursor.execute('''
                    SELECT hour, energy_level 
                    FROM energy_levels 
                    WHERE date = ? AND energy_level = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (date, result[2]))  # Peak energy
                peak_hour_result = cursor.fetchone()
                
                cursor.execute('''
                    SELECT hour, energy_level 
                    FROM energy_levels 
                    WHERE date = ? AND energy_level = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (date, result[3]))  # Low energy
                low_hour_result = cursor.fetchone()
                
                return {
                    "date": date,
                    "total_entries": result[0],
                    "avg_energy": round(result[1], 1) if result[1] else 0,
                    "peak_energy": result[2],
                    "low_energy": result[3],
                    "peak_hour": peak_hour_result[0] if peak_hour_result else None,
                    "low_hour": low_hour_result[0] if low_hour_result else None
                }
                
        except Exception as e:
            print(f"Error getting daily energy stats: {e}")
            return {"date": date, "total_entries": 0, "avg_energy": 0, 
                   "peak_energy": 0, "low_energy": 0, "peak_hour": None, "low_hour": None}
    
    def get_energy_trends(self, days: int = 7) -> List[Dict]:
        """Get energy trends over specified number of days."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            
            trends = []
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                stats = self.get_daily_energy_stats(date_str)
                trends.append(stats)
                current_date += timedelta(days=1)
            
            return trends
            
        except Exception as e:
            print(f"Error getting energy trends: {e}")
            return []
    
    def get_optimal_break_times(self) -> List[int]:
        """Analyze energy patterns to suggest optimal break times."""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Get average energy by hour over last 7 days
                cursor.execute('''
                    SELECT hour, AVG(energy_level) as avg_energy
                    FROM energy_levels 
                    WHERE date >= date('now', '-7 days')
                    GROUP BY hour
                    ORDER BY avg_energy ASC
                    LIMIT 3
                ''')
                
                low_energy_hours = [row[0] for row in cursor.fetchall()]
                return low_energy_hours
                
        except Exception as e:
            print(f"Error analyzing break times: {e}")
            return [14, 16, 10]  # Default low-energy hours
    
    def generate_energy_insights(self) -> List[str]:
        """Generate personalized energy insights."""
        stats = self.get_daily_energy_stats()
        trends = self.get_energy_trends(7)
        
        insights = []
        
        # Daily insights
        if stats["total_entries"] > 0:
            if stats["avg_energy"] >= 7:
                insights.append("🌟 Great energy today! You're in a high-performance zone.")
            elif stats["avg_energy"] >= 5:
                insights.append("👍 Moderate energy levels today. Consider optimizing with breaks.")
            else:
                insights.append("⚡ Low energy detected. Focus on rest, nutrition, and hydration.")
            
            # Peak/low hour insights
            if stats["peak_hour"] is not None:
                peak_time = f"{stats['peak_hour']:02d}:00"
                insights.append(f"🚀 Your peak energy was at {peak_time} - schedule important tasks then!")
            
            if stats["low_hour"] is not None:
                low_time = f"{stats['low_hour']:02d}:00"
                insights.append(f"😴 Energy dip at {low_time} - perfect time for a break or light tasks.")
        
        # Weekly trends
        if len(trends) >= 3:
            recent_avg = sum(t["avg_energy"] for t in trends[-3:] if t["avg_energy"] > 0) / 3
            older_avg = sum(t["avg_energy"] for t in trends[:3] if t["avg_energy"] > 0) / 3
            
            if recent_avg > older_avg + 0.5:
                insights.append("📈 Your energy levels are trending upward this week!")
            elif recent_avg < older_avg - 0.5:
                insights.append("📉 Energy levels declining this week. Consider adjusting your routine.")
        
        return insights if insights else ["🔋 Keep tracking your energy to get personalized insights!"]


if __name__ == "__main__":
    # Test energy tracking
    from db.database import DatabaseManager
    
    db = DatabaseManager("../data/usage.db")
    energy_tracker = EnergyTracker(db)
    
    print("Testing energy tracking...")
    
    # Test energy check-in
    result = energy_tracker.show_energy_checkin()
    if result:
        energy_level, notes = result
        energy_tracker.log_energy_level(energy_level, notes)
        print(f"Energy logged: {energy_level}/10")
        if notes:
            print(f"Notes: {notes}")
    
    # Show stats
    stats = energy_tracker.get_daily_energy_stats()
    print(f"Daily stats: {stats}")
    
    # Show insights
    insights = energy_tracker.generate_energy_insights()
    for insight in insights:
        print(f"Insight: {insight}") 