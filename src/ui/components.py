"""
UI Components for SoPDF

This module contains reusable UI components like thumbnails and widgets.
"""

# Use lazy loading for UI libraries
from src.utils.lazy_ui import ctk, tk, pil


class PageThumbnail(ctk.CTkFrame):
    """Visual page thumbnail widget with drag-and-drop functionality"""
    
    def __init__(self, parent, page_image, page_index, original_page_num, app_reference, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.app = app_reference
        self.page_index = page_index
        self.original_page_num = original_page_num
        self.is_removed = False
        self.is_selected = False
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Create thumbnail image
        thumbnail_size = (120, 160)
        page_image.thumbnail(thumbnail_size, pil.Image.Resampling.LANCZOS)
        
        # Convert to CTkImage
        self.tk_image = ctk.CTkImage(light_image=page_image, dark_image=page_image, size=thumbnail_size)
        
        # Image label
        self.image_label = ctk.CTkLabel(
            self,
            image=self.tk_image,
            text="",
            corner_radius=8
        )
        self.image_label.grid(row=0, column=0, padx=5, pady=(5, 2), sticky="ew")
        
        # Page info label
        current_pos = self.app.organize_page_order.index(page_index) + 1 if page_index in self.app.organize_page_order else "?"
        self.info_label = ctk.CTkLabel(
            self,
            text=f"Page {current_pos}\n(orig. {original_page_num})",
            font=ctk.CTkFont(size=11),
            height=30
        )
        self.info_label.grid(row=1, column=0, padx=5, pady=(2, 5), sticky="ew")
        
        # Bind events for selection and drag-and-drop
        self.bind("<Button-1>", self.on_click)
        self.bind("<Button-3>", self.on_right_click)  # Right-click for context menu
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        
        # Bind events to child widgets too
        self.image_label.bind("<Button-1>", self.on_click)
        self.image_label.bind("<Button-3>", self.on_right_click)
        self.image_label.bind("<B1-Motion>", self.on_drag)
        self.image_label.bind("<ButtonRelease-1>", self.on_drop)
        
        self.info_label.bind("<Button-1>", self.on_click)
        self.info_label.bind("<Button-3>", self.on_right_click)
        self.info_label.bind("<B1-Motion>", self.on_drag)
        self.info_label.bind("<ButtonRelease-1>", self.on_drop)
        
        self.update_appearance()
    
    def on_click(self, event):
        """Handle thumbnail click for selection"""
        self.app.select_thumbnail(self)
        self.app.drag_data["x"] = event.x_root
        self.app.drag_data["y"] = event.y_root
        self.app.drag_data["item"] = self
    
    def on_right_click(self, event):
        """Handle right-click for context menu"""
        # Create context menu
        context_menu = tk.Menu(self, tearoff=0)
        
        if self.is_removed:
            context_menu.add_command(label="Restore Page", command=lambda: self.app.restore_specific_page(self.page_index))
        else:
            context_menu.add_command(label="Remove Page", command=lambda: self.app.remove_specific_page(self.page_index))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def on_drag(self, event):
        """Handle dragging motion"""
        if self.app.drag_data["item"] == self and not self.is_removed:
            # Calculate distance moved
            dx = event.x_root - self.app.drag_data["x"]
            dy = event.y_root - self.app.drag_data["y"]
            
            # If moved significantly, start visual drag feedback
            if abs(dx) > 5 or abs(dy) > 5:
                self.configure(fg_color=("gray70", "gray30"))
    
    def on_drop(self, event):
        """Handle drop operation"""
        if self.app.drag_data["item"] == self and not self.is_removed:
            # Find target position based on mouse location
            target_widget = event.widget.winfo_containing(event.x_root, event.y_root)
            
            # Find the target page thumbnail
            target_thumbnail = None
            for thumb in self.app.page_thumbnails:
                if (target_widget == thumb or target_widget == thumb.image_label or 
                    target_widget == thumb.info_label) and not thumb.is_removed:
                    target_thumbnail = thumb
                    break
            
            if target_thumbnail and target_thumbnail != self:
                self.app.move_page_to_position(self.page_index, target_thumbnail.page_index)
        
        # Reset drag state
        self.app.drag_data = {"x": 0, "y": 0, "item": None}
        self.update_appearance()
    
    def update_appearance(self):
        """Update visual appearance based on state"""
        if self.is_removed:
            self.configure(fg_color=("gray80", "gray20"))
            self.image_label.configure(text_color=("gray60", "gray40"))
            self.info_label.configure(text_color=("gray60", "gray40"))
            self.image_label.configure(fg_color=("gray80", "gray20"))
        elif self.is_selected:
            self.configure(fg_color=("#1f538d", "#1f538d"))
            self.image_label.configure(fg_color=("#1f538d", "#1f538d"))
        else:
            self.configure(fg_color=("gray90", "gray13"))
            self.image_label.configure(fg_color=("gray90", "gray13"))
            self.info_label.configure(text_color=("gray10", "gray90"))
    
    def update_position_info(self):
        """Update the position information displayed"""
        if not self.is_removed:
            current_pos = [i for i, idx in enumerate(self.app.organize_page_order) if idx not in self.app.removed_pages and idx == self.page_index]
            if current_pos:
                pos = current_pos[0] + 1
                self.info_label.configure(text=f"Page {pos}\n(orig. {self.original_page_num})")
        else:
            self.info_label.configure(text=f"REMOVED\n(orig. {self.original_page_num})")
    
    def set_removed(self, removed):
        """Set the removed state"""
        self.is_removed = removed
        self.update_appearance()
        self.update_position_info()
    
    def set_selected(self, selected):
        """Set the selected state"""
        self.is_selected = selected
        self.update_appearance() 