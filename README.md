# Calendar Reminder App

## Overview
This is a simple calendar reminder application built using Python and Tkinter. It allows users to add, edit, and delete events, and sends Telegram notifications when an event is near. Events are saved in a JSON file for persistence.

## Features
- Add, edit, and delete events with a user-friendly interface
- Set reminders for events
- Automatic Telegram notifications
- Saves events locally in a JSON file

## Requirements
- Python 3.x
- Tkinter (included with Python)
- Requests library for Telegram API communication

## Installation
1. Clone or download the repository.
2. Install dependencies using:
   ```bash
   pip install requests
   ```
3. Update the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the script with your actual Telegram bot details.

## Usage
1. Run the script:
   ```bash
   python calendar_app.py
   ```
2. Use the GUI to add, edit, or delete events.
3. The app will automatically send reminders via Telegram when an event is near.

## Configuration
- **TELEGRAM_BOT_TOKEN**: Replace with your Telegram bot token.
- **TELEGRAM_CHAT_ID**: Replace with your Telegram chat ID.
- **EVENTS_FILE**: JSON file where events are stored.

## File Structure
```
calendar_app.py  # Main application script
events.json      # Stores event data (created automatically)
```

## Troubleshooting
- If Telegram notifications are not working, verify your bot token and chat ID.
- Ensure you have an active internet connection for Telegram messages to send.
- If the JSON file gets corrupted, delete `events.json` and restart the app.

## License
This project is open-source and free to use.

