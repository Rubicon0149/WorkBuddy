"""
Notifier module for WorkBuddy app.
Handles different types of reminders: break, hydration, and inspiration.
"""

import random
import os
import sys
from datetime import datetime
from typing import List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from win10toast import ToastNotifier
    # Be very conservative - disable win10toast to prevent WNDPROC errors
    # This library is known to cause Windows API issues in certain environments
    print("⚠️ win10toast library detected but disabled to prevent Windows API errors")
    print("   Using console notifications for all toast notifications")
    TOAST_AVAILABLE = False
except (ImportError, Exception) as e:
    TOAST_AVAILABLE = False
    print(f"Warning: win10toast not available: {e}. Using console notifications only.")

from db.database import DatabaseManager


class WorkBuddyNotifier:
    def __init__(self, db_manager: DatabaseManager):
        """Initialize notifier with database manager."""
        self.db_manager = db_manager
        # Only create toaster if it's known to be working
        self.toaster = None
        if TOAST_AVAILABLE:
            try:
                self.toaster = ToastNotifier()
            except Exception as e:
                print(f"Warning: Failed to create ToastNotifier: {e}")
                self.toaster = None
        self.quotes = self.load_quotes()
    
    def load_quotes(self) -> List[str]:
        """Load inspirational quotes from assets/quotes.txt."""
        quotes_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'quotes.txt')
        
        default_quotes = [
            "Take care of your body. It's the only place you have to live.",
            "A healthy mind lives in a healthy body.",
            "Rest when you're weary. Refresh and renew yourself, your body, your mind, your spirit.",
            "Small steps in the right direction can turn out to be the biggest step of your life.",
            "You are capable of more than you know.",
            "Progress, not perfection.",
            "Every moment is a fresh beginning.",
            "Take time to make your soul happy.",
            "Breathe in peace, breathe out stress.",
            "Your mental health is a priority. Your happiness is essential.",
            "It's okay to take a break. It's okay to rest.",
            "You don't have to be productive every moment of every day.",
            "Mental health is not a luxury. It's a necessity.",
            "Be gentle with yourself. You're doing the best you can.",
            "Your worth is not determined by your productivity."
        ]
        
        try:
            if os.path.exists(quotes_file):
                with open(quotes_file, 'r', encoding='utf-8') as f:
                    file_quotes = [line.strip() for line in f.readlines() if line.strip()]
                return file_quotes if file_quotes else default_quotes
            else:
                # Create quotes file with default quotes
                os.makedirs(os.path.dirname(quotes_file), exist_ok=True)
                with open(quotes_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(default_quotes))
                return default_quotes
        except Exception as e:
            print(f"Error loading quotes: {e}. Using default quotes.")
            return default_quotes
    
    def show_toast_notification(self, title: str, message: str, duration: int = 10, 
                               icon_path: str = None) -> None:
        """Show Windows toast notification."""
        # Double-check that toast notifications are available and working
        if self.toaster and TOAST_AVAILABLE:
            try:
                self.toaster.show_toast(
                    title=title,
                    msg=message,
                    duration=duration,
                    icon_path=icon_path,
                    threaded=True
                )
            except Exception as e:
                print(f"Toast notification failed with Windows API error: {e}")
                print("📢 Switching to console notifications to prevent crashes...")
                # Disable toaster for future calls to prevent repeated errors
                self.toaster = None
                self.show_console_notification(title, message)
        else:
            # Use console as fallback
            self.show_console_notification(title, message)
    
    def show_console_notification(self, title: str, message: str) -> None:
        """Show notification in console as fallback."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print("\n" + "="*60)
        print(f"🔔 {title} - {timestamp}")
        print("-" * 60)
        print(f"{message}")
        print("="*60 + "\n")
    
    def send_break_reminder(self) -> None:
        """Send break reminder notification."""
        messages = [
            "Time for a break! Give your eyes and mind a rest. Step away from the screen for a few minutes.",
            "Break time! Stand up, stretch, and take a deep breath. Your body will thank you.",
            "You've been working hard! Take a 5-10 minute break to recharge and refocus.",
            "Reminder: Regular breaks improve productivity and reduce eye strain. Take one now!",
            "Time to pause! Look away from the screen, do some light stretching, or take a short walk."
        ]
        
        message = random.choice(messages)
        
        # Log to console
        self.show_console_notification("💻 Break Reminder", message)
        
        # Show toast notification
        self.show_toast_notification(
            title="WorkBuddy - Break Time!",
            message=message,
            duration=15
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("break")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Break reminder sent")
    
    def send_hydration_reminder(self) -> None:
        """Send hydration reminder notification."""
        messages = [
            "💧 Hydration check! Time to drink some water. Your body needs it to function at its best.",
            "Don't forget to hydrate! Grab a glass of water and keep your energy levels up.",
            "Water break! Staying hydrated helps maintain focus and prevents fatigue.",
            "Time for H2O! Proper hydration improves cognitive function and overall well-being.",
            "Hydration reminder: Your brain is 75% water. Keep it happy with a drink!"
        ]
        
        message = random.choice(messages)
        
        # Log to console
        self.show_console_notification("💧 Hydration Reminder", message)
        
        # Show toast notification
        self.show_toast_notification(
            title="WorkBuddy - Hydration Time!",
            message=message,
            duration=12
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("hydration")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Hydration reminder sent")
    
    def send_inspiration_reminder(self) -> None:
        """Send inspirational quote/tip notification."""
        quote = random.choice(self.quotes)
        
        tips = [
            "💡 Tip: Practice the 20-20-20 rule - every 20 minutes, look at something 20 feet away for 20 seconds.",
            "💡 Tip: Take deep breaths regularly. It helps reduce stress and improve concentration.",
            "💡 Tip: Organize your workspace. A clean environment can lead to a clearer mind.",
            "💡 Tip: Set small, achievable goals throughout your day to maintain motivation.",
            "💡 Tip: Listen to music you enjoy while working to boost your mood and productivity."
        ]
        
        # Randomly choose between quote and tip
        if random.choice([True, False]):
            title = "✨ Daily Inspiration"
            message = f"💫 {quote}"
        else:
            title = "💡 Wellness Tip"
            message = random.choice(tips)
        
        # Log to console
        self.show_console_notification(title, message)
        
        # Show toast notification
        self.show_toast_notification(
            title=f"WorkBuddy - {title}",
            message=message,
            duration=15
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("inspiration")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Inspiration reminder sent")
    
    def send_daily_summary(self, total_screen_time: int, top_apps: List[tuple]) -> None:
        """Send end-of-day summary notification."""
        # Convert screen time to hours and minutes
        hours = total_screen_time // 3600
        minutes = (total_screen_time % 3600) // 60
        
        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        # Format top apps
        if top_apps:
            top_apps_str = "\n".join([
                f"{i+1}. {app[0]}: {app[1]//60}m {app[1]%60}s" 
                for i, app in enumerate(top_apps[:3])
            ])
        else:
            top_apps_str = "No app usage recorded today"
        
        message = f"""📊 Daily Summary:
        
