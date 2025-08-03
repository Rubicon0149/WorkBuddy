# 🎯 WorkBuddy - Employee Wellness & Productivity Tracker

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> **WorkBuddy** is a comprehensive desktop wellness and productivity application designed for Windows. It combines traditional productivity tools like Pomodoro timers with advanced wellness features including energy tracking, guided meditation, ambient soundscapes, and intelligent health reminders.

## 🌟 Screenshots & Demo

*Beautiful, intuitive multi-level menu system*

```
╔════════════════════════════════════════════════════════════╗
║              🎯 WorkBuddy - Wellness Dashboard              ║
╚════════════════════════════════════════════════════════════╝

🏠 WORKBUDDY DASHBOARD - Choose a Feature Category
────────────────────────────────────────────────────────────
1️⃣  🎯 Focus & Productivity
2️⃣  📊 Tracking & Analytics  
3️⃣  🧘 Wellness & Health
4️⃣  🎧 Ambient & Soundscapes
5️⃣  🔧 System & Testing
6️⃣  ❓ Help & Documentation
7️⃣  🚪 Exit WorkBuddy
```

## ✨ Features

### 🔍 **Activity Tracking**
- **Real-time app monitoring**: Tracks which application is in the foreground and usage duration
- **Intelligent idle detection**: Automatically pauses tracking when system is idle for 5+ minutes
- **SQLite storage**: All data stored locally in a secure SQLite database
- **Privacy-focused**: No data leaves your computer

### 🔔 **Smart Reminders**
- **Break reminders**: Every 45 minutes (customizable)
- **Hydration alerts**: Every 2 hours (customizable)
- **Inspirational messages**: Every 3 hours with motivational quotes and wellness tips
- **Daily summary**: End-of-day report with screen time and top applications

### ⚙️ **Intelligent Scheduling**
- **Work hours awareness**: Only sends reminders during configured work hours (9 AM - 6 PM by default)
- **Weekday focus**: Can be configured to only run on work days (Monday-Friday)
- **Customizable intervals**: All reminder timings can be adjusted via settings

### 📊 **Analytics & Insights**
- **Daily usage reports**: See how much time you spend on different applications
- **Historical data**: Track trends over time (30-day retention)
- **Productivity insights**: Understand your work patterns

## 🚀 Quick Start

### Prerequisites
- **Windows 10/11** (required for Windows API features)
- **Python 3.11+** 
- **Administrator privileges** (for some Windows API calls)

### Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd workbuddy
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv workbuddy_env
   workbuddy_env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run WorkBuddy:**
   ```bash
   python main.py
   ```

### First Launch
On first launch, WorkBuddy will:
- Create the SQLite database (`data/usage.db`)
- Generate default configuration (`config/settings.json`)
- Create quotes file (`assets/quotes.txt`)
- Start activity tracking and reminder scheduling

## 🖥️ Usage

### Interactive Commands
Once WorkBuddy is running, you can use these commands:

- `status` - Show current tracking status and statistics
- `summary` - Display today's app usage summary
- `test` - Test all notification types
- `help` - Show available commands
- `quit` or `exit` - Stop WorkBuddy

### Example Session
```
🎯 WorkBuddy - Employee Wellness Tracker
============================================================
Started at: 14:30:15
Database: data/usage.db
============================================================

🟢 WorkBuddy is now running in the background!
💡 Features active:
   • App usage tracking
   • Break reminders (every 45 min)
   • Hydration reminders (every 2 hours)
   • Inspiration messages (every 3 hours)
   • Daily summary (5 PM)

WorkBuddy> status
📊 WorkBuddy Status:
----------------------------------------
Uptime: 25 minutes
Tracking: 🟢 Active
Current app: Code (main.py - WorkBuddy)
Session time: 15 minutes
System idle: No
Reminders: 🟢 Active
Active timers: break, hydration, inspiration, daily_summary
Work hours: Yes
Work day: Yes
```

## 📁 Project Structure

