"""
First-launch setup wizard for API credentials

Provides a GUI for users to enter their Ambient Weather API credentials
on first launch of the packaged application.
"""

import tkinter as tk
import webbrowser
from tkinter import messagebox

from weather_app.config import BASE_DIR, ENV_FILE


class SetupWizard:
    """GUI wizard for initial Weather App setup"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather App Setup")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.api_key_var = tk.StringVar()
        self.app_key_var = tk.StringVar()

        self.create_ui()

    def create_ui(self):
        """Create setup wizard UI"""
        # Title
        title = tk.Label(
            self.root, text="Welcome to Weather App!", font=("Arial", 18, "bold")
        )
        title.pack(pady=20)

        # Instructions
        instructions = tk.Label(
            self.root,
            text="Please enter your Ambient Weather API credentials.\n"
            "You can find these at: ambientweather.net/account",
            font=("Arial", 10),
            justify=tk.LEFT,
        )
        instructions.pack(pady=10)

        # API Key field
        api_frame = tk.Frame(self.root)
        api_frame.pack(pady=10, padx=40, fill=tk.X)

        tk.Label(api_frame, text="API Key:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W
        )
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=50)
        api_entry.pack(fill=tk.X, pady=5)

        # Application Key field
        app_frame = tk.Frame(self.root)
        app_frame.pack(pady=10, padx=40, fill=tk.X)

        tk.Label(app_frame, text="Application Key:", font=("Arial", 10, "bold")).pack(
            anchor=tk.W
        )
        app_entry = tk.Entry(app_frame, textvariable=self.app_key_var, width=50)
        app_entry.pack(fill=tk.X, pady=5)

        # Help link
        help_text = tk.Label(
            self.root,
            text="Need help getting your API keys?",
            font=("Arial", 9),
            fg="blue",
            cursor="hand2",
        )
        help_text.pack(pady=5)
        help_text.bind("<Button-1>", lambda e: self.open_help())

        # Additional info
        info_text = tk.Label(
            self.root,
            text="Don't have an Ambient Weather station?\nVisit ambientweather.com to learn more.",
            font=("Arial", 8),
            fg="gray",
        )
        info_text.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        save_btn = tk.Button(
            btn_frame,
            text="Save & Continue",
            command=self.save_credentials,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
        )
        save_btn.pack(side=tk.LEFT, padx=10)

        quit_btn = tk.Button(
            btn_frame,
            text="Quit",
            command=self.quit_wizard,
            font=("Arial", 10),
            padx=20,
            pady=10,
        )
        quit_btn.pack(side=tk.LEFT, padx=10)

    def save_credentials(self):
        """Save credentials to .env file"""
        api_key = self.api_key_var.get().strip()
        app_key = self.app_key_var.get().strip()

        if not api_key or not app_key:
            messagebox.showerror(
                "Error", "Please enter both API Key and Application Key"
            )
            return

        # Create .env file in user data directory
        env_content = f"""# Ambient Weather API Credentials
AMBIENT_API_KEY={api_key}
AMBIENT_APP_KEY={app_key}

# Scheduler Configuration
SCHEDULER_ENABLED=true
SCHEDULER_FETCH_INTERVAL_MINUTES=5

# Server Configuration
BIND_HOST=127.0.0.1
BIND_PORT=8000

# Logging
LOG_LEVEL=INFO
"""

        try:
            # Ensure BASE_DIR exists
            BASE_DIR.mkdir(parents=True, exist_ok=True)

            # Write .env file
            ENV_FILE.write_text(env_content, encoding="utf-8")

            messagebox.showinfo(
                "Success",
                "Credentials saved successfully!\n\n"
                "The Weather App will now start and begin collecting data.\n\n"
                "Click the system tray icon to open your dashboard.",
            )
            self.root.quit()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save credentials:\n{str(e)}\n\n"
                f"Please check that the application has write access to:\n{ENV_FILE}",
            )

    def quit_wizard(self):
        """Quit the wizard without saving"""
        result = messagebox.askyesno(
            "Quit Setup",
            "Are you sure you want to quit?\n\n"
            "The Weather App requires API credentials to function.",
        )
        if result:
            self.root.quit()

    def open_help(self):
        """Open help URL in browser"""
        webbrowser.open("https://ambientweather.net/account")

    def run(self):
        """Run setup wizard and return whether setup was completed"""
        self.root.mainloop()
        # Check if .env file was created
        return ENV_FILE.exists()


def needs_setup() -> bool:
    """
    Check if setup wizard needs to be run.

    Returns:
        bool: True if .env file doesn't exist, False otherwise
    """
    return not ENV_FILE.exists()


def run_setup() -> bool:
    """
    Run setup wizard if needed.

    Returns:
        bool: True if setup completed successfully or not needed, False if user quit
    """
    if needs_setup():
        wizard = SetupWizard()
        result: bool = wizard.run()
        return result
    return True
