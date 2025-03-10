import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
import datetime
import requests
from tkinter import font as tkfont
from tkcalendar import Calendar

# === CONFIGURATION ===
TELEGRAM_BOT_TOKEN = "XXXX"
TELEGRAM_CHAT_ID = "XXXX"
EVENTS_FILE = "events.json"

# Font configuration
FONTS = {
    "title": ("Victor Mono", 20, "bold"),
    "header": ("Victor Mono", 14, "bold"),
    "normal": ("Victor Mono", 11, "bold"),
    "small": ("Victor Mono", 10, "bold"),
    "tiny": ("Victor Mono", 9, "bold")
}

# Minimal color scheme
COLORS = {
    "primary": "#2196F3",  # Clean blue
    "secondary": "#757575",  # Neutral gray
    "accent": "#FF4081",  # Subtle pink
    "background": "#FFFFFF",
    "card": "#F5F5F5",
    "text": "#212121",
    "text_light": "#757575",
    "success": "#4CAF50",  # Material green
    "warning": "#FFC107",  # Material amber
    "danger": "#F44336",   # Material red
    "border": "#E0E0E0"
}

# Simplified button styles
BUTTON_STYLES = {
    "standard": {
        "bg": COLORS["primary"],
        "fg": "white",
        "font": FONTS["small"],
        "padx": 15,
        "pady": 8,
        "relief": tk.FLAT,
        "bd": 0,
        "borderwidth": 0,
    },
    "success": {
        "bg": COLORS["success"],
        "fg": "white",
        "font": FONTS["small"],
        "padx": 15,
        "pady": 8,
        "relief": tk.FLAT,
        "bd": 0,
    },
    "danger": {
        "bg": COLORS["danger"],
        "fg": "white",
        "font": FONTS["small"],
        "padx": 15,
        "pady": 8,
        "relief": tk.FLAT,
        "bd": 0,
    }
}

def create_rounded_button(parent, **kwargs):
    """Create a button with modern styling"""
    button = tk.Button(parent, **kwargs)
    return button

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