```
workbuddy/
├── main.py                 # Main application entry point
├── tracker/
│   ├── activity_tracker.py # Windows app focus monitoring
│   ├── notifier.py         # Reminder notifications
│   └── scheduler.py        # Reminder scheduling logic
├── db/
│   └── database.py         # SQLite database operations
├── utils/
│   └── time_utils.py       # Time formatting utilities
├── config/
│   └── settings.json       # App configuration (auto-generated)
├── assets/
│   └── quotes.txt          # Inspirational quotes (auto-generated)
├── data/
│   └── usage.db           # SQLite database (auto-generated)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ⚙️ Configuration

WorkBuddy creates a `config/settings.json` file with these customizable options:

```json
{
    "break_interval": 45,           // Break reminder interval (minutes)
    "hydration_interval": 120,      // Hydration reminder interval (minutes)
    "inspiration_interval": 180,    // Inspiration reminder interval (minutes)
    "daily_summary_time": "17:00",  // Daily summary time (24h format)
    "work_start_time": "09:00",     // Work day start time
    "work_end_time": "18:00",       // Work day end time
    "notifications_enabled": true,   // Enable/disable all notifications
    "sound_enabled": true,          // Enable notification sounds
    "work_days_only": true,         // Only run on weekdays
    "idle_pause_reminders": true    // Pause when system is idle
}
```

## 📊 Database Schema

WorkBuddy uses SQLite with these tables:

### `app_usage`
Stores application usage sessions:
- `id` - Unique session ID
- `app_name` - Application name with window title
- `start_time` - Session start timestamp
- `end_time` - Session end timestamp
- `duration_seconds` - Session duration
- `created_at` - Record creation time

### `daily_summary`
Stores daily usage summaries:
- `date` - Date (YYYY-MM-DD)
- `total_screen_time` - Total screen time in seconds
- `top_apps` - JSON string of top applications
- `created_at` - Summary creation time

### `reminders_log`
Tracks when reminders were sent:
- `id` - Unique reminder ID
- `reminder_type` - Type (break, hydration, inspiration, daily_summary)
- `sent_at` - When reminder was sent

## 🔧 Technical Details

### Windows API Integration
- Uses `ctypes` and `windll.user32` for window detection
- `GetForegroundWindow()` - Gets active window handle
- `GetWindowText()` - Retrieves window title
- `GetWindowThreadProcessId()` - Gets process information
- `GetLastInputInfo()` - Detects system idle time

### Threading Architecture
- **Main thread**: Interactive command processing
- **Activity tracker thread**: Monitors active windows (5-second intervals)
- **Scheduler timers**: Independent threads for each reminder type
- **Graceful shutdown**: Proper cleanup of all threads and resources

### Notification System
- **Primary**: Windows 10 Toast Notifications via `win10toast`
- **Fallback**: Console notifications if toast unavailable
- **Types**: Break, hydration, inspiration, daily summary

## 🛡️ Privacy & Security

- **Local-only**: All data stays on your computer
- **No network communication**: No data sent to external servers
- **Minimal permissions**: Only requires standard user access (some features may need admin)
- **Data retention**: Automatically cleans up data older than 30 days
- **Transparent**: Open source code for full transparency

## 🔮 Future Enhancements

### Planned Features
- **System tray integration**: Run completely in background with tray icon
- **Auto-start on Windows boot**: Seamless integration with Windows startup
- **Web dashboard**: Optional local web interface for detailed analytics
- **Export functionality**: Export usage data to CSV/JSON
- **Custom reminder types**: User-defined reminder categories
- **Focus sessions**: Pomodoro-style work sessions with break enforcement
- **Wellness scoring**: Daily wellness metrics based on usage patterns

### Potential Integrations
- **Calendar integration**: Respect meeting times for reminders
- **Health apps**: Integration with fitness trackers
- **Team features**: Anonymous team wellness metrics
- **Slack/Teams**: Reminder integration with communication tools

## 🐛 Troubleshooting

### Common Issues

**"Error getting active window info"**
- Ensure you have proper Windows permissions
- Try running as administrator
- Check if antivirus is blocking the application

**"Toast notifications not working"**
- Verify Windows 10/11 toast notifications are enabled
- Check Windows notification settings
- Application falls back to console notifications automatically

**"Database permission errors"**
- Ensure write permissions in the WorkBuddy directory
- Try running from a folder with full user permissions

**"Activity tracking not starting"**
- Check if Windows API access is blocked
- Verify psutil can access process information
- Some corporate environments may restrict these APIs

### Debug Mode
Add `--debug` flag when running for verbose logging:
```bash
python main.py --debug
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Windows API Documentation** - Microsoft Developer Documentation
- **Toast Notifications** - Windows 10 Toast Notification API
- **Mental Health Awareness** - Inspired by workplace wellness initiatives
- **Open Source Libraries** - All the amazing Python libraries that make this possible

---

**WorkBuddy** - Taking care of your mental health, one reminder at a time. 💚

Made with ❤️ for employee wellness and productivity.

## 📞 Support

If you encounter issues or have questions:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information
4. For urgent matters, contact the development team

Remember: Your mental health matters! 🧠💚 