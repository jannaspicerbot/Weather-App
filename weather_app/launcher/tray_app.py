"""
System tray application for Weather App

Manages the FastAPI server in the background and provides a system tray
icon with menu options for user interaction.
"""

import sys
import threading
import webbrowser
from pathlib import Path
import logging

# Note: pystray and PIL will be imported dynamically to handle missing dependencies gracefully
from weather_app.config import PORT, BASE_DIR
from weather_app.launcher.setup_wizard import run_setup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherTrayApp:
    """System tray application for Weather App"""

    def __init__(self):
        self.server_thread = None
        self.server = None
        self.icon = None

    def start_server(self):
        """Start FastAPI server in background thread"""
        try:
            import uvicorn
            from weather_app.web.app import create_app

            logger.info("Starting FastAPI server...")
            app = create_app()
            config = uvicorn.Config(
                app,
                host="127.0.0.1",
                port=PORT,
                log_level="info",
                access_log=False  # Reduce console noise
            )
            self.server = uvicorn.Server(config)
            self.server_thread = threading.Thread(target=self.server.run, daemon=True)
            self.server_thread.start()
            logger.info(f"Server started on http://127.0.0.1:{PORT}")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise

    def stop_server(self):
        """Stop FastAPI server"""
        if self.server:
            logger.info("Stopping FastAPI server...")
            self.server.should_exit = True
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)

    def open_dashboard(self, icon=None, item=None):
        """Open web dashboard in default browser"""
        try:
            url = f'http://localhost:{PORT}'
            logger.info(f"Opening dashboard: {url}")
            webbrowser.open(url)
        except Exception as e:
            logger.error(f"Failed to open dashboard: {e}")

    def open_data_folder(self, icon=None, item=None):
        """Open user data folder in file explorer"""
        try:
            import subprocess
            import platform

            data_path = str(BASE_DIR)
            logger.info(f"Opening data folder: {data_path}")

            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', data_path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', data_path])
            else:  # Linux
                subprocess.Popen(['xdg-open', data_path])
        except Exception as e:
            logger.error(f"Failed to open data folder: {e}")

    def restart_app(self, icon=None, item=None):
        """Restart the application"""
        logger.info("Restarting application...")
        self.quit_app(icon, item, restart=True)

    def quit_app(self, icon=None, item=None, restart=False):
        """Quit application"""
        logger.info("Shutting down...")
        self.stop_server()

        if self.icon:
            self.icon.stop()

        if restart:
            # Restart the application
            import os
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            sys.exit(0)

    def create_icon_image(self):
        """
        Create a simple icon image for the system tray.

        Returns a PIL Image object. For now, creates a simple colored square.
        In production, this should use a proper icon file.
        """
        from PIL import Image, ImageDraw

        # Create a simple 64x64 icon with a weather theme
        # Blue background with white cloud-like shape
        size = 64
        image = Image.new('RGB', (size, size), color='#2196F3')  # Blue background

        draw = ImageDraw.Draw(image)
        # Draw a simple cloud shape (series of circles)
        white = '#FFFFFF'
        # Left circle
        draw.ellipse([10, 25, 30, 45], fill=white)
        # Middle circle (larger)
        draw.ellipse([20, 15, 45, 40], fill=white)
        # Right circle
        draw.ellipse([35, 25, 55, 45], fill=white)
        # Bottom rectangle to connect
        draw.rectangle([10, 35, 55, 45], fill=white)

        return image

    def load_icon_image(self):
        """
        Load icon image from file or create a default one.

        Returns:
            PIL.Image: Icon image
        """
        icon_path = Path(__file__).parent / 'icon.png'

        if icon_path.exists():
            try:
                from PIL import Image
                return Image.open(icon_path)
            except Exception as e:
                logger.warning(f"Failed to load icon from {icon_path}: {e}")

        # Fallback to generated icon
        return self.create_icon_image()

    def run(self):
        """Run system tray application"""
        try:
            import pystray
            from PIL import Image
        except ImportError as e:
            logger.error(
                f"Missing required dependency: {e}\n"
                "Please install: pip install pystray Pillow"
            )
            sys.exit(1)

        # Load icon image
        image = self.load_icon_image()

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem('Open Dashboard', self.open_dashboard, default=True),
            pystray.MenuItem('Open Data Folder', self.open_data_folder),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Restart', self.restart_app),
            pystray.MenuItem('Quit', self.quit_app)
        )

        # Create tray icon
        self.icon = pystray.Icon('weather_app', image, 'Weather App', menu)

        # Start server in background
        try:
            self.start_server()
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            sys.exit(1)

        # Auto-open dashboard on first start
        try:
            import time
            time.sleep(2)  # Wait for server to fully start
            self.open_dashboard()
        except Exception as e:
            logger.warning(f"Failed to auto-open dashboard: {e}")

        # Run tray icon (blocks until quit)
        logger.info("System tray app running...")
        self.icon.run()


def main():
    """Main entry point for the tray application"""
    logger.info("Starting Weather App...")

    # Run setup wizard if needed
    if not run_setup():
        logger.info("Setup cancelled by user")
        sys.exit(0)

    # Start tray app
    app = WeatherTrayApp()
    app.run()


if __name__ == '__main__':
    main()