class ModernEventDialog(tk.Toplevel):
    def __init__(self, parent, title="", date_str="", hour="12", minute="00", notify_days="0"):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        
        # Window setup
        self.title("New Event")
        self.configure(bg=COLORS["background"])
        self.geometry("350x450")
        
        # Create main container with padding
        container = tk.Frame(self, bg=COLORS["background"], padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Label(container, 
                         text="New Event",
                         font=FONTS["header"],
                         bg=COLORS["background"],
                         fg=COLORS["text"])
        header.pack(pady=(0, 20), anchor="w")
        
        # Event title
        title_frame = tk.Frame(container, bg=COLORS["background"])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, 
                text="Title",
                font=FONTS["small"],
                bg=COLORS["background"],
                fg=COLORS["text_light"]).pack(anchor="w")
        
        self.title_entry = tk.Entry(title_frame,
                                   font=FONTS["normal"],
                                   bg=COLORS["card"],
                                   fg=COLORS["text"],
                                   relief=tk.FLAT,
                                   highlightthickness=1,
                                   highlightbackground=COLORS["border"])
        self.title_entry.pack(fill=tk.X, pady=(5, 0))
        self.title_entry.insert(0, title)
        
        # Date and time frame
        datetime_frame = tk.Frame(container, bg=COLORS["background"])
        datetime_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date selection
        tk.Label(datetime_frame,
                text="Date",
                font=FONTS["small"],
                bg=COLORS["background"],
                fg=COLORS["text_light"]).pack(anchor="w")
        
        self.date_entry = tk.Entry(datetime_frame,
                                  font=FONTS["normal"],
                                  bg=COLORS["card"],
                                  fg=COLORS["text"],
                                  relief=tk.FLAT,
                                  highlightthickness=1,
                                  highlightbackground=COLORS["border"])
        self.date_entry.pack(fill=tk.X, pady=(5, 10))
        self.date_entry.insert(0, date_str if date_str else datetime.datetime.now().strftime("%d/%m/%Y"))
        
        # Time selection
        time_label_frame = tk.Frame(datetime_frame, bg=COLORS["background"])
        time_label_frame.pack(fill=tk.X)
        
        tk.Label(time_label_frame,
                text="Time",
                font=FONTS["small"],
                bg=COLORS["background"],
                fg=COLORS["text_light"]).pack(side=tk.LEFT)
        
        time_frame = tk.Frame(datetime_frame, bg=COLORS["background"])
        time_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Hour selection
        self.hour_var = tk.StringVar(value=hour)
        hours = [f"{h:02d}" for h in range(24)]
        hour_menu = ttk.Combobox(time_frame,
                                textvariable=self.hour_var,
                                values=hours,
                                width=5,
                                state="readonly",
                                font=FONTS["normal"])
        hour_menu.pack(side=tk.LEFT)
        
        tk.Label(time_frame,
                text=":",
                font=FONTS["normal"],
                bg=COLORS["background"],
                fg=COLORS["text"]).pack(side=tk.LEFT, padx=5)
        
        # Minute selection
        self.minute_var = tk.StringVar(value=minute)
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        minute_menu = ttk.Combobox(time_frame,
                                  textvariable=self.minute_var,
                                  values=minutes,
                                  width=5,
                                  state="readonly",
                                  font=FONTS["normal"])
        minute_menu.pack(side=tk.LEFT)
        
        # Notification frame
        notify_frame = tk.Frame(container, bg=COLORS["background"])
        notify_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(notify_frame,
                text="Reminder",
                font=FONTS["small"],
                bg=COLORS["background"],
                fg=COLORS["text_light"]).pack(anchor="w")
        
        self.notify_var = tk.StringVar(value=notify_days)
        days = [str(d) for d in range(8)]
        notify_menu = ttk.Combobox(notify_frame,
                                  textvariable=self.notify_var,
                                  values=days,
                                  width=5,
                                  state="readonly",
                                  font=FONTS["normal"])
        notify_menu.pack(side=tk.LEFT, pady=(5, 0))
        
        tk.Label(notify_frame,
                text="days before",
                font=FONTS["small"],
                bg=COLORS["background"],
                fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=(5, 0), pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(container, bg=COLORS["background"])
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        cancel_btn = create_rounded_button(
            button_frame,
            text="Cancel",
            command=self.on_cancel,
            **BUTTON_STYLES["danger"]
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = create_rounded_button(
            button_frame,
            text="Save",
            command=self.on_ok,
            **BUTTON_STYLES["success"]
        )
        save_btn.pack(side=tk.LEFT)
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.result = None
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
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

# Add font loading code after imports
def load_fonts():
    """Load Victor Mono font family"""
    try:
        # Try to load the font to verify it's available
        test_font = tkfont.Font(family="Victor Mono")
        print("Victor Mono font loaded successfully")
    except Exception as e:
        print("Warning: Victor Mono font not found. Please install the font.")
        # Fallback to system fonts
        FONTS.update({
            "title": ("Helvetica", 20, "bold"),
            "header": ("Helvetica", 14, "bold"),
            "normal": ("Helvetica", 11, "normal"),
            "small": ("Helvetica", 10, "normal"),
            "tiny": ("Helvetica", 9, "normal")
        })

class ModernCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar")
        self.root.geometry("1000x600")
        self.root.configure(bg=COLORS["background"])
        
        # Load fonts
        load_fonts()
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Modern.Treeview",
                           background=COLORS["card"],
                           foreground=COLORS["text"],
                           fieldbackground=COLORS["card"],
                           borderwidth=0,
                           font=FONTS["normal"])
        self.style.configure("Modern.Treeview.Heading",
                           background=COLORS["background"],
                           foreground=COLORS["text"],
                           borderwidth=0,
                           font=FONTS["small"])
        
        # Load events
        self.events = []
        self.load_events()
        
        # Create UI
        self.create_widgets()
        
        # Update calendar markers after widgets are created
        self.update_calendar_markers()
        
        # Start event checking
        self.check_events()

    def create_widgets(self):
        # Main container
        container = tk.Frame(self.root, bg=COLORS["background"], padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Create a frame for the left and right sections
        main_frame = tk.Frame(container, bg=COLORS["background"])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Events
        left_panel = tk.Frame(main_frame, bg=COLORS["background"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        # Events panel (top part of left panel)
        events_panel = tk.Frame(left_panel, bg=COLORS["card"])
        events_panel.pack(fill=tk.BOTH, expand=True)

        # Events header
        events_header = tk.Frame(events_panel, bg=COLORS["background"], padx=15, pady=10)
        events_header.pack(fill=tk.X)

        tk.Label(events_header,
                text="Events",
                font=FONTS["header"],
                bg=COLORS["background"],
                fg=COLORS["text"]).pack(side=tk.LEFT)

        # Events list
        self.events_tree = ttk.Treeview(events_panel,
                                     columns=("title", "date", "time", "notify"),
                                     show="headings",
                                     style="Modern.Treeview")

        # Configure columns
        self.events_tree.heading("title", text="Title")
        self.events_tree.heading("date", text="Date")
        self.events_tree.heading("time", text="Time")
        self.events_tree.heading("notify", text="Reminder")

        self.events_tree.column("title", width=200)
        self.events_tree.column("date", width=100)
        self.events_tree.column("time", width=80)
        self.events_tree.column("notify", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(events_panel, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)

        self.events_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=15)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 15))

        # Action buttons below events panel
        buttons_frame = tk.Frame(left_panel, bg=COLORS["background"], pady=15)
        buttons_frame.pack(fill=tk.X)

        add_btn = create_rounded_button(
            buttons_frame,
            text="Add Event",
            command=self.add_event,
            **BUTTON_STYLES["success"]
        )
        add_btn.pack(side=tk.LEFT, padx=5)

        edit_btn = create_rounded_button(
            buttons_frame,
            text="Edit",
            command=self.edit_event,
            **BUTTON_STYLES["standard"]
        )
        edit_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = create_rounded_button(
            buttons_frame,
            text="Delete",
            command=self.delete_event,
            **BUTTON_STYLES["danger"]
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

        # Right panel - Calendar
        right_panel = tk.Frame(main_frame, bg=COLORS["card"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Calendar header
        calendar_header = tk.Frame(right_panel, bg=COLORS["background"], padx=15, pady=10)
        calendar_header.pack(fill=tk.X)

        tk.Label(calendar_header,
                text="Calendar",
                font=FONTS["header"],
                bg=COLORS["background"],
                fg=COLORS["text"]).pack(side=tk.LEFT)

        # Calendar widget
        self.calendar = Calendar(right_panel,
                             selectmode='day',
                             year=datetime.datetime.now().year,
                             month=datetime.datetime.now().month,
                             day=datetime.datetime.now().day,
                             background=COLORS["background"],
                             foreground=COLORS["text"],
                             bordercolor=COLORS["border"],
                             headersbackground=COLORS["background"],
                             headersforeground=COLORS["text"],
                             selectbackground=COLORS["primary"],
                             normalbackground=COLORS["card"],
                             weekendbackground=COLORS["card"],
                             othermonthbackground=COLORS["background"],
                             othermonthforeground=COLORS["text_light"],
                             font=FONTS["normal"],
                             showothermonthdays=False,
                             showweeknumbers=False,
                             markwidth=1)  # Make the marker small

        self.calendar.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Activity log
        log_frame = tk.Frame(right_panel, bg=COLORS["card"])
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_header = tk.Frame(log_frame, bg=COLORS["background"], padx=15, pady=10)
        log_header.pack(fill=tk.X)

        tk.Label(log_header,
                  text="Activity",
                  font=FONTS["header"],
                  bg=COLORS["background"],
                  fg=COLORS["text"]).pack(side=tk.LEFT)

        # Log text area
        self.log_text = tk.Text(log_frame,
                                 font=FONTS["small"],
                                 bg=COLORS["card"],
                                 fg=COLORS["text"],
                                 height=8,
                                 padx=15,
                                 pady=10,
                                 relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        status_frame = tk.Frame(container, bg=COLORS["background"], pady=10)
        status_frame.pack(fill=tk.X)

        status_label = tk.Label(status_frame,
                                 text="Telegram notifications enabled",
                                 font=FONTS["tiny"],
                                 bg=COLORS["background"],
                                 fg=COLORS["text_light"])
        status_label.pack(side=tk.LEFT)

        # Initialize
        self.populate_events_tree()
        self.log("Welcome to Calendar! ✨")

        # Bind events
        self.events_tree.bind("<Double-1>", lambda e: self.edit_event())
        self.calendar.bind("<<CalendarSelected>>", self.filter_events_by_date)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)

    def populate_events_tree(self):
        self.events_tree.delete(*self.events_tree.get_children())
        for event in self.events:
            dt = datetime.datetime.fromisoformat(event["datetime"])
            self.events_tree.insert("", tk.END,
                                  values=(
                                      event["title"],
                                      dt.strftime("%d/%m/%Y"),
                                      dt.strftime("%H:%M"),
                                      f"{event['notify_days']} days before"
                                  ))

    def update_calendar_markers(self):
        """Update the calendar to show dots on days with events"""
        # Clear existing markers
        self.calendar.calevent_remove('all')
        
        # Add markers for each event
        for event in self.events:
            dt = datetime.datetime.fromisoformat(event["datetime"])
            self.calendar.calevent_create(dt.date(), event["title"], 'event')  # Create event marker
        
        # Configure the marker appearance to show a small dot below the date
        self.calendar.tag_config('event', 
                               background=COLORS["background"],
                               foreground=COLORS["text"],
                               markbackground=COLORS["primary"],
                               markheight=4,  # Small height for the dot
                               markwidth=4,   # Small width for the dot
                               justify='center')

    def add_event(self):
        dialog = ModernEventDialog(self.root)
        if dialog.result:
            try:
                dt = datetime.datetime.strptime(
                    f"{dialog.result['date']} {dialog.result['hour']}:{dialog.result['minute']}",
                    "%d/%m/%Y %H:%M"
                )
                event = {
                    "title": dialog.result["title"],
                    "datetime": dt.isoformat(),
                    "notify_days": dialog.result["notify_days"],
                    "notified": False
                }
                self.events.append(event)
                self.populate_events_tree()
                self.save_events()
                self.update_calendar_markers()  # Update calendar markers
                self.log(f"✨ Added new event: {event['title']}")
            except ValueError:
                messagebox.showerror("Error", "Invalid date or time format")

    def edit_event(self):
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an event to edit")
            return
        
        item = selection[0]
        index = self.events_tree.index(item)
        event = self.events[index]
        dt = datetime.datetime.fromisoformat(event["datetime"])
        
        dialog = ModernEventDialog(
            self.root,
            title=event["title"],
            date_str=dt.strftime("%d/%m/%Y"),
            hour=dt.strftime("%H"),
            minute=dt.strftime("%M"),
            notify_days=str(event["notify_days"])
        )
        
        if dialog.result:
            try:
                new_dt = datetime.datetime.strptime(
                    f"{dialog.result['date']} {dialog.result['hour']}:{dialog.result['minute']}",
                    "%d/%m/%Y %H:%M"
                )
                event.update({
                    "title": dialog.result["title"],
                    "datetime": new_dt.isoformat(),
                    "notify_days": dialog.result["notify_days"],
                    "notified": False
                })
                self.populate_events_tree()
                self.save_events()
                self.update_calendar_markers()  # Update calendar markers
                self.log(f"✏️ Updated event: {event['title']}")
            except ValueError:
                messagebox.showerror("Error", "Invalid date or time format")

    def delete_event(self):
        selection = self.events_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an event to delete")
            return
        
        item = selection[0]
        index = self.events_tree.index(item)
        event = self.events[index]
        
        if messagebox.askyesno("Confirm Delete", f"Delete event '{event['title']}'?"):
            self.events.pop(index)
            self.populate_events_tree()
            self.save_events()
            self.update_calendar_markers()  # Update calendar markers
            self.log(f"🗑️ Deleted event: {event['title']}")

    def filter_events_by_date(self, event=None):
        selected_date = self.calendar.get_date()
        date_obj = datetime.datetime.strptime(selected_date, "%m/%d/%y")
        formatted_date = date_obj.strftime("%d/%m/%Y")
        
        self.events_tree.delete(*self.events_tree.get_children())
        for event in self.events:
            dt = datetime.datetime.fromisoformat(event["datetime"])
            if dt.strftime("%d/%m/%Y") == formatted_date:
                self.events_tree.insert("", tk.END,
                                      values=(
                                          event["title"],
                                          dt.strftime("%d/%m/%Y"),
                                          dt.strftime("%H:%M"),
                                          f"{event['notify_days']} days before"
                                      ))
        
        self.log(f"🔍 Filtered events for {formatted_date}")

    def check_events(self):
        now = datetime.datetime.now()
        for event in self.events:
            dt = datetime.datetime.fromisoformat(event["datetime"])
            notify_time = dt - datetime.timedelta(days=event["notify_days"])
            if not event["notified"] and now >= notify_time and now < dt:
                text = f"🔔 Reminder: '{event['title']}' starts at {dt.strftime('%d/%m/%Y %H:%M')}"
                send_telegram_message(text)
                event["notified"] = True
                self.log(f"📱 Sent notification for: {event['title']}")
        
        self.save_events()
        self.root.after(30000, self.check_events)

    def load_events(self):
        if os.path.exists(EVENTS_FILE):
            try:
                with open(EVENTS_FILE, "r") as f:
                    self.events = json.load(f)
            except json.JSONDecodeError:
                self.events = []
        else:
            self.events = []

    def save_events(self):
        with open(EVENTS_FILE, "w") as f:
            json.dump(self.events, f, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernCalendarApp(root)
    root.mainloop()