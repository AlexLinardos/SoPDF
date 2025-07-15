"""
SoPDF Main Application

This is the main application class that coordinates all the UI modules.
"""

import os
import sys
import json
from typing import Optional, Any

# Import lazy UI utilities instead of direct imports
from src.utils.lazy_ui import ctk, tk, pil, lazy_tabs
from src.utils.file_utils import get_asset_path


class SoPDFApp:
    """Main SoPDF Application class"""
    
    def __init__(self):
        # Don't configure Custom Tkinter here - it will be done lazily
        
        # Create main window using lazy loader
        self.root = ctk.CTk()
        self.root.title("SoPDF")
        
        # Get screen dimensions for responsive sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set more reasonable minimum size for smaller screens
        min_width = min(800, int(screen_width * 0.6))
        min_height = min(600, int(screen_height * 0.6))
        self.root.minsize(min_width, min_height)
        
        # Load saved window state or use defaults
        self.load_window_state(screen_width, screen_height)
        
        # Set window icon
        self.setup_window_icon()
        
        # Configure grid weight for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize tab references - these will be loaded lazily
        self.organize_tab_instance = None
        self.merge_tab_instance = None
        self.split_tab_instance = None
        
        # Initialize page organization variables (needed by organize tab)
        self.organize_page_order = []
        self.removed_pages = set()
        self.page_thumbnails = []
        self.drag_data = {"x": 0, "y": 0, "item": None}
        
        # Setup UI and restore window state
        self.setup_ui()
        self.restore_window_state()
        
        # Bind window close event to save state
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
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
                    png_image = pil.Image.open(png_path)
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
        """Setup the main user interface with lazy tab loading"""
        # Create tabview directly in root (no extra container needed)
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Add tabs but don't initialize their content yet
        organize_tab_frame = self.tabview.add("Organize")
        merge_tab_frame = self.tabview.add("Merge")
        split_tab_frame = self.tabview.add("Split")
        
        # Register tabs for lazy loading
        lazy_tabs.set_app_reference(self)
        
        # Import tab classes only when registering (not when creating instances)
        from src.ui.organize_tab import OrganizeTab
        from src.ui.merge_tab import MergeTab
        from src.ui.split_tab import SplitTab
        
        lazy_tabs.register_tab("Organize", OrganizeTab, organize_tab_frame)
        lazy_tabs.register_tab("Merge", MergeTab, merge_tab_frame)
        lazy_tabs.register_tab("Split", SplitTab, split_tab_frame)
        
        # Bind tab change event to handle lazy loading
        self.tabview.configure(command=self.on_tab_change)
        
        # Load the default tab (Organize) immediately for better UX
        self.load_tab_if_needed("Organize")
    
    def on_tab_change(self):
        """Handle tab change events to load tabs lazily"""
        current_tab = self.tabview.get()
        self.load_tab_if_needed(current_tab)
    
    def load_tab_if_needed(self, tab_name: str):
        """Load a tab's content if it hasn't been loaded yet"""
        if not lazy_tabs.is_tab_loaded(tab_name):
            # Load the tab content
            tab_instance = lazy_tabs.get_tab(tab_name)
            
            # Store references for backwards compatibility
            if tab_name == "Organize":
                self.organize_tab_instance = tab_instance
            elif tab_name == "Merge":
                self.merge_tab_instance = tab_instance
            elif tab_name == "Split":
                self.split_tab_instance = tab_instance
    
    # Methods needed by organize tab for backwards compatibility
    def select_thumbnail(self, thumbnail):
        """Select a thumbnail (called by organize tab)"""
        if self.organize_tab_instance:
            self.organize_tab_instance.select_thumbnail(thumbnail)
    
    def restore_specific_page(self, page_index):
        """Restore a specific page (called by organize tab)"""
        if self.organize_tab_instance:
            self.organize_tab_instance.restore_specific_page(page_index)
    
    def remove_specific_page(self, page_index):
        """Remove a specific page (called by organize tab)"""
        if self.organize_tab_instance:
            self.organize_tab_instance.remove_specific_page(page_index)
    
    def move_page_to_position(self, source_index, target_index):
        """Move a page to a new position (called by organize tab)"""
        if self.organize_tab_instance:
            self.organize_tab_instance.move_page_to_position(source_index, target_index)
    
    def run(self):
        """Start the application"""
        # Window state is already restored in __init__
        
        # Start the main loop
        self.root.mainloop()
    
    def get_state_file_path(self):
        """Get the path to the state file"""
        # Create a config directory in the user's home directory
        config_dir = os.path.join(os.path.expanduser("~"), ".sopdf")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "window_state.json")
    
    def load_window_state(self, screen_width, screen_height):
        """Load window state from file or use defaults"""
        self.window_state = {
            "maximized": True,  # Default to maximized
            "width": min(1200, int(screen_width * 0.8)),
            "height": min(900, int(screen_height * 0.8)),
            "x": None,  # Will be calculated for centering
            "y": None,  # Will be calculated for centering
            "organize_preview_mode": False  # Default preview mode state
        }
        
        state_file = self.get_state_file_path()
        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    saved_state = json.load(f)
                    # Update with saved values, keeping defaults for missing keys
                    self.window_state.update(saved_state)
        except Exception as e:
            print(f"Could not load window state: {e}")
    
    def save_window_state(self):
        """Save current window state to file"""
        try:
            # Get current window state
            current_state = {
                "maximized": self.root.state() == 'zoomed',
                "width": self.root.winfo_width(),
                "height": self.root.winfo_height(),
                "x": self.root.winfo_x(),
                "y": self.root.winfo_y(),
                "organize_preview_mode": getattr(self.organize_tab_instance, 'preview_mode', False) if self.organize_tab_instance else False
            }
            
            state_file = self.get_state_file_path()
            with open(state_file, 'w') as f:
                json.dump(current_state, f, indent=2)
        except Exception as e:
            print(f"Could not save window state: {e}")
    
    def restore_window_state(self):
        """Restore window state after UI is set up"""
        try:
            if self.window_state["maximized"]:
                # If it was maximized, maximize it
                self.root.after(100, lambda: self.root.state('zoomed'))
            else:
                # If it wasn't maximized, set the saved geometry
                width = self.window_state["width"]
                height = self.window_state["height"]
                x = self.window_state["x"]
                y = self.window_state["y"]
                
                # If position wasn't saved, center the window
                if x is None or y is None:
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    x = (screen_width // 2) - (width // 2)
                    y = (screen_height // 2) - (height // 2)
                
                self.root.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"Could not restore window state: {e}")
            # Fallback to centering
            self.center_window()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_closing(self):
        """Handle window closing - save state before destroying"""
        self.save_window_state()
        self.root.destroy()


def main():
    """Main entry point"""
    try:
        app = SoPDFApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        # Import messagebox only when needed
        from tkinter import messagebox
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 