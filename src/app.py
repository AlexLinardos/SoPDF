"""
SoPDF Main Application

This is the main application class that coordinates all the UI modules.
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

# Import our modular components
from src.ui.organize_tab import OrganizeTab
from src.ui.merge_tab import MergeTab
from src.ui.split_tab import SplitTab
from src.utils.file_utils import get_asset_path


class SoPDFApp:
    """Main SoPDF Application class"""
    
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")  # "light" or "dark" or "system"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("SoPDF")
        
        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive window size (80% of screen, but with reasonable limits)
        window_width = min(1200, int(screen_width * 0.8))
        window_height = min(900, int(screen_height * 0.8))
        
        # Set more reasonable minimum size for smaller screens
        min_width = min(800, int(screen_width * 0.6))
        min_height = min(600, int(screen_height * 0.6))
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(min_width, min_height)
        
        # Set window icon
        self.setup_window_icon()
        
        # Configure grid weight for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize tab references
        self.organize_tab_instance = None
        self.merge_tab_instance = None
        self.split_tab_instance = None
        
        self.setup_ui()
    
    def setup_window_icon(self):
        """Setup the window icon using assets from the assets directory"""
        try:
            # Try to use the existing ICO file
            ico_path = get_asset_path("SoPDF_icon.ico")
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
                return
            
            # Fallback: try to create ICO from PNG
            png_path = get_asset_path("SoPDF_logo_trans.png")
            if os.path.exists(png_path):
                try:
                    # Convert PNG to ICO if ICO doesn't exist
                    png_image = Image.open(png_path)
                    # Resize to standard icon sizes and save as ICO
                    png_image.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
                    print("Created ICO file from PNG")
                    self.root.iconbitmap(ico_path)
                    return
                except Exception as e:
                    print(f"Could not create ICO file: {e}")
                
                # Fallback to PhotoImage method
                icon_image = tk.PhotoImage(file=png_path)
                self.root.iconphoto(True, icon_image)
            
        except Exception as e:
            print(f"Could not set window icon: {e}")
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create tabview directly in root (no extra container needed)
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Add tabs
        organize_tab_frame = self.tabview.add("Organize")
        merge_tab_frame = self.tabview.add("Merge")
        split_tab_frame = self.tabview.add("Split")
        
        # Setup individual tabs using the modular classes
        self.organize_tab_instance = OrganizeTab(organize_tab_frame, self)
        self.merge_tab_instance = MergeTab(merge_tab_frame, self)
        self.split_tab_instance = SplitTab(split_tab_frame, self)
    

    
    def run(self):
        """Start the application"""
        # Center the window on screen
        self.center_window()
        
        # Start the main loop
        self.root.mainloop()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """Main entry point"""
    try:
        app = SoPDFApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 