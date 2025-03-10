import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
import datetime
import requests

# === CONFIGURATION: Set these with your Telegram Bot details ===
TELEGRAM_BOT_TOKEN = "7777704982:AAENdawbGbre5MjIP9F6ckBV2g3EiELBRj4"  # Replace with your bot token
TELEGRAM_CHAT_ID = "886470354"      # Replace with your chat id

EVENTS_FILE = "events.json"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# --- Custom Dialog for Event Details ---
class EventDialog(tk.Toplevel):
    def __init__(self, parent, title="", date_str="", hour="12", minute="00", notify_days="0"):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.parent = parent
        self.result = None

        self.title("Event Details")

        # Title
        tk.Label(self, text="Event Title:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.title_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)
        self.title_entry.insert(0, title)

        # Date (DD/MM/YYYY)
        tk.Label(self, text="Date (DD/MM/YYYY):", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = tk.Entry(self, width=30, font=("Arial", 12))
        self.date_entry.grid(row=1, column=1, padx=10, pady=5)
        self.date_entry.insert(0, date_str)

        # Time selection: Hour and Minute drop-downs
        tk.Label(self, text="Hour (24h):", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.hour_var = tk.StringVar(value=hour)
        hours = [f"{h:02d}" for h in range(24)]
        self.hour_menu = ttk.Combobox(self, textvariable=self.hour_var, values=hours, width=5, state="readonly")
        self.hour_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self, text="Minute:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.minute_var = tk.StringVar(value=minute)
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        self.minute_menu = ttk.Combobox(self, textvariable=self.minute_var, values=minutes, width=5, state="readonly")
        self.minute_menu.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Notification lead time: Days before event
        tk.Label(self, text="Notify (days before):", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.notify_var = tk.StringVar(value=notify_days)
        days = [str(d) for d in range(8)]  # 0 to 7 days
        self.notify_menu = ttk.Combobox(self, textvariable=self.notify_var, values=days, width=5, state="readonly")
        self.notify_menu.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ok_btn = tk.Button(button_frame, text="OK", width=10, command=self.on_ok)
        ok_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = tk.Button(button_frame, text="Cancel", width=10, command=self.on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self)

    def on_ok(self):
        self.result = {
            "title": self.title_entry.get(),
            "date": self.date_entry.get(),
            "hour": self.hour_var.get(),
            "minute": self.minute_var.get(),
            "notify_days": int(self.notify_var.get())
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

# --- Calendar App with Notifications ---
class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Retro Calendar Reminder")
        self.root.geometry("1000x600")
        self.root.config(padx=20, pady=20)

        self.events = []  # Each event is a dict with: title, datetime (ISO string), notify_days, notified flag
        self.load_events()
        self.create_widgets()
        self.check_events()

    def create_widgets(self):
        # Title label
        self.title_label = tk.Label(self.root, text="Calendar Reminder", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0,20))

        # Events List Frame
        events_frame = tk.Frame(self.root)
        events_frame.grid(row=1, column=0, sticky="nsew", padx=(0,20))
        events_frame.grid_columnconfigure(0, weight=1)

        self.events_label = tk.Label(events_frame, text="Events:", font=("Arial", 14))
        self.events_label.grid(row=0, column=0, sticky="w", pady=(0,10))

        self.events_listbox = tk.Listbox(events_frame, font=("Arial", 12), height=15, width=50)
        self.events_listbox.grid(row=1, column=0, sticky="nsew", pady=(0,10))

        self.populate_events_listbox()

        # Buttons for event actions
        events_btn_frame = tk.Frame(events_frame)
        events_btn_frame.grid(row=2, column=0, pady=(0,10))
        self.add_event_btn = tk.Button(events_btn_frame, text="Add Event", command=self.add_event, font=("Arial", 12), width=12)
        self.add_event_btn.pack(side=tk.LEFT, padx=5)
        self.edit_event_btn = tk.Button(events_btn_frame, text="Edit Event", command=self.edit_event, font=("Arial", 12), width=12)
        self.edit_event_btn.pack(side=tk.LEFT, padx=5)
        self.delete_event_btn = tk.Button(events_btn_frame, text="Delete Event", command=self.delete_event, font=("Arial", 12), width=12)
        self.delete_event_btn.pack(side=tk.LEFT, padx=5)

        # Info and Log Frame
        info_frame = tk.Frame(self.root)
        info_frame.grid(row=1, column=1, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)

        self.info_label = tk.Label(info_frame, text="Notification Info:\nEvents will send a Telegram message\nwhen the event is near.", font=("Arial", 14))
        self.info_label.grid(row=0, column=0, sticky="w", pady=(0,20))

        self.log_text = tk.Text(info_frame, font=("Arial", 12), height=10, width=40)
        self.log_text.grid(row=1, column=0, sticky="nsew")
        self.log("Calendar app started.")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def populate_events_listbox(self):
        self.events_listbox.delete(0, tk.END)
        for event in self.events:
            dt = datetime.datetime.fromisoformat(event["datetime"])
            line = f"{event['title']} @ {dt.strftime('%d/%m/%Y %H:%M')} (Notify {event['notify_days']} days before)"
            self.events_listbox.insert(tk.END, line)

    def add_event(self):
        # Use the custom dialog to get event details
        dialog = EventDialog(self.root)
        if dialog.result is None:
            return
        details = dialog.result
        try:
            dt = datetime.datetime.strptime(f"{details['date']} {details['hour']}:{details['minute']}", "%d/%m/%Y %H:%M")
        except ValueError:
            messagebox.showerror("Invalid Date/Time", "Please enter the date and time in the correct format.", parent=self.root)
            return
        event = {
            "title": details["title"],
            "datetime": dt.isoformat(),
            "notify_days": details["notify_days"],
            "notified": False
        }
        self.events.append(event)
        self.populate_events_listbox()
        self.save_events()
        self.log(f"Added event: {event['title']} at {dt.strftime('%d/%m/%Y %H:%M')}")

    def edit_event(self):
        selection = self.events_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Event Selected", "Please select an event to edit.", parent=self.root)
            return
        index = selection[0]
        event = self.events[index]
        dt = datetime.datetime.fromisoformat(event["datetime"])
        dialog = EventDialog(
            self.root,
            title=event["title"],
            date_str=dt.strftime("%d/%m/%Y"),
            hour=dt.strftime("%H"),
            minute=dt.strftime("%M"),
            notify_days=str(event["notify_days"])
        )
        if dialog.result is None:
            return
        details = dialog.result
        try:
            new_dt = datetime.datetime.strptime(f"{details['date']} {details['hour']}:{details['minute']}", "%d/%m/%Y %H:%M")
        except ValueError:
            messagebox.showerror("Invalid Date/Time", "Please enter the date and time in the correct format.", parent=self.root)
            return
        event["title"] = details["title"]
        event["datetime"] = new_dt.isoformat()
        event["notify_days"] = details["notify_days"]
        event["notified"] = False
        self.populate_events_listbox()
        self.save_events()
        self.log(f"Edited event: {event['title']} at {new_dt.strftime('%d/%m/%Y %H:%M')}")

    def delete_event(self):
        selection = self.events_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Event Selected", "Please select an event to delete.", parent=self.root)
            return
        index = selection[0]
        event = self.events.pop(index)
        self.populate_events_listbox()
        self.save_events()
        self.log(f"Deleted event: {event['title']}")

    def check_events(self):
        now = datetime.datetime.now()
        for event in self.events:
            event_dt = datetime.datetime.fromisoformat(event["datetime"])
            notify_delta = datetime.timedelta(days=event["notify_days"])
            if not event["notified"] and now >= (event_dt - notify_delta) and now < event_dt:
                text = f"Reminder: Event '{event['title']}' starts at {event_dt.strftime('%d/%m/%Y %H:%M')}."
                send_telegram_message(text)
                event["notified"] = True
                self.log(f"Sent notification for event: {event['title']}")
        self.save_events()
        self.root.after(30000, self.check_events)

    def load_events(self):
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r") as file:
                try:
                    self.events = json.load(file)
                except json.JSONDecodeError:
                    print("Error loading events.")
        else:
            self.events = []

    def save_events(self):
        with open(EVENTS_FILE, "w") as file:
            json.dump(self.events, file, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