⏱️ Total Screen Time: {time_str}

🏆 Top Applications:
{top_apps_str}

Great work today! Remember to maintain a healthy work-life balance."""
        
        # Log to console
        self.show_console_notification("📊 Daily Summary", message)
        
        # Show toast notification
        self.show_toast_notification(
            title="WorkBuddy - Daily Summary",
            message=f"Screen Time: {time_str}\n\nTop Apps:\n{top_apps_str.replace(chr(10), ' • ')}",
            duration=20
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("daily_summary")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Daily summary sent")
    
    def test_notifications(self) -> None:
        """Test all notification types."""
        print("Testing all notification types...")
        
        print("\n1. Testing break reminder...")
        self.send_break_reminder()
        
        print("\n2. Testing hydration reminder...")
        self.send_hydration_reminder()
        
        print("\n3. Testing inspiration reminder...")
        self.send_inspiration_reminder()
        
        print("\n4. Testing daily summary...")
        sample_apps = [("Visual Studio Code", 7200), ("Chrome", 3600), ("Slack", 1800)]
        self.send_daily_summary(12600, sample_apps)
        
        print("\nAll notifications tested!")


if __name__ == "__main__":
    # Test the notifier
    from db.database import DatabaseManager
    
    db = DatabaseManager("../data/usage.db")
    notifier = WorkBuddyNotifier(db)
    notifier.test_notifications() 