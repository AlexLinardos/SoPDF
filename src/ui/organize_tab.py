"""
Organize Tab for SoPDF

This module contains the PDF page organization functionality.
"""

import os
import io

# Use lazy loading for UI libraries
from src.utils.lazy_ui import ctk, tk, pil

# Import other modules normally
import fitz  # PyMuPDF


class OrganizeTab:
    """Manages the PDF page organization functionality"""
    
    def __init__(self, tab_frame, app_reference):
        self.tab_frame = tab_frame
        self.app = app_reference
        
        # Initialize organize-related variables
        self.organize_pdf_path = None
        self.organize_pages = []  # List of page objects
        self.organize_page_order = []  # List of page indices (0-based)
        self.removed_pages = set()  # Set of removed page indices
        self.listbox_drag_data = {"dragging": False, "start_index": None}  # Drag state for listbox
        
        # Preview mode variables
        self.preview_mode = False
        self.pdf_document = None  # PyMuPDF document
        self.page_thumbnails = {}  # Cache for page thumbnails
        self.preview_widgets = {}  # Cache for preview widgets
        self.selected_pages = set()  # Selected pages in preview mode
        self.preview_drag_data = {"dragging": False, "start_widget": None, "start_x": 0, "start_y": 0}
        self.current_drop_target = None  # Track current drop target for visual feedback
        
        self.setup_organize_tab()
    
    def setup_organize_tab(self):
        """Setup the Organize tab with text-based PDF page organization functionality"""
        # Configure grid weights
        self.tab_frame.grid_columnconfigure(0, weight=1)
        self.tab_frame.grid_rowconfigure(2, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.tab_frame,
            text="📁 Organize PDF Pages",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # File selection frame
        file_frame = ctk.CTkFrame(self.tab_frame)
        file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)
        
        # Select file button
        self.select_organize_btn = ctk.CTkButton(
            file_frame,
            text="📁 Select PDF File",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14),
            command=self.select_pdf_for_organize
        )
        self.select_organize_btn.grid(row=0, column=0, padx=(20, 10), pady=20)
        
        # File info label
        self.organize_file_info = ctk.CTkLabel(
            file_frame,
            text="No file selected",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.organize_file_info.grid(row=0, column=1, padx=10, pady=20, sticky="w")
        
        # Clear file button
        self.clear_organize_btn = ctk.CTkButton(
            file_frame,
            text="🗑️ Clear",
            width=100,
            height=45,
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.clear_organize_file
        )
        self.clear_organize_btn.grid(row=0, column=2, padx=(10, 20), pady=20)
        
        # Main content frame with controls and page list
        self.content_frame = ctk.CTkFrame(self.tab_frame, corner_radius=8)
        self.content_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        
        # Control buttons frame at top
        controls_frame = ctk.CTkFrame(self.content_frame)
        controls_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        controls_frame.grid_columnconfigure(0, weight=1)
        
        # Top row with instructions and preview toggle
        top_row_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        top_row_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        top_row_frame.grid_columnconfigure(0, weight=1)
        
        # Instructions label
        self.instructions_label = ctk.CTkLabel(
            top_row_frame,
            text="🧾 Instructions: Use buttons or drag to reorder • Remove/restore pages as needed",
            font=ctk.CTkFont(size=14),
            text_color="lightblue"
        )
        self.instructions_label.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        
        # Preview mode toggle
        self.preview_toggle = ctk.CTkSwitch(
            top_row_frame,
            text="🖼️ Preview Mode",
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.toggle_preview_mode
        )
        self.preview_toggle.grid(row=0, column=1, padx=(20, 0), pady=0, sticky="e")
        
        # Control buttons
        button_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.reset_order_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Reset All",
            width=120,
            height=35,
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.reset_page_order
        )
        self.reset_order_btn.grid(row=0, column=0, padx=(0, 10), pady=5)
        
        self.save_organized_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Organized PDF",
            width=180,
            height=35,
            state="disabled",
            command=self.save_organized_pdf,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.save_organized_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Status info
        self.organize_status = ctk.CTkLabel(
            button_frame,
            text="No file loaded",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.organize_status.grid(row=0, column=2, padx=(20, 0), pady=5, sticky="e")
        
        # Container frame for the text interface
        self.pages_frame = ctk.CTkFrame(self.content_frame, corner_radius=8)
        self.pages_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.pages_frame.grid_columnconfigure(0, weight=1)
        self.pages_frame.grid_rowconfigure(0, weight=1)
    
    def toggle_preview_mode(self):
        """Toggle between text and preview modes"""
        self.preview_mode = self.preview_toggle.get()
        
        # Update instructions
        if self.preview_mode:
            self.instructions_label.configure(
                text="🖼️ Preview Mode: Drag to reorder • Right-click to remove/restore"
            )
        else:
            self.instructions_label.configure(
                text="🧾 Instructions: Use buttons or drag-and-drop to reorder • Remove/restore pages as needed"
            )
        
        # Only update interface if a PDF is loaded
        if not self.organize_pdf_path:
            return
        
        # Clear existing content
        for widget in self.pages_frame.winfo_children():
            widget.destroy()
        
        # Create appropriate interface
        if self.preview_mode:
            self.create_preview_interface()
        else:
            self.create_text_based_organize_interface()
    
    def select_pdf_for_organize(self):
        """Select a PDF file for text-based organizing"""
        file_types = [("PDF files", "*.pdf"), ("All files", "*.*")]
        file_path = tk.filedialog.askopenfilename(
            title="Select PDF file to organize",
            filetypes=file_types
        )
        
        if file_path:
            try:
                # Show loading message
                self.organize_file_info.configure(text="Loading PDF...", text_color="orange")
                self.app.root.update()
                
                # Open PDF with PyMuPDF 
                self.pdf_document = fitz.open(file_path)
                page_count = self.pdf_document.page_count
                
                if page_count < 1:
                    tk.messagebox.showwarning("Warning", "PDF file appears to be empty.")
                    self.pdf_document.close()
                    return
                
                # Set up organize variables
                self.organize_pdf_path = file_path
                # With PyMuPDF, we don't store page objects, just work with page indices
                self.organize_pages = list(range(page_count))  # Store page indices instead
                self.organize_page_order = list(range(page_count))  # [0, 1, 2, ...]
                self.removed_pages = set()
                self.page_thumbnails = {}  # Clear thumbnail cache
                self.preview_widgets = {}  # Clear widget cache
                
                # Clear existing content
                for widget in self.pages_frame.winfo_children():
                    widget.destroy()
                
                # Create appropriate interface based on current mode
                if self.preview_mode:
                    self.create_preview_interface()
                else:
                    self.create_text_based_organize_interface()
                
                # Update UI
                filename = os.path.basename(file_path)
                self.organize_file_info.configure(
                    text=f"{filename} ({page_count} pages)",
                    text_color="white"
                )
                
                # Enable controls
                self.clear_organize_btn.configure(state="normal")
                self.reset_order_btn.configure(state="normal")
                self.save_organized_btn.configure(state="normal")
                self.preview_toggle.configure(state="normal")
                
                # Apply saved preview mode state
                self.apply_saved_preview_state()
                
                # Update status
                self.update_organize_status()
                
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error reading PDF file:\n{str(e)}")
    
    def apply_saved_preview_state(self):
        """Apply saved preview mode state when PDF is loaded"""
        try:
            # Get saved preview mode state from app
            if (hasattr(self.app, 'window_state') and 
                'organize_preview_mode' in self.app.window_state):
                
                saved_preview_mode = self.app.window_state['organize_preview_mode']
                
                if saved_preview_mode and not self.preview_mode:
                    # Apply saved state: turn on preview mode
                    self.preview_toggle.select()
                    self.toggle_preview_mode()
                elif not saved_preview_mode and self.preview_mode:
                    # Apply saved state: turn off preview mode
                    self.preview_toggle.deselect()
                    self.toggle_preview_mode()
        except Exception as e:
            print(f"Could not apply saved preview state: {e}")
    
    def create_text_based_organize_interface(self):
        """Create text-based interface for page organization"""
        # Main container
        text_container = ctk.CTkFrame(self.pages_frame)
        text_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        text_container.grid_columnconfigure(0, weight=0)  # Controls column - fixed width
        text_container.grid_columnconfigure(1, weight=1)  # List column - expandable
        text_container.grid_rowconfigure(0, weight=1)
        
        # Control buttons frame (compact for smaller screens)
        controls_frame = ctk.CTkFrame(text_container)
        controls_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ns")
        
        # Move up button
        self.text_move_up_btn = ctk.CTkButton(
            controls_frame,
            text="⬆ Move Up",
            width=110,
            height=32,
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self.text_move_page_up
        )
        self.text_move_up_btn.grid(row=0, column=0, padx=10, pady=(10, 3))
        
        # Move down button
        self.text_move_down_btn = ctk.CTkButton(
            controls_frame,
            text="⬇ Move Down",
            width=110,
            height=32,
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self.text_move_page_down
        )
        self.text_move_down_btn.grid(row=1, column=0, padx=10, pady=3)
        
        # Remove page button
        self.text_remove_btn = ctk.CTkButton(
            controls_frame,
            text="❌ Remove",
            width=110,
            height=32,
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self.text_remove_page
        )
        self.text_remove_btn.grid(row=2, column=0, padx=10, pady=3)
        
        # Restore page button
        self.text_restore_btn = ctk.CTkButton(
            controls_frame,
            text="↶ Restore",
            width=110,
            height=32,
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self.text_restore_page
        )
        self.text_restore_btn.grid(row=3, column=0, padx=10, pady=(3, 10))
        
        # List frame
        list_frame = ctk.CTkFrame(text_container)
        list_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_columnconfigure(1, weight=0)  # Keep scrollbar column fixed width
        list_frame.grid_rowconfigure(1, weight=1)  # Make the listbox row expandable
        
        # Instructions
        instructions = ctk.CTkLabel(
            list_frame,
            text="📋 Select a page • Use buttons or drag-and-drop to reorder",
            font=ctk.CTkFont(size=14),
            text_color="lightblue"
        )
        instructions.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        # Page listbox with drag-and-drop support (responsive height)
        self.text_organize_listbox = tk.Listbox(
            list_frame,
            bg="#212121",
            fg="white",
            selectbackground="#1f538d",
            selectforeground="white",
            font=("Segoe UI", 13),
            borderwidth=0,
            highlightthickness=0
        )
        self.text_organize_listbox.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.text_organize_listbox.bind('<<ListboxSelect>>', self.on_text_page_select)
        
        # Add drag-and-drop functionality
        self.text_organize_listbox.bind('<Button-1>', self.on_listbox_click)
        self.text_organize_listbox.bind('<B1-Motion>', self.on_listbox_drag)
        self.text_organize_listbox.bind('<ButtonRelease-1>', self.on_listbox_drop)
        
        # Initialize drag state
        self.listbox_drag_data = {"dragging": False, "start_index": None}
        
        # Scrollbar for listbox
        text_scrollbar = ctk.CTkScrollbar(list_frame, command=self.text_organize_listbox.yview)
        text_scrollbar.grid(row=1, column=1, padx=(0, 10), pady=(5, 10), sticky="ns")
        self.text_organize_listbox.configure(yscrollcommand=text_scrollbar.set)
        
        # Update the text display
        self.update_text_organize_display()
    
    def create_preview_interface(self):
        """Create preview interface with page thumbnails in a grid"""
        # Create scrollable frame for the preview grid
        self.preview_scrollable_frame = ctk.CTkScrollableFrame(
            self.pages_frame,
            label_text="📁 PDF Pages Preview"
        )
        self.preview_scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configure grid for responsive layout
        for i in range(6):  # 6 columns
            self.preview_scrollable_frame.grid_columnconfigure(i, weight=1)
        
        self.update_preview_display()
    
    def generate_page_thumbnail(self, page_index, size=(120, 160)):
        """Generate a thumbnail image for a PDF page using PyMuPDF"""
        if page_index in self.page_thumbnails:
            return self.page_thumbnails[page_index]
        
        try:
            # Get page from PyMuPDF document
            page = self.pdf_document[page_index]
            
            # Render page to image
            zoom = min(size[0] / page.rect.width, size[1] / page.rect.height)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            pil_image = pil.Image.open(io.BytesIO(img_data))
            
            # Resize to exact thumbnail size
            pil_image = pil_image.resize(size, pil.Image.Resampling.LANCZOS)
            
            # Convert to CTkImage for better HighDPI support
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            
            # Cache the thumbnail
            self.page_thumbnails[page_index] = ctk_image
            
            return ctk_image
        
        except Exception as e:
            print(f"Error generating thumbnail for page {page_index}: {e}")
            # Return a placeholder image
            placeholder = pil.Image.new('RGB', size, color='lightgray')
            return ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=size)
    
    def update_preview_display(self):
        """Update the preview display with current page order"""
        # Clear existing preview widgets and all children in the scrollable frame
        for widget_dict in self.preview_widgets.values():
            if isinstance(widget_dict, dict):
                for widget in widget_dict.values():
                    if hasattr(widget, 'destroy'):
                        widget.destroy()
        
        # Also clear any remaining widgets in the scrollable frame (like removed page widgets)
        for widget in self.preview_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.preview_widgets = {}
        
        # Display active pages
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        cols = 6  # Number of columns in grid
        
        for i, page_idx in enumerate(active_pages):
            row = i // cols
            col = i % cols
            
            # Create page frame
            page_frame = ctk.CTkFrame(
                self.preview_scrollable_frame,
                width=140,
                height=200,
                corner_radius=8
            )
            page_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            page_frame.grid_propagate(False)
            
            # Generate thumbnail
            thumbnail = self.generate_page_thumbnail(page_idx)
            
            # Create thumbnail label
            thumbnail_label = ctk.CTkLabel(
                page_frame,
                image=thumbnail,
                text="",
                width=120,
                height=160
            )
            thumbnail_label.grid(row=0, column=0, padx=10, pady=(10, 5))
            
            # Page info label
            original_page_num = page_idx + 1
            current_position = i + 1
            info_text = f"Page {current_position}\n(OG: {original_page_num})"
            
            info_label = ctk.CTkLabel(
                page_frame,
                text=info_text,
                font=ctk.CTkFont(size=11),
                height=20
            )
            info_label.grid(row=1, column=0, padx=5, pady=(0, 10))
            
            # Store references
            self.preview_widgets[page_idx] = {
                'frame': page_frame,
                'thumbnail': thumbnail_label,
                'info': info_label,
                'position': i
            }
            
            # Bind events for selection and drag-and-drop
            for widget in [page_frame, thumbnail_label, info_label]:
                widget.bind("<Button-1>", lambda e, p=page_idx: self.on_preview_page_click(e, p))
                widget.bind("<Button-3>", lambda e, p=page_idx: self.on_preview_page_right_click(e, p))
                widget.bind("<B1-Motion>", lambda e, p=page_idx: self.on_preview_page_drag(e, p))
                widget.bind("<ButtonRelease-1>", lambda e: self.on_preview_page_drop(e))
                # Add hover effects
                widget.bind("<Enter>", lambda e, p=page_idx: self.on_preview_page_hover(e, p))
                widget.bind("<Leave>", lambda e, p=page_idx: self.on_preview_page_leave(e, p))
        
        # Add removed pages section if any
        if self.removed_pages:
            removed_row = (len(active_pages) // cols) + 1
            
            # Removed pages header
            removed_header = ctk.CTkLabel(
                self.preview_scrollable_frame,
                text="🗑️ REMOVED PAGES",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="orange"
            )
            removed_header.grid(row=removed_row, column=0, columnspan=cols, padx=5, pady=(20, 10), sticky="ew")
            
            # Display removed pages
            for i, page_idx in enumerate(sorted(self.removed_pages)):
                row = removed_row + 1 + (i // cols)
                col = i % cols
                
                # Create removed page frame (grayed out)
                removed_frame = ctk.CTkFrame(
                    self.preview_scrollable_frame,
                    width=140,
                    height=200,
                    corner_radius=8,
                    fg_color="gray30"
                )
                removed_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                removed_frame.grid_propagate(False)
                
                # Generate thumbnail (grayed out)
                thumbnail = self.generate_page_thumbnail(page_idx)
                
                thumbnail_label = ctk.CTkLabel(
                    removed_frame,
                    image=thumbnail,
                    text="",
                    width=120,
                    height=160
                )
                thumbnail_label.grid(row=0, column=0, padx=10, pady=(10, 5))
                
                # Removed page info
                original_page_num = page_idx + 1
                info_text = f"❌ REMOVED\nPage {original_page_num}"
                
                info_label = ctk.CTkLabel(
                    removed_frame,
                    text=info_text,
                    font=ctk.CTkFont(size=11),
                    text_color="orange",
                    height=20
                )
                info_label.grid(row=1, column=0, padx=5, pady=(0, 10))
                
                # Bind right-click for restore
                for widget in [removed_frame, thumbnail_label, info_label]:
                    widget.bind("<Button-3>", lambda e, p=page_idx: self.on_preview_removed_page_right_click(e, p))
    
    def on_preview_page_click(self, event, page_idx):
        """Handle click on preview page to initialize drag"""
        # Initialize drag data
        self.preview_drag_data = {
            "dragging": False, 
            "start_widget": page_idx,
            "start_x": event.x_root,
            "start_y": event.y_root
        }
    
    def on_preview_page_right_click(self, event, page_idx):
        """Handle right-click on preview page for context menu"""
        # Create context menu
        context_menu = tk.Menu(self.app.root, tearoff=0)
        
        original_page_num = page_idx + 1
        context_menu.add_command(
            label=f"Remove Page {original_page_num}",
            command=lambda: self.preview_remove_page(page_idx)
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def on_preview_removed_page_right_click(self, event, page_idx):
        """Handle right-click on removed page for restore"""
        # Create context menu
        context_menu = tk.Menu(self.app.root, tearoff=0)
        
        original_page_num = page_idx + 1
        context_menu.add_command(
            label=f"Restore Page {original_page_num}",
            command=lambda: self.preview_restore_page(page_idx)
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def on_preview_page_drag(self, event, page_idx):
        """Handle dragging in preview mode"""
        if (self.preview_drag_data["start_widget"] == page_idx and 
            not self.preview_drag_data["dragging"]):
            
            # Check if we've moved enough to start dragging (minimum threshold)
            dx = abs(event.x_root - self.preview_drag_data["start_x"])
            dy = abs(event.y_root - self.preview_drag_data["start_y"])
            
            if dx > 5 or dy > 5:  # Minimum movement threshold
                self.preview_drag_data["dragging"] = True
                # Visual feedback for dragging
                if page_idx in self.preview_widgets:
                    self.preview_widgets[page_idx]['frame'].configure(border_width=2, border_color="orange")
                try:
                    event.widget.configure(cursor="fleur")
                except:
                    pass  # Some widgets may not support cursor changes
        
        # Update drop target highlighting during drag
        if self.preview_drag_data["dragging"] and self.preview_drag_data["start_widget"] == page_idx:
            self.update_drop_target_highlight(event)
    
    def update_drop_target_highlight(self, event):
        """Update visual highlighting of drop target during drag"""
        # Find which page frame the mouse is currently over
        new_drop_target = None
        
        try:
            for page_idx, widgets in self.preview_widgets.items():
                # Skip the page being dragged and removed pages
                if (page_idx == self.preview_drag_data["start_widget"] or 
                    page_idx in self.removed_pages):
                    continue
                
                frame_widget = widgets['frame']
                frame_x = frame_widget.winfo_rootx()
                frame_y = frame_widget.winfo_rooty()
                frame_width = frame_widget.winfo_width()
                frame_height = frame_widget.winfo_height()
                
                # Check if mouse is within this frame's bounds
                if (frame_x <= event.x_root <= frame_x + frame_width and 
                    frame_y <= event.y_root <= frame_y + frame_height):
                    new_drop_target = page_idx
                    break
        
        except Exception as e:
            # Ignore errors during drag operations
            pass
        
        # Update highlighting if drop target changed
        if new_drop_target != self.current_drop_target:
            # Clear previous drop target highlight
            if (self.current_drop_target is not None and 
                self.current_drop_target in self.preview_widgets):
                self.preview_widgets[self.current_drop_target]['frame'].configure(
                    border_width=0
                )
            
            # Set new drop target highlight
            if (new_drop_target is not None and 
                new_drop_target in self.preview_widgets):
                self.preview_widgets[new_drop_target]['frame'].configure(
                    border_width=2, 
                    border_color="lightgreen"
                )
            
            self.current_drop_target = new_drop_target
    
    def on_preview_page_drop(self, event):
        """Handle drop in preview mode"""
        if self.preview_drag_data["dragging"]:
            try:
                # Reset cursor
                event.widget.configure(cursor="")
            except:
                pass
            
            # Reset visual feedback for the dragged item
            if (self.preview_drag_data["start_widget"] is not None and 
                self.preview_drag_data["start_widget"] in self.preview_widgets):
                # Reset border to normal
                self.preview_widgets[self.preview_drag_data["start_widget"]]['frame'].configure(border_width=0)
            
            # Clear drop target highlight
            if (self.current_drop_target is not None and 
                self.current_drop_target in self.preview_widgets):
                self.preview_widgets[self.current_drop_target]['frame'].configure(border_width=0)
            self.current_drop_target = None
            
            # Find drop target by checking all page frames
            drop_target_page = None
            
            # Get the widget at the current mouse position
            try:
                widget_at_cursor = self.preview_scrollable_frame.winfo_containing(event.x_root, event.y_root)
                
                # Check if the cursor is over any page frame
                for page_idx, widgets in self.preview_widgets.items():
                    frame_widget = widgets['frame']
                    # Check if the mouse is within the bounds of this frame
                    frame_x = frame_widget.winfo_rootx()
                    frame_y = frame_widget.winfo_rooty()
                    frame_width = frame_widget.winfo_width()
                    frame_height = frame_widget.winfo_height()
                    
                    if (frame_x <= event.x_root <= frame_x + frame_width and 
                        frame_y <= event.y_root <= frame_y + frame_height):
                        drop_target_page = page_idx
                        break
                        
            except Exception as e:
                print(f"Drop detection error: {e}")
            
            # Perform reorder if valid drop target
            if (drop_target_page is not None and 
                self.preview_drag_data["start_widget"] is not None and
                drop_target_page != self.preview_drag_data["start_widget"] and
                drop_target_page not in self.removed_pages):
                
                self.preview_reorder_pages(self.preview_drag_data["start_widget"], drop_target_page)
        
        # Reset drag data
        self.preview_drag_data = {"dragging": False, "start_widget": None, "start_x": 0, "start_y": 0}
    
    def preview_reorder_pages(self, from_page, to_page):
        """Reorder pages in preview mode"""
        # Get current active pages
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        from_pos = active_pages.index(from_page)
        to_pos = active_pages.index(to_page)
        
        # Remove from_page from its current position in organize_page_order
        current_position = self.organize_page_order.index(from_page)
        self.organize_page_order.pop(current_position)
        
        # Find new insertion position
        target_position = self.organize_page_order.index(to_page)
        if from_pos < to_pos:
            # Moving forward - insert after target
            self.organize_page_order.insert(target_position + 1, from_page)
        else:
            # Moving backward - insert before target
            self.organize_page_order.insert(target_position, from_page)
        
        # Update display
        self.update_preview_display()
        self.update_organize_status()
    
    def preview_remove_page(self, page_idx):
        """Remove a page in preview mode"""
        original_page_num = page_idx + 1
        result = tk.messagebox.askyesno(
            "Remove Page",
            f"Remove page {original_page_num}?\n\nThis can be undone by right-clicking the removed page."
        )
        
        if result:
            self.removed_pages.add(page_idx)
            self.update_preview_display()
            self.update_organize_status()
    
    def preview_restore_page(self, page_idx):
        """Restore a removed page in preview mode"""
        self.removed_pages.remove(page_idx)
        self.update_preview_display()
        self.update_organize_status()
    
    def on_preview_page_hover(self, event, page_idx):
        """Handle hover over preview page"""
        if (page_idx in self.preview_widgets and 
            not self.preview_drag_data["dragging"]):
            self.preview_widgets[page_idx]['frame'].configure(border_width=1, border_color="gray50")
    
    def on_preview_page_leave(self, event, page_idx):
        """Handle leaving preview page"""
        if (page_idx in self.preview_widgets and 
            not self.preview_drag_data["dragging"]):
            self.preview_widgets[page_idx]['frame'].configure(border_width=0)
    
    def clear_organize_file(self):
        """Clear the selected PDF file"""
        self.organize_pdf_path = None
        self.organize_pages = []
        self.organize_page_order = []
        self.removed_pages = set()
        self.listbox_drag_data = {"dragging": False, "start_index": None}
        
        # Clear preview mode variables
        if self.pdf_document:
            self.pdf_document.close()
        self.pdf_document = None
        self.page_thumbnails = {}
        self.preview_widgets = {}
        self.selected_pages = set()
        self.preview_drag_data = {"dragging": False, "start_widget": None, "start_x": 0, "start_y": 0}
        self.current_drop_target = None
        
        # Reset preview mode toggle
        self.preview_toggle.deselect()
        self.preview_mode = False
        
        # Clear all interface elements
        for widget in self.pages_frame.winfo_children():
            widget.destroy()
        
        # Reset text interface references
        if hasattr(self, 'text_organize_listbox'):
            delattr(self, 'text_organize_listbox')
        
        # Update UI
        self.organize_file_info.configure(text="No file selected", text_color="gray")
        self.clear_organize_btn.configure(state="disabled")
        self.reset_order_btn.configure(state="disabled")
        self.save_organized_btn.configure(state="disabled")
        self.preview_toggle.configure(state="disabled")
        self.organize_status.configure(text="No file loaded", text_color="gray")
    
    def reset_page_order(self):
        """Reset page order to original"""
        if not self.organize_pdf_path:
            return
        
        result = tk.messagebox.askyesno(
            "Reset Order", 
            "Reset all changes and restore original page order?\n\nThis will undo all reordering and restore all removed pages."
        )
        
        if result:
            # Reset to original order
            self.organize_page_order = list(range(len(self.organize_pages)))
            self.removed_pages = set()

            
            # Update appropriate display
            if self.preview_mode:
                self.update_preview_display()
            elif hasattr(self, 'text_organize_listbox'):
                self.update_text_organize_display()
            
            self.update_organize_status()
    
    def update_organize_status(self):
        """Update the organize status display"""
        if not self.organize_pdf_path:
            self.organize_status.configure(text="No file loaded", text_color="gray")
            return
        
        total_pages = len(self.organize_pages)
        active_pages = len([idx for idx in self.organize_page_order if idx not in self.removed_pages])
        removed_count = len(self.removed_pages)
        
        # Check if order has changed
        active_order = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        original_order = [idx for idx in range(total_pages) if idx not in self.removed_pages]
        order_changed = active_order != original_order
        
        status_parts = []
        status_parts.append(f"📄 {active_pages}/{total_pages} pages")
        
        if removed_count > 0:
            status_parts.append(f"🗑️ {removed_count} removed")
        
        if order_changed:
            status_parts.append("🔄 Reordered")
        
        status_text = " • ".join(status_parts)
        
        # Color based on changes
        if removed_count > 0 or order_changed:
            self.organize_status.configure(text=status_text, text_color="orange")
        else:
            self.organize_status.configure(text=status_text, text_color="lightgreen")
    
    def save_organized_pdf(self):
        """Save the organized PDF with reordered/removed pages"""
        if not self.organize_pdf_path:
            tk.messagebox.showwarning("Warning", "Please select a PDF file first.")
            return
        
        # Get active pages in current order
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        if not active_pages:
            tk.messagebox.showwarning("Warning", "Cannot save PDF with no pages. Please restore at least one page.")
            return
        
        # Ask user where to save
        base_name = os.path.splitext(os.path.basename(self.organize_pdf_path))[0]
        output_file = tk.filedialog.asksaveasfilename(
            title="Save organized PDF as...",
            defaultextension=".pdf",
            initialfile=f"{base_name}_organized.pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
        
        try:
            # Create new PDF with organized pages
            output_doc = fitz.open()
            
            for page_idx in active_pages:
                # Insert individual page from source document
                output_doc.insert_pdf(self.pdf_document, from_page=page_idx, to_page=page_idx)
            
            # Save the organized PDF
            output_doc.save(output_file)
            output_doc.close()
            
            # Show success message
            total_original = len(self.organize_pages)
            pages_kept = len(active_pages)
            pages_removed = total_original - pages_kept
            
            success_msg = f"PDF successfully organized!\n\n"
            success_msg += f"Original pages: {total_original}\n"
            success_msg += f"Final pages: {pages_kept}\n"
            
            if pages_removed > 0:
                success_msg += f"Pages removed: {pages_removed}\n"
            
            success_msg += f"\nSaved as: {os.path.basename(output_file)}"
            
            tk.messagebox.showinfo("Success", success_msg)
            
            # Ask if user wants to clear the current file
            response = tk.messagebox.askyesno("Clear File", "Would you like to clear the current file and start over?")
            if response:
                self.clear_organize_file()
                
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error saving organized PDF:\n{str(e)}")
    
    # Text-based organize interface methods
    def update_text_organize_display(self):
        """Update the text-based page list display"""
        if not hasattr(self, 'text_organize_listbox'):
            return
            
        self.text_organize_listbox.delete(0, tk.END)
        
        # Add active pages
        for i, page_idx in enumerate(self.organize_page_order):
            if page_idx not in self.removed_pages:
                original_page_num = page_idx + 1
                current_position = len([idx for idx in self.organize_page_order[:i] if idx not in self.removed_pages]) + 1
                display_text = f"Page {current_position} (OG: {original_page_num})"
                self.text_organize_listbox.insert(tk.END, display_text)
        
        # Add removed pages section
        if self.removed_pages:
            self.text_organize_listbox.insert(tk.END, "")
            self.text_organize_listbox.insert(tk.END, "--- REMOVED PAGES ---")
            for page_idx in sorted(self.removed_pages):
                original_page_num = page_idx + 1
                display_text = f"❌ REMOVED: Page {original_page_num}"
                self.text_organize_listbox.insert(tk.END, display_text)
    
    def on_text_page_select(self, event):
        """Handle page selection in text interface"""
        selection = self.text_organize_listbox.curselection()
        
        if not selection:
            # Disable control buttons when no selection
            self.text_move_up_btn.configure(state="disabled")
            self.text_move_down_btn.configure(state="disabled")
            self.text_remove_btn.configure(state="disabled")
            self.text_restore_btn.configure(state="disabled")
            return
        
        index = selection[0]
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        if index < len(active_pages):
            page_idx = active_pages[index]
            
            # Enable/disable buttons based on position and status
            self.text_move_up_btn.configure(state="normal" if index > 0 else "disabled")
            self.text_move_down_btn.configure(state="normal" if index < len(active_pages) - 1 else "disabled")
            self.text_remove_btn.configure(state="normal")
            self.text_restore_btn.configure(state="disabled")  # Can't restore active pages
        else:
            # This is a removed page
            removed_index = index - len(active_pages)
            removed_pages_list = sorted(list(self.removed_pages))
            
            if removed_index < len(removed_pages_list):
                self.text_move_up_btn.configure(state="disabled")
                self.text_move_down_btn.configure(state="disabled")
                self.text_remove_btn.configure(state="disabled")  # Can't remove already removed pages
                self.text_restore_btn.configure(state="normal")
    
    # Drag-and-drop methods for the listbox
    def on_listbox_click(self, event):
        """Handle initial click on listbox for potential drag operation"""
        # Get the index of the clicked item
        index = self.text_organize_listbox.nearest(event.y)
        
        # Only allow dragging of active pages (not removed pages or separators)
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        if index < len(active_pages):
            self.listbox_drag_data["start_index"] = index
            self.listbox_drag_data["dragging"] = False
            # Select the item
            self.text_organize_listbox.selection_clear(0, tk.END)
            self.text_organize_listbox.selection_set(index)
            self.text_organize_listbox.activate(index)
        else:
            self.listbox_drag_data["start_index"] = None
    
    def on_listbox_drag(self, event):
        """Handle drag motion over listbox"""
        if self.listbox_drag_data["start_index"] is not None:
            # Start visual drag feedback if we've moved enough
            if not self.listbox_drag_data["dragging"]:
                self.listbox_drag_data["dragging"] = True
                # Change cursor to indicate dragging
                self.text_organize_listbox.configure(cursor="fleur")
            
            # Get current position
            current_index = self.text_organize_listbox.nearest(event.y)
            active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
            
            # Only highlight valid drop targets (active pages)
            if current_index < len(active_pages):
                self.text_organize_listbox.selection_clear(0, tk.END)
                self.text_organize_listbox.selection_set(current_index)
    
    def on_listbox_drop(self, event):
        """Handle drop operation in listbox"""
        if self.listbox_drag_data["dragging"] and self.listbox_drag_data["start_index"] is not None:
            # Get drop position
            drop_index = self.text_organize_listbox.nearest(event.y)
            start_index = self.listbox_drag_data["start_index"]
            
            active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
            
            # Only allow drops on valid positions (active pages)
            if drop_index < len(active_pages) and drop_index != start_index:
                # Perform the reorder
                self.listbox_move_page(start_index, drop_index)
        
        # Reset drag state
        self.listbox_drag_data = {"dragging": False, "start_index": None}
        self.text_organize_listbox.configure(cursor="")
        
        # Update button states
        if hasattr(self, 'text_organize_listbox'):
            # Trigger selection event to update buttons
            self.on_text_page_select(None)
    
    def listbox_move_page(self, from_index, to_index):
        """Move a page from one position to another in the listbox"""
        if from_index == to_index:
            return
        
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        # Check if both indices are within active pages range
        if from_index >= len(active_pages) or to_index >= len(active_pages):
            return
        
        # Get the page index being moved
        page_idx = active_pages[from_index]
        
        # Remove the page from current position in organize_page_order
        current_position = self.organize_page_order.index(page_idx)
        self.organize_page_order.pop(current_position)
        
        # Find where to insert it
        if to_index == 0:
            # Moving to beginning
            self.organize_page_order.insert(0, page_idx)
        elif to_index >= len(active_pages) - 1:
            # Moving to end (among active pages)
            # Find the last active page's position and insert after it
            last_active_pos = max([self.organize_page_order.index(idx) for idx in active_pages if idx != page_idx])
            self.organize_page_order.insert(last_active_pos + 1, page_idx)
        else:
            # Moving to middle - insert before the page that will be at to_index
            active_pages_updated = [idx for idx in self.organize_page_order if idx not in self.removed_pages and idx != page_idx]
            target_page = active_pages_updated[to_index]
            target_position = self.organize_page_order.index(target_page)
            self.organize_page_order.insert(target_position, page_idx)
        
        # Update display and status
        self.update_text_organize_display()
        self.update_organize_status()
        
        # Restore selection to the new position
        self.text_organize_listbox.selection_set(to_index)
        self.text_organize_listbox.activate(to_index)
    
    def text_move_page_up(self):
        """Move selected page up in the text interface"""
        selection = self.text_organize_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        if index > 0 and index < len(active_pages):
            # Get the page indices
            current_page = active_pages[index]
            above_page = active_pages[index - 1]
            
            # Find their positions in the main order list
            pos1 = self.organize_page_order.index(current_page)
            pos2 = self.organize_page_order.index(above_page)
            
            # Swap them
            self.organize_page_order[pos1], self.organize_page_order[pos2] = \
                self.organize_page_order[pos2], self.organize_page_order[pos1]
            
            # Update display and maintain selection
            self.update_text_organize_display()
            self.text_organize_listbox.select_set(index - 1)
            self.on_text_page_select(None)
            self.update_organize_status()
    
    def text_move_page_down(self):
        """Move selected page down in the text interface"""
        selection = self.text_organize_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        if index < len(active_pages) - 1:
            # Get the page indices
            current_page = active_pages[index]
            below_page = active_pages[index + 1]
            
            # Find their positions in the main order list
            pos1 = self.organize_page_order.index(current_page)
            pos2 = self.organize_page_order.index(below_page)
            
            # Swap them
            self.organize_page_order[pos1], self.organize_page_order[pos2] = \
                self.organize_page_order[pos2], self.organize_page_order[pos1]
            
            # Update display and maintain selection
            self.update_text_organize_display()
            self.text_organize_listbox.select_set(index + 1)
            self.on_text_page_select(None)
            self.update_organize_status()
    
    def text_remove_page(self):
        """Remove selected page in the text interface"""
        selection = self.text_organize_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        if index < len(active_pages):
            page_to_remove = active_pages[index]
            original_page_num = page_to_remove + 1
            
            # Confirm removal
            result = tk.messagebox.askyesno(
                "Remove Page", 
                f"Remove page {index + 1} (originally page {original_page_num})?\n\nThis can be undone with 'Restore Page'."
            )
            
            if result:
                self.removed_pages.add(page_to_remove)
                self.update_text_organize_display()
                self.on_text_page_select(None)
                self.update_organize_status()
    
    def text_restore_page(self):
        """Restore a removed page in the text interface"""
        if not self.removed_pages:
            return
        
        # Create a dialog to select which page to restore
        removed_list = sorted(list(self.removed_pages))
        page_options = [f"Page {idx + 1}" for idx in removed_list]
        
        if len(removed_list) == 1:
            # Only one page to restore
            page_to_restore = removed_list[0]
            self.removed_pages.remove(page_to_restore)
        else:
            # Show selection dialog for multiple removed pages
            dialog_text = "Select page to restore:\n\n" + "\n".join(
                f"{i+1}. {page_options[i]}" for i in range(len(page_options))
            )
            
            try:
                choice = tk.simpledialog.askinteger(
                    "Restore Page",
                    dialog_text + f"\n\nEnter number (1-{len(page_options)}):",
                    minvalue=1,
                    maxvalue=len(page_options)
                )
                
                if choice:
                    page_to_restore = removed_list[choice - 1]
                    self.removed_pages.remove(page_to_restore)
                else:
                    return
            except:
                return
        
        self.update_text_organize_display()
        self.on_text_page_select(None)
        self.update_organize_status() 