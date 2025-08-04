"""
Enhanced Wellness Notifier for WorkBuddy app.
Handles eye strain (20-20-20), posture, and other health reminders.
"""

import random
import os
import sys
from datetime import datetime
from typing import List, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from win10toast import ToastNotifier
    # Be very conservative - disable win10toast to prevent WNDPROC errors
    # This library is known to cause Windows API issues in certain environments
    print("⚠️ win10toast library detected in wellness notifier but disabled to prevent Windows API errors")
    TOAST_AVAILABLE = False
except (ImportError, Exception) as e:
    TOAST_AVAILABLE = False
    print(f"Warning: win10toast not available in wellness notifier: {e}")

from db.database import DatabaseManager
from tracker.notifier import WorkBuddyNotifier


class WellnessNotifier(WorkBuddyNotifier):
    """Enhanced notifier with specialized wellness reminders."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize wellness notifier."""
        super().__init__(db_manager)
        self.posture_exercises = self.load_posture_exercises()
        self.eye_strain_tips = self.load_eye_strain_tips()
        self.micro_exercises = self.load_micro_exercises()
        self.ambient_comfort_checks = self.load_ambient_checks()
        self.nutrition_tips = self.load_nutrition_tips()
    
    def load_posture_exercises(self) -> List[str]:
        """Load posture and ergonomic exercises."""
        return [
            "🦴 Chin Tucks: Pull your chin back and hold for 5 seconds. Repeat 5 times.",
            "🦴 Shoulder Rolls: Roll your shoulders backward 10 times, then forward 10 times.",
            "🦴 Neck Stretch: Gently tilt your head to each side, hold for 10 seconds.",
            "🦴 Upper Trap Stretch: Reach one hand over your head to the opposite ear, hold 15 seconds each side.",
            "🦴 Doorway Chest Stretch: Place your arm against a doorframe and step forward to stretch.",
            "🦴 Seated Spinal Twist: While seated, twist your torso to each side, hold for 10 seconds.",
            "🦴 Cat-Cow Stretch: Arch and round your back while seated, repeat 10 times.",
            "🦴 Shoulder Blade Squeeze: Pull your shoulder blades together, hold for 5 seconds, repeat 10 times."
        ]
    
    def load_eye_strain_tips(self) -> List[str]:
        """Load eye strain prevention tips beyond 20-20-20."""
        return [
            "👁️ Blink Deliberately: Blink slowly and completely 10 times to refresh your eyes.",
            "👁️ Adjust Screen Brightness: Match your screen brightness to your surroundings.",
            "👁️ Check Screen Distance: Your screen should be 20-26 inches from your eyes.",
            "👁️ Screen Position: Top of screen should be at or below eye level.",
            "👁️ Reduce Glare: Position your screen perpendicular to windows.",
            "👁️ Use Artificial Tears: If eyes feel dry, use preservative-free eye drops.",
            "👁️ Focus Exercise: Hold your finger 6 inches away, focus on it, then focus far away.",
            "👁️ Palm Covering: Cover closed eyes with palms for 30 seconds to rest them."
        ]
    
    def load_micro_exercises(self) -> List[Dict[str, str]]:
        """Load micro-exercises for desk workers."""
        return [
            {
                "name": "Wrist Circles",
                "emoji": "🤚",
                "instruction": "Make 10 slow circles with your wrists in each direction.",
                "duration": "30 seconds"
            },
            {
                "name": "Ankle Pumps", 
                "emoji": "🦶",
                "instruction": "Point your toes up, then down. Repeat 15 times each foot.",
                "duration": "45 seconds"
            },
            {
                "name": "Seated Marching",
                "emoji": "🚶",
                "instruction": "While seated, lift your knees alternately as if marching in place.",
                "duration": "1 minute"
            },
            {
                "name": "Desk Push-ups",
                "emoji": "💪",
                "instruction": "Stand arm's length from your desk, place hands on edge, do 10 push-ups.",
                "duration": "1 minute"
            },
            {
                "name": "Calf Raises",
                "emoji": "🦵",
                "instruction": "Stand and raise up on your toes, hold for 2 seconds, repeat 15 times.",
                "duration": "45 seconds"
            },
            {
                "name": "Deep Breathing",
                "emoji": "🫁",
                "instruction": "Breathe in for 4 counts, hold for 4, exhale for 6. Repeat 5 times.",
                "duration": "1 minute"
            }
        ]
    
    def load_ambient_checks(self) -> List[str]:
        """Load ambient comfort check reminders."""
        return [
            "🌡️ Temperature Check: Is your workspace temperature comfortable? Adjust if needed.",
            "💡 Lighting Check: Is your workspace well-lit without glare? Adjust lighting.",
            "🪑 Chair Check: Are you sitting with good posture? Adjust your chair height.",
            "🖥️ Monitor Check: Is your screen at the right height and distance?",
            "🌪️ Air Quality Check: Is the air fresh? Consider opening a window or adjusting ventilation.",
            "🔇 Noise Check: Is your environment conducive to focus? Use headphones if needed.",
            "🧹 Workspace Check: Is your desk organized and clutter-free?",
            "🌿 Plants Check: Do you have any greenery nearby? Plants can improve air quality and mood."
        ]
    
    def load_nutrition_tips(self) -> List[Dict[str, str]]:
        """Load healthy snack and nutrition tips by time of day."""
        return [
            {
                "time": "morning",
                "emoji": "🌅",
                "tip": "Start with protein: Greek yogurt, nuts, or a hard-boiled egg for sustained energy."
            },
            {
                "time": "mid-morning",
                "emoji": "🍎",
                "tip": "Fresh fruit time: An apple, banana, or berries provide natural energy and vitamins."
            },
            {
                "time": "afternoon",
                "emoji": "🥜",
                "tip": "Healthy fats: A handful of almonds, walnuts, or pumpkin seeds combat afternoon slumps."
            },
            {
                "time": "late-afternoon",
                "emoji": "🥕",
                "tip": "Crunchy veggies: Carrot sticks, bell peppers, or cucumber with hummus."
            },
            {
                "time": "any",
                "emoji": "💧",
                "tip": "Hydration boost: Add lemon, cucumber, or mint to your water for flavor."
            }
        ]
    
    def send_eye_strain_reminder(self) -> None:
        """Send 20-20-20 rule reminder with additional eye care tips."""
        messages = [
            "👁️ 20-20-20 Rule Time! Look at something 20 feet away for 20 seconds to rest your eyes.",
            "👁️ Eye Break! Find something in the distance and focus on it for 20 seconds.",
            "👁️ Give your eyes a break! Look out the window or at the far wall for 20 seconds.",
            "👁️ Screen break time! Look away from your screen and focus on distant objects."
        ]
        
        # Add a random eye care tip
        eye_tip = random.choice(self.eye_strain_tips)
        
        main_message = random.choice(messages)
        full_message = f"{main_message}\n\nBonus tip: {eye_tip}"
        
        # Log to console
        self.show_console_notification("👁️ Eye Strain Prevention", full_message)
        
        # Show toast notification
        self.show_toast_notification(
            "WorkBuddy - Eye Care Reminder",
            f"👁️ 20-20-20 Rule: Look 20 feet away for 20 seconds!\n{eye_tip}",
            duration=20
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("eye_strain")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Eye strain reminder sent")
    
    def send_posture_reminder(self) -> None:
        """Send posture and ergonomic reminder with exercises."""
        exercises = random.sample(self.posture_exercises, 2)  # Pick 2 random exercises
        
        message = f"""🦴 Posture Check Time!
        
Check your posture right now:
• Feet flat on floor
• Back straight against chair
• Shoulders relaxed
• Screen at eye level

Quick exercises to try:
1. {exercises[0]}
2. {exercises[1]}

Your spine will thank you!"""
        
        # Log to console
        self.show_console_notification("🦴 Posture & Ergonomics", message)
        
        # Show toast notification
        self.show_toast_notification(
            "WorkBuddy - Posture Check",
            "🦴 Posture reminder: Sit straight, relax shoulders, feet flat!\nTry some quick stretches.",
            duration=15
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("posture")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Posture reminder sent")
    
    def send_micro_exercise_reminder(self) -> None:
        """Send micro-exercise break reminder."""
        exercise = random.choice(self.micro_exercises)
        
        message = f"""🏃 Micro-Exercise Break!
        
{exercise['emoji']} {exercise['name']}
Duration: {exercise['duration']}

Instructions:
{exercise['instruction']}

Small movements make a big difference for your health!"""
        
        # Log to console
        self.show_console_notification("🏃 Micro-Exercise Time", message)
        
        # Show toast notification
        self.show_toast_notification(
            "WorkBuddy - Exercise Break",
            f"{exercise['emoji']} {exercise['name']}: {exercise['instruction']}",
            duration=12
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("micro_exercise")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Micro-exercise reminder sent")
    
    def send_ambient_comfort_reminder(self) -> None:
        """Send ambient environment comfort check."""
        check = random.choice(self.ambient_comfort_checks)
        
        message = f"""🌡️ Comfort & Environment Check
        
{check}

A comfortable workspace improves focus and reduces stress. Take a moment to optimize your environment!"""
        
        # Log to console
        self.show_console_notification("🌡️ Environment Check", message)
        
        # Show toast notification
        self.show_toast_notification(
            "WorkBuddy - Comfort Check",
            check,
            duration=10
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("ambient_comfort")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ambient comfort reminder sent")
    
    def send_nutrition_reminder(self) -> None:
        """Send healthy snack and nutrition reminder."""
        # Determine time of day for appropriate suggestion
        hour = datetime.now().hour
        
        if 6 <= hour < 10:
            time_category = "morning"
        elif 10 <= hour < 12:
            time_category = "mid-morning"
        elif 14 <= hour < 16:
            time_category = "afternoon"
        elif 16 <= hour < 18:
            time_category = "late-afternoon"
        else:
            time_category = "any"
        
        # Get appropriate nutrition tip
        relevant_tips = [tip for tip in self.nutrition_tips if tip["time"] in [time_category, "any"]]
        nutrition_tip = random.choice(relevant_tips)
        
        message = f"""🍎 Healthy Snack Time!
        
{nutrition_tip['emoji']} {nutrition_tip['tip']}

Remember: Eating well fuels your brain and maintains energy levels throughout the day."""
        
        # Log to console
        self.show_console_notification("🍎 Nutrition Reminder", message)
        
        # Show toast notification
        self.show_toast_notification(
            "WorkBuddy - Healthy Snack",
            f"{nutrition_tip['emoji']} {nutrition_tip['tip']}",
            duration=12
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("nutrition")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Nutrition reminder sent")
    
    def send_mood_checkin(self) -> None:
        """Send mood check-in prompt."""
        prompts = [
            "😊 How are you feeling right now? Take a moment to check in with yourself.",
            "🧠 Mental health check: What's your energy level and mood like today?",
            "💭 Quick reflection: What's going well for you right now?",
            "❤️ Self-care moment: How can you be kind to yourself today?",
            "🌟 Gratitude check: What's one thing you're grateful for right now?"
        ]
        
        prompt = random.choice(prompts)
        
        message = f"""💚 Mood & Wellness Check-in
        
{prompt}

Remember: It's okay to have ups and downs. Your mental health matters, and taking breaks is productive!"""
        
        # Log to console
        self.show_console_notification("💚 Mood Check-in", message)
        
        # Show toast notification
        self.show_toast_notification(
            "WorkBuddy - Wellness Check",
            prompt,
            duration=15
        )
        
        # Log reminder in database
        self.db_manager.log_reminder("mood_checkin")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Mood check-in sent")
    
    def test_wellness_notifications(self) -> None:
        """Test all wellness notification types."""
        print("Testing enhanced wellness notifications...")
        
        notifications = [
            ("Eye Strain (20-20-20)", self.send_eye_strain_reminder),
            ("Posture & Ergonomics", self.send_posture_reminder),
            ("Micro-Exercise", self.send_micro_exercise_reminder),
            ("Ambient Comfort", self.send_ambient_comfort_reminder),
            ("Nutrition", self.send_nutrition_reminder),
            ("Mood Check-in", self.send_mood_checkin)
        ]
        
        for i, (name, func) in enumerate(notifications, 1):
            print(f"\n{i}. Testing {name}...")
            func()
            if i < len(notifications):  # Don't sleep after the last one
                import time
                time.sleep(2)
        
        print("\nAll wellness notifications tested!")


if __name__ == "__main__":
    # Test the wellness notifier
    from db.database import DatabaseManager
    
    db = DatabaseManager("../data/usage.db")
    wellness_notifier = WellnessNotifier(db)
    wellness_notifier.test_wellness_notifications() 