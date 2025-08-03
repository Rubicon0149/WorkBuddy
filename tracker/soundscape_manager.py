"""
Focus Soundscape Manager for WorkBuddy app.
Provides white noise and nature sounds for focus and relaxation.
"""

import os
import sys
import threading
import time
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox
import pygame
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import DatabaseManager


class SoundscapePlayer:
    """Manages audio playback for focus soundscapes."""
    
    def __init__(self):
        """Initialize soundscape player."""
        self.is_playing = False
        self.current_sound = None
        self.volume = 0.5
        self.loop_count = -1  # -1 means infinite loop
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.mixer_available = True
            print("✅ Audio mixer initialized")
        except Exception as e:
            print(f"❌ Audio mixer initialization failed: {e}")
            self.mixer_available = False
    
    def load_sound(self, sound_path: str) -> bool:
        """Load a sound file."""
        if not self.mixer_available:
            print("Audio mixer not available")
            return False
        
        try:
            if os.path.exists(sound_path):
                print(f"Loading sound file: {sound_path}")
                self.current_sound = pygame.mixer.Sound(sound_path)
                print(f"Successfully loaded: {sound_path}")
                return True
            else:
                print(f"Sound file not found: {sound_path}")
                return False
        except Exception as e:
            print(f"Error loading sound {sound_path}: {e}")
            return False
    
    def play_sound(self, sound_path: str = None, volume: float = None) -> bool:
        """Play a sound file."""
        if not self.mixer_available:
            return False
        
        try:
            if sound_path:
                if not self.load_sound(sound_path):
                    return False
            
            if not self.current_sound:
                return False
            
            if volume is not None:
                self.volume = max(0.0, min(1.0, volume))
            
            self.current_sound.set_volume(self.volume)
            self.current_sound.play(loops=self.loop_count)
            self.is_playing = True
            return True
            
        except Exception as e:
            print(f"Error playing sound: {e}")
            return False
    
    def stop_sound(self) -> None:
        """Stop current sound."""
        if self.mixer_available:
            pygame.mixer.stop()
            self.is_playing = False
    
    def pause_sound(self) -> None:
        """Pause current sound."""
        if self.mixer_available:
            pygame.mixer.pause()
    
    def resume_sound(self) -> None:
        """Resume paused sound."""
        if self.mixer_available:
            pygame.mixer.unpause()
    
    def set_volume(self, volume: float) -> None:
        """Set playback volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        if self.current_sound:
            self.current_sound.set_volume(self.volume)
    
    def is_sound_playing(self) -> bool:
        """Check if sound is currently playing."""
        if self.mixer_available:
            return pygame.mixer.get_busy()
        return False


class SoundscapeControlWindow:
    """Control window for soundscape management."""
    
    def __init__(self, soundscape_manager):
        """Initialize soundscape control window."""
        self.manager = soundscape_manager
        self.player = soundscape_manager.player
        
        # Create window
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.update_status()
    
    def setup_window(self):
        """Setup the soundscape control window."""
        self.root.title("WorkBuddy - Focus Soundscapes")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Position window (top-right corner)
        self.root.update_idletasks()
        x = self.root.winfo_screenwidth() - 420
        y = 50
        self.root.geometry(f"400x500+{x}+{y}")
        
        self.root.configure(bg='#f0f0f0')
        self.root.attributes('-topmost', True)  # Keep on top
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        """Create the soundscape control widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🎧 Focus Soundscapes", 
                              font=("Segoe UI", 16, "bold"),
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 20))
        
        # Current status
        self.status_label = tk.Label(main_frame, text="No sound playing", 
                                   font=("Segoe UI", 11),
                                   bg='#f0f0f0', fg='#666666')
        self.status_label.pack(pady=(0, 15))
        
        # Sound selection
        sounds_label = tk.Label(main_frame, text="Select Sound:", 
                               font=("Segoe UI", 12, "bold"),
                               bg='#f0f0f0', fg='#333333')
        sounds_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Sound buttons frame
        sounds_frame = ttk.Frame(main_frame)
        sounds_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Available sounds
        self.sounds = {
            "🌧️ Rain": "rain",
            "🌊 Ocean Waves": "ocean",
            "🌲 Forest": "forest", 
            "🔥 Fireplace": "fireplace",
            "☕ Coffee Shop": "coffee_shop",
            "🎵 White Noise": "white_noise",
            "🌸 Pink Noise": "pink_noise",
            "🌊 Brown Noise": "brown_noise"
        }
        
        # Create sound buttons
        row = 0
        col = 0
        for sound_name, sound_key in self.sounds.items():
            btn = ttk.Button(sounds_frame, text=sound_name, width=18,
                           command=lambda k=sound_key, n=sound_name: self.play_sound(k, n))
            btn.grid(row=row, column=col, padx=5, pady=3, sticky="ew")
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Configure grid weights
        sounds_frame.columnconfigure(0, weight=1)
        sounds_frame.columnconfigure(1, weight=1)
        
        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.play_btn = ttk.Button(controls_frame, text="▶️ Play", 
                                  command=self.toggle_playback)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="⏹️ Stop", 
                  command=self.stop_sound).pack(side=tk.LEFT, padx=(0, 10))
        
        # Volume control
        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(fill=tk.X, pady=(20, 0))
        
        volume_label = tk.Label(volume_frame, text="Volume:", 
                               font=("Segoe UI", 11),
                               bg='#f0f0f0', fg='#333333')
        volume_label.pack(anchor=tk.W)
        
        self.volume_var = tk.DoubleVar(value=50)
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.volume_var, command=self.on_volume_change,
                                    bg='#f0f0f0', fg='#333333', highlightthickness=0)
        self.volume_scale.pack(fill=tk.X, pady=(5, 0))
        
        # Timer controls
        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(fill=tk.X, pady=(20, 0))
        
        timer_label = tk.Label(timer_frame, text="Auto-stop timer:", 
                              font=("Segoe UI", 11),
                              bg='#f0f0f0', fg='#333333')
        timer_label.pack(anchor=tk.W)
        
        timer_buttons_frame = ttk.Frame(timer_frame)
        timer_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        timer_options = [("15 min", 15), ("30 min", 30), ("60 min", 60), ("90 min", 90)]
        for text, minutes in timer_options:
            ttk.Button(timer_buttons_frame, text=text, width=8,
                      command=lambda m=minutes: self.set_timer(m)).pack(side=tk.LEFT, padx=2)
        
        # Timer status
        self.timer_label = tk.Label(main_frame, text="", 
                                   font=("Segoe UI", 10),
                                   bg='#f0f0f0', fg='#666666')
        self.timer_label.pack(pady=(10, 0))
        
        # Tips
        tips_text = """💡 Tips:
• Use nature sounds for relaxation
• Try white/pink noise for deep focus
• Lower volume for background ambiance
• Set timers for study sessions"""
        
        tips_label = tk.Label(main_frame, text=tips_text, 
                             font=("Segoe UI", 9), justify=tk.LEFT,
                             bg='#f0f0f0', fg='#666666')
        tips_label.pack(pady=(20, 0))
    
    def play_sound(self, sound_key: str, sound_name: str):
        """Play selected sound."""
        success = self.manager.play_soundscape(sound_key)
        if success:
            self.status_label.config(text=f"Playing: {sound_name}", fg='#44aa44')
            self.play_btn.config(text="⏸️ Pause")
        else:
            self.status_label.config(text="Failed to play sound", fg='#ff4444')
    
    def toggle_playback(self):
        """Toggle play/pause."""
        if self.player.is_sound_playing():
            self.player.pause_sound()
            self.play_btn.config(text="▶️ Resume")
            self.status_label.config(text="Paused", fg='#ff8800')
        else:
            self.player.resume_sound()
            self.play_btn.config(text="⏸️ Pause")
            self.status_label.config(text="Playing", fg='#44aa44')
    
    def stop_sound(self):
        """Stop current sound."""
        self.manager.stop_soundscape()
        self.status_label.config(text="Stopped", fg='#666666')
        self.play_btn.config(text="▶️ Play")
        self.manager.cancel_timer()
        self.timer_label.config(text="")
    
    def on_volume_change(self, value):
        """Handle volume change."""
        volume = float(value) / 100.0
        self.player.set_volume(volume)
    
    def set_timer(self, minutes: int):
        """Set auto-stop timer."""
        self.manager.set_timer(minutes)
        self.timer_label.config(text=f"Timer set: {minutes} minutes")
        print(f"Timer set for {minutes} minutes")  # Debug
    
    def update_status(self):
        """Update status display."""
        # Update timer display
        remaining = self.manager.get_timer_remaining()
        if remaining > 0:
            mins, secs = divmod(int(remaining), 60)
            self.timer_label.config(text=f"Time remaining: {mins:02d}:{secs:02d}")
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def on_close(self):
        """Handle window close."""
        self.root.withdraw()  # Hide instead of destroy
    
    def show(self):
        """Show the control window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide(self):
        """Hide the control window."""
        self.root.withdraw()


class FocusSoundscapeManager:
    """Manages focus soundscapes and ambient sounds."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize soundscape manager."""
        self.db_manager = db_manager
        self.player = SoundscapePlayer()
        self.control_window = None
        self.current_sound = None
        self.timer_thread = None
        self.timer_duration = 0
        self.timer_start = None
        
        # Create sounds directory
        self.sounds_dir = Path(__file__).parent.parent / "assets" / "sounds"
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate synthetic sounds if real files don't exist
        self.ensure_sounds_available()
    
    def ensure_sounds_available(self):
        """Ensure sound files are available (generate if needed)."""
        # For demonstration, we'll create simple tone-based sounds
        # In a real implementation, you'd include actual audio files
        
        sound_generators = {
            "white_noise": self.generate_white_noise,
            "pink_noise": self.generate_pink_noise,
            "brown_noise": self.generate_brown_noise,
            "rain": self.generate_rain_sound,
            "ocean": self.generate_ocean_sound,
            "forest": self.generate_forest_sound,
            "fireplace": self.generate_fire_sound,
            "coffee_shop": self.generate_coffee_shop_sound
        }
        
        for sound_name, generator in sound_generators.items():
            sound_file = self.sounds_dir / f"{sound_name}.wav"
            if not sound_file.exists():
                try:
                    print(f"Generating {sound_name} sound...")
                    generator(str(sound_file))
                except Exception as e:
                    print(f"Failed to generate {sound_name}: {e}")
    
    def generate_white_noise(self, filename: str):
        """Generate white noise audio file."""
        import numpy as np
        import wave
        
        # Generate 10 seconds of white noise
        duration = 10  # seconds
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Generate white noise
        noise = np.random.normal(0, 0.1, samples)
        noise = (noise * 32767).astype(np.int16)
        
        # Save as WAV
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(noise.tobytes())
    
    def generate_pink_noise(self, filename: str):
        """Generate pink noise audio file."""
        import numpy as np
        import wave
        
        duration = 10
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Generate pink noise (simplified version)
        white_noise = np.random.normal(0, 0.1, samples)
        # Apply simple filtering to approximate pink noise
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        
        # Simple filter approximation
        pink_noise = white_noise * 0.5  # Simplified pink noise
        pink_noise = (pink_noise * 32767).astype(np.int16)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pink_noise.tobytes())
    
    def generate_brown_noise(self, filename: str):
        """Generate brown noise audio file."""
        import numpy as np
        import wave
        
        duration = 10
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Generate brown noise
        white_noise = np.random.normal(0, 0.1, samples)
        brown_noise = np.cumsum(white_noise) * 0.01  # Brownian motion
        brown_noise = (brown_noise * 32767).astype(np.int16)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(brown_noise.tobytes())
    
    def generate_rain_sound(self, filename: str):
        """Generate rain sound simulation."""
        import numpy as np
        import wave
        
        duration = 10
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Simulate rain with filtered noise
        rain = np.random.normal(0, 0.05, samples)
        # Add some low-frequency rumble
        t = np.linspace(0, duration, samples)
        rumble = 0.02 * np.sin(2 * np.pi * 0.5 * t) * np.random.normal(1, 0.1, samples)
        rain_sound = rain + rumble
        rain_sound = (rain_sound * 32767).astype(np.int16)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(rain_sound.tobytes())
    
    def generate_ocean_sound(self, filename: str):
        """Generate ocean wave sound simulation."""
        import numpy as np
        import wave
        
        duration = 10
        sample_rate = 22050
        samples = int(duration * sample_rate)
        
        # Generate ocean waves
        t = np.linspace(0, duration, samples)
        # Main wave pattern
        waves = 0.3 * np.sin(2 * np.pi * 0.2 * t) * (1 + 0.5 * np.sin(2 * np.pi * 0.05 * t))
        # Add noise for foam/bubbles
        foam = 0.1 * np.random.normal(0, 1, samples)
        ocean_sound = waves + foam
        ocean_sound = (ocean_sound * 32767).astype(np.int16)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(ocean_sound.tobytes())
    
    def generate_forest_sound(self, filename: str):
        """Generate forest ambiance simulation."""
        # Simplified - use filtered white noise
        self.generate_white_noise(filename)
    
    def generate_fire_sound(self, filename: str):
        """Generate fireplace crackling simulation."""
        # Simplified - use brown noise
        self.generate_brown_noise(filename)
    
    def generate_coffee_shop_sound(self, filename: str):
        """Generate coffee shop ambiance simulation."""
        # Simplified - use pink noise
        self.generate_pink_noise(filename)
    
    def play_soundscape(self, sound_key: str) -> bool:
        """Play a soundscape."""
        sound_file = self.sounds_dir / f"{sound_key}.wav"
        print(f"Attempting to play soundscape: {sound_key}")
        print(f"Sound file path: {sound_file}")
        
        if sound_file.exists():
            print(f"Sound file exists, size: {sound_file.stat().st_size} bytes")
            success = self.player.play_sound(str(sound_file))
            if success:
                self.current_sound = sound_key
                print(f"✅ Successfully playing soundscape: {sound_key}")
            else:
                print(f"❌ Failed to play soundscape: {sound_key}")
            return success
        else:
            print(f"❌ Sound file not found: {sound_file}")
            return False
    
    def stop_soundscape(self):
        """Stop current soundscape."""
        self.player.stop_sound()
        self.current_sound = None
        print("Soundscape stopped")
    
    def set_timer(self, minutes: int):
        """Set auto-stop timer."""
        self.cancel_timer()
        
        self.timer_duration = minutes * 60  # Convert to seconds
        self.timer_start = time.time()
        print(f"Timer started: {minutes} minutes ({self.timer_duration} seconds)")
        
        def timer_callback():
            start_time = time.time()
            while (time.time() - start_time) < self.timer_duration:
                if not self.timer_thread or not self.timer_thread.is_alive():
                    break  # Timer was cancelled
                time.sleep(1)
            
            if self.timer_thread and self.timer_thread.is_alive():
                self.stop_soundscape()
                print(f"🔔 Soundscape auto-stopped after {minutes} minutes")
        
        self.timer_thread = threading.Thread(target=timer_callback, daemon=True)
        self.timer_thread.start()
        print(f"Timer set for {minutes} minutes")
    
    def cancel_timer(self):
        """Cancel current timer."""
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread = None
        self.timer_duration = 0
        self.timer_start = None
    
    def get_timer_remaining(self) -> float:
        """Get remaining timer time in seconds."""
        if self.timer_start and self.timer_duration > 0:
            elapsed = time.time() - self.timer_start
            remaining = self.timer_duration - elapsed
            return max(0, remaining)
        return 0
    
    def show_control_window(self):
        """Show soundscape control window."""
        if not self.control_window:
            self.control_window = SoundscapeControlWindow(self)
        
        self.control_window.show()
    
    def hide_control_window(self):
        """Hide soundscape control window."""
        if self.control_window:
            self.control_window.hide()
    
    def get_available_sounds(self) -> List[str]:
        """Get list of available sound files."""
        sounds = []
        for sound_file in self.sounds_dir.glob("*.wav"):
            sounds.append(sound_file.stem)
        return sounds
    
    def get_status(self) -> Dict:
        """Get current soundscape status."""
        return {
            "is_playing": self.player.is_sound_playing(),
            "current_sound": self.current_sound,
            "volume": self.player.volume,
            "timer_remaining": self.get_timer_remaining(),
            "available_sounds": self.get_available_sounds()
        }


if __name__ == "__main__":
    # Test soundscape manager
    from db.database import DatabaseManager
    
    db = DatabaseManager("../data/usage.db")
    soundscape_manager = FocusSoundscapeManager(db)
    
    print("Soundscape Manager initialized!")
    print(f"Available sounds: {soundscape_manager.get_available_sounds()}")
    
    # Show control window for testing
    soundscape_manager.show_control_window()
    
    # Keep the test running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping soundscape manager...")
        soundscape_manager.stop_soundscape() 