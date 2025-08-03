"""
Modal Notification system for WorkBuddy app.
Creates blocking, modal notifications that cover the screen until dismissed.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Callable
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False

from db.database import DatabaseManager


class ModalNotificationWindow:
    """Modal notification window that blocks all interactions until dismissed."""
    
    def __init__(self, title: str, message: str, notification_type: str = "info", 
                 auto_dismiss_seconds: int = None, action_callback: Callable = None):
        """Initialize modal notification window."""
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.auto_dismiss_seconds = auto_dismiss_seconds
        self.action_callback = action_callback
        self.dismissed = False
        self.user_response = None
        
        # Create root window
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        
        # Auto-dismiss timer
        if auto_dismiss_seconds:
            self.root.after(auto_dismiss_seconds * 1000, self.auto_dismiss)
    
    def setup_window(self):
        """Setup the modal window properties."""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Window size (responsive to screen size)
        window_width = min(600, int(screen_width * 0.4))
        window_height = min(400, int(screen_height * 0.3))
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Configure window
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.title("WorkBuddy Reminder")
        self.root.resizable(False, False)
        
        # Make it modal and always on top
        self.root.transient()  # Modal to parent
        self.root.grab_set()   # Grab all events
        self.root.attributes('-topmost', True)  # Always on top
        self.root.focus_force()  # Force focus
        
        # Prevent closing with X button unless specifically allowed
        self.root.protocol("WM_DELETE_WINDOW", self.on_dismiss)
        
        # Style configuration
        self.root.configure(bg='#f0f0f0')
        
        # Set icon if available
        try:
            # You can add an icon file here
            # self.root.iconbitmap('assets/workbuddy_icon.ico')
            pass
        except:
            pass
    
    def create_widgets(self):
        """Create the notification widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Emoji and title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Get emoji based on notification type
        emoji_map = {
            "break": "💻",
            "hydration": "💧", 
            "inspiration": "✨",
            "eye_strain": "👁️",
            "posture": "🦴",
            "micro_exercise": "🏃",
            "nutrition": "🍎",
            "mood": "💚",
            "focus_start": "🎯",
            "focus_complete": "🎉",
            "break_complete": "✨",
            "ambient": "🌡️",
            "daily_summary": "📊",
            "info": "ℹ️",
            "warning": "⚠️",
            "success": "✅"
        }
        
        emoji = emoji_map.get(self.notification_type, "📢")
        
        # Large emoji
        emoji_label = tk.Label(title_frame, text=emoji, font=("Segoe UI Emoji", 48), 
                              bg='#f0f0f0', fg='#333333')
        emoji_label.pack(side=tk.TOP, pady=(0, 10))
        
        # Title
        title_label = tk.Label(title_frame, text=self.title, 
                              font=("Segoe UI", 16, "bold"),
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(side=tk.TOP)
        
        # Message frame with scrollable text
        message_frame = ttk.Frame(main_frame)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Message text with scrollbar
        text_widget = tk.Text(message_frame, wrap=tk.WORD, font=("Segoe UI", 11),
                             bg='white', fg='#333333', relief=tk.FLAT,
                             padx=15, pady=15, height=8)
        scrollbar = ttk.Scrollbar(message_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert message
        text_widget.insert(tk.END, self.message)
        text_widget.configure(state=tk.DISABLED)  # Make read-only
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create appropriate buttons based on notification type
        self.create_action_buttons(button_frame)
        
        # Auto-dismiss countdown if applicable
        if self.auto_dismiss_seconds:
            self.countdown_label = tk.Label(button_frame, 
                                          text=f"Auto-closing in {self.auto_dismiss_seconds}s",
                                          font=("Segoe UI", 9), bg='#f0f0f0', fg='#666666')
            self.countdown_label.pack(side=tk.BOTTOM, pady=(10, 0))
            self.start_countdown()
    
    def create_action_buttons(self, parent_frame):
        """Create action buttons based on notification type."""
        if self.notification_type in ["focus_complete", "break_complete"]:
            # Focus/break completion - offer next action
            if self.notification_type == "focus_complete":
                ttk.Button(parent_frame, text="Start Break", 
                          command=lambda: self.on_action("start_break")).pack(side=tk.LEFT, padx=(0, 10))
                ttk.Button(parent_frame, text="Continue Working", 
                          command=lambda: self.on_action("continue")).pack(side=tk.LEFT, padx=(0, 10))
            else:  # break_complete
                ttk.Button(parent_frame, text="Start Focus Session", 
                          command=lambda: self.on_action("start_focus")).pack(side=tk.LEFT, padx=(0, 10))
                ttk.Button(parent_frame, text="Take More Time", 
                          command=lambda: self.on_action("extend_break")).pack(side=tk.LEFT, padx=(0, 10))
        
        elif self.notification_type in ["break", "hydration", "eye_strain", "posture", "micro_exercise"]:
            # Health reminders - acknowledge or snooze
            ttk.Button(parent_frame, text="Done! ✓", 
                      command=lambda: self.on_action("acknowledge")).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(parent_frame, text="Snooze 5 min", 
                      command=lambda: self.on_action("snooze")).pack(side=tk.LEFT, padx=(0, 10))
        
        elif self.notification_type == "mood":
            # Mood check-in - quick mood buttons
            mood_frame = ttk.Frame(parent_frame)
            mood_frame.pack(fill=tk.X, pady=(0, 10))
            
            moods = [("😊", "Great"), ("😐", "Okay"), ("😔", "Not Great"), ("😴", "Tired")]
            for emoji, mood in moods:
                ttk.Button(mood_frame, text=f"{emoji} {mood}", 
                          command=lambda m=mood: self.on_action(f"mood_{m.lower()}")).pack(side=tk.LEFT, padx=2)
        
        # Always include dismiss button
        dismiss_btn = ttk.Button(parent_frame, text="Dismiss", command=self.on_dismiss)
        dismiss_btn.pack(side=tk.RIGHT)
        
        # Make dismiss button default
        dismiss_btn.focus_set()
        self.root.bind('<Return>', lambda e: self.on_dismiss())
        self.root.bind('<Escape>', lambda e: self.on_dismiss())
    
    def start_countdown(self):
        """Start countdown timer for auto-dismiss."""
        if hasattr(self, 'countdown_label') and self.auto_dismiss_seconds > 0:
            self.countdown_label.config(text=f"Auto-closing in {self.auto_dismiss_seconds}s")
            self.auto_dismiss_seconds -= 1
            self.root.after(1000, self.start_countdown)
    
    def auto_dismiss(self):
        """Auto-dismiss the notification."""
        if not self.dismissed:
            self.on_action("auto_dismiss")
    
    def on_action(self, action: str):
        """Handle action button clicks."""
        self.user_response = action
        if self.action_callback:
            self.action_callback(action, self.notification_type)
        self.on_dismiss()
    
    def on_dismiss(self):
        """Handle notification dismissal."""
        if not self.dismissed:
            self.dismissed = True
            self.root.quit()
            self.root.destroy()
    
    def show(self) -> str:
        """Show the modal notification and return user response."""
        # Show window
        self.root.deiconify()
        
        # Start the event loop
        self.root.mainloop()
        
        return self.user_response or "dismissed"


class ModalNotificationManager:
    """Manages modal notifications for WorkBuddy."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize modal notification manager."""
        self.db_manager = db_manager
        self.active_notifications = {}
        
        # Fallback to toast if modal fails
        self.toast_notifier = ToastNotifier() if TOAST_AVAILABLE else None
    
    def show_modal_notification(self, title: str, message: str, 
                               notification_type: str = "info",
                               auto_dismiss_seconds: int = None,
                               action_callback: Callable = None) -> str:
        """Show a modal notification that blocks interaction."""
        try:
            # Create and show modal notification
            modal = ModalNotificationWindow(
                title=title,
                message=message,
                notification_type=notification_type,
                auto_dismiss_seconds=auto_dismiss_seconds,
                action_callback=action_callback
            )
            
            return modal.show()
            
        except Exception as e:
            print(f"Error showing modal notification: {e}")
            # Fallback to toast notification
            if self.toast_notifier:
                self.toast_notifier.show_toast(title, message, duration=10)
            else:
                print(f"\n🔔 {title}: {message}\n")
            return "error"
    
    def show_break_reminder(self, action_callback: Callable = None) -> str:
        """Show modal break reminder."""
        message = """⏰ It's time for a break!

💻 You've been working hard. Give your eyes and mind a rest.

🚶‍♂️ Recommended break activities:
• Stand up and stretch
• Look out the window for 30 seconds  
• Take 5 deep breaths
• Walk around for 2 minutes
• Hydrate with a glass of water

Your productivity and health will benefit from this short pause!"""
        
        return self.show_modal_notification(
            title="Break Time!",
            message=message,
            notification_type="break",
            auto_dismiss_seconds=30,
            action_callback=action_callback
        )
    
    def show_eye_strain_reminder(self, action_callback: Callable = None) -> str:
        """Show modal 20-20-20 eye strain reminder."""
        message = """👁️ 20-20-20 Eye Care Rule

Look at something 20 feet away for 20 seconds to rest your eyes.

🔍 Right now:
1. Look away from your screen
2. Find an object at least 20 feet away (window, far wall)
3. Focus on it for 20 seconds
4. Blink slowly several times

💡 Additional eye care tips:
• Adjust screen brightness to match surroundings
• Keep screen 20-26 inches from your eyes
• Take breaks every hour for eye health"""
        
        return self.show_modal_notification(
            title="Eye Strain Prevention",
            message=message,
            notification_type="eye_strain",
            auto_dismiss_seconds=25,
            action_callback=action_callback
        )
    
    def show_posture_reminder(self, action_callback: Callable = None) -> str:
        """Show modal posture check reminder."""
        message = """🦴 Posture Check Time!

Check your posture right now:
✓ Feet flat on floor
✓ Back straight against chair  
✓ Shoulders relaxed (not hunched)
✓ Screen at eye level
✓ Wrists in neutral position

🤸‍♂️ Quick exercises (30 seconds each):
• Shoulder rolls (10 backwards, 10 forwards)
• Neck stretches (gently tilt each side)
• Chin tucks (pull chin back, hold 5 seconds)
• Upper back stretch (clasp hands, reach forward)

Your spine will thank you!"""
        
        return self.show_modal_notification(
            title="Posture & Ergonomics Check",
            message=message,
            notification_type="posture",
            auto_dismiss_seconds=30,
            action_callback=action_callback
        )
    
    def show_focus_complete(self, duration_minutes: int, action_callback: Callable = None) -> str:
        """Show modal focus session completion."""
        message = f"""🎉 Focus Session Complete!

⏱️ You completed a {duration_minutes}-minute focus session!

🧠 Great job staying focused and productive.

🌟 What's next?
• Take a well-deserved break
• Continue with another focus session
• Review what you accomplished

Consistent focus sessions improve concentration and reduce mental fatigue."""
        
        return self.show_modal_notification(
            title="Focus Session Complete! 🎯",
            message=message,
            notification_type="focus_complete",
            action_callback=action_callback
        )
    
    def show_hydration_reminder(self, action_callback: Callable = None) -> str:
        """Show modal hydration reminder."""
        message = """💧 Hydration Check!

Time to drink some water. Your body and brain need it to function optimally.

🥤 Hydration benefits:
• Maintains energy levels
• Improves cognitive function  
• Prevents headaches
• Supports overall health

💡 Hydration tips:
• Add lemon, cucumber, or mint for flavor
• Keep a water bottle at your desk
• Aim for 8 glasses throughout the day
• Notice if you feel thirsty - you're already dehydrated!"""
        
        return self.show_modal_notification(
            title="Hydration Time! 💧",
            message=message,
            notification_type="hydration",
            auto_dismiss_seconds=20,
            action_callback=action_callback
        )
    
    def show_mood_checkin(self, action_callback: Callable = None) -> str:
        """Show modal mood check-in."""
        message = """💚 Wellness Check-In

How are you feeling right now? Take a moment to check in with yourself.

🧠 Mental health matters:
• It's okay to have ups and downs
• Taking breaks is productive, not lazy
• Your feelings are valid
• Self-care is essential, not selfish

🌟 Quick mood boosters:
• Take 3 deep breaths
• Think of something you're grateful for
• Step outside for fresh air
• Listen to a favorite song

Remember: You're doing your best, and that's enough. 💙"""
        
        return self.show_modal_notification(
            title="Mood & Wellness Check-In",
            message=message,
            notification_type="mood",
            action_callback=action_callback
        )
    
    def show_console_notification(self, title: str, message: str) -> None:
        """Fallback console notification method for compatibility."""
        print(f"\n{title}")
        print("-" * len(title))
        print(message)
        print()
    
    def show_toast_notification(self, title: str, message: str, icon: str = None, duration: int = 10) -> None:
        """Fallback toast notification method for compatibility."""
        # Try to use the basic notifier if available, otherwise console
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=duration, threaded=True)
        except:
            # Fall back to console if toast fails
            self.show_console_notification(title, message)


if __name__ == "__main__":
    # Test the modal notification system
    from db.database import DatabaseManager
    
    def test_callback(action, notification_type):
        print(f"Action: {action}, Type: {notification_type}")
    
    db = DatabaseManager("../data/usage.db")
    modal_manager = ModalNotificationManager(db)
    
    print("Testing modal notifications...")
    
    # Test different notification types
    result = modal_manager.show_break_reminder(test_callback)
    print(f"Break reminder result: {result}")
    
    result = modal_manager.show_eye_strain_reminder(test_callback)
    print(f"Eye strain reminder result: {result}")
    
    print("Modal notification tests completed!") 