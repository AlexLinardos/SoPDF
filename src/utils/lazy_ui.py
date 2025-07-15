"""
Lazy UI Loading Utilities

This module provides lazy loading capabilities for UI components to improve startup times.
"""

import importlib
from typing import Optional, Any


class LazyCustomTkinter:
    """Lazy loader for CustomTkinter that defers import until first use"""
    
    def __init__(self):
        self._ctk = None
        self._configured = False
    
    def _ensure_loaded(self) -> Any:
        """Ensure Custom Tkinter is loaded and return the module"""
        if self._ctk is None:
            self._ctk = importlib.import_module('customtkinter')
            self._configure_defaults()
        return self._ctk
    
    def _configure_defaults(self):
        """Configure default settings for Custom Tkinter"""
        if not self._configured:
            self._ctk.set_appearance_mode("dark")  # "light" or "dark" or "system"
            self._ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
            self._configured = True
    
    def __getattr__(self, name: str) -> Any:
        """Dynamically get attributes from Custom Tkinter module"""
        ctk = self._ensure_loaded()
        return getattr(ctk, name)


class LazyTkinter:
    """Lazy loader for standard Tkinter components"""
    
    def __init__(self):
        self._tk = None
    
    def _ensure_loaded(self) -> Any:
        """Ensure Tkinter is loaded and return the module"""
        if self._tk is None:
            self._tk = importlib.import_module('tkinter')
        return self._tk
    
    def __getattr__(self, name: str) -> Any:
        """Dynamically get attributes from Tkinter module"""
        tk = self._ensure_loaded()
        return getattr(tk, name)


class LazyPIL:
    """Lazy loader for PIL/Pillow components"""
    
    def __init__(self):
        self._pil_image = None
    
    def _ensure_image_loaded(self) -> Any:
        """Ensure PIL Image is loaded and return the module"""
        if self._pil_image is None:
            self._pil_image = importlib.import_module('PIL.Image')
        return self._pil_image
    
    @property
    def Image(self) -> Any:
        """Get PIL Image module with lazy loading"""
        return self._ensure_image_loaded()


# Global lazy loaders - these will be imported by other modules
ctk = LazyCustomTkinter()
tk = LazyTkinter()
pil = LazyPIL()


class LazyTabManager:
    """Manages lazy initialization of tabs"""
    
    def __init__(self):
        self._tabs = {}
        self._tab_classes = {}
        self._tab_frames = {}
        self._app_reference = None
    
    def register_tab(self, tab_name: str, tab_class: type, tab_frame: Any):
        """Register a tab for lazy initialization"""
        self._tab_classes[tab_name] = tab_class
        self._tab_frames[tab_name] = tab_frame
    
    def set_app_reference(self, app_reference: Any):
        """Set the main app reference for tabs"""
        self._app_reference = app_reference
    
    def get_tab(self, tab_name: str) -> Any:
        """Get a tab instance, creating it lazily if needed"""
        if tab_name not in self._tabs:
            if tab_name in self._tab_classes:
                # Dynamically import the tab class and create instance
                tab_class = self._tab_classes[tab_name]
                tab_frame = self._tab_frames[tab_name]
                self._tabs[tab_name] = tab_class(tab_frame, self._app_reference)
            else:
                raise ValueError(f"Tab '{tab_name}' not registered")
        return self._tabs[tab_name]
    
    def is_tab_loaded(self, tab_name: str) -> bool:
        """Check if a tab has been loaded"""
        return tab_name in self._tabs


# Global lazy tab manager
lazy_tabs = LazyTabManager() 