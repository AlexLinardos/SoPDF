"""
Split Tab for SoPDF

This module contains the PDF splitting functionality.
"""

import os
import io

# Use lazy loading for UI libraries
from src.utils.lazy_ui import ctk, tk, pil

# Import other modules normally
import fitz  # PyMuPDF


class SplitTab:
    """Manages the PDF splitting functionality"""
    
    def __init__(self, tab_frame, app_reference):
        self.tab_frame = tab_frame
        self.app = app_reference
        
        # Initialize split-related variables
        self.split_pdf_path = None
        self.split_pdf_pages = 0
        self.pdf_document = None  # PyMuPDF document for preview
        self.page_thumbnails = {}  # Cache for page thumbnails
        
        self.setup_split_tab()
    
    def setup_split_tab(self):
        """Setup the Split tab with PDF splitting functionality"""
        # Configure grid weights
        self.tab_frame.grid_columnconfigure(0, weight=1)
        self.tab_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.tab_frame,
            text="✂️Split PDF Documents",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Main content frame (now scrollable)
        content_frame = ctk.CTkScrollableFrame(self.tab_frame, corner_radius=8)
        content_frame.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(2, weight=1)
        
        # File selection section
        file_section_label = ctk.CTkLabel(
            content_frame,
            text="Select PDF File to Split:",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        file_section_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # File selection frame
        file_frame = ctk.CTkFrame(content_frame)
        file_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)
        
        # Select file button
        self.select_pdf_btn = ctk.CTkButton(
            file_frame,
            text="📁 Select PDF File",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14),
            command=self.select_pdf_for_split
        )
        self.select_pdf_btn.grid(row=0, column=0, padx=(20, 10), pady=20)
        
        # File info label
        self.file_info_label = ctk.CTkLabel(
            file_frame,
            text="No file selected",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.file_info_label.grid(row=0, column=1, padx=10, pady=20, sticky="w")
        
        # Clear file button
        self.clear_pdf_btn = ctk.CTkButton(
            file_frame,
            text="🗑️ Clear",
            width=100,
            height=45,
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.clear_split_file
        )
        self.clear_pdf_btn.grid(row=0, column=2, padx=(10, 20), pady=20)
        
        # Split settings frame
        settings_frame = ctk.CTkFrame(content_frame)
        settings_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Split settings title
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Split Settings:",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_title.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Split point controls
        split_control_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        split_control_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        split_control_frame.grid_columnconfigure(1, weight=1)
        
        # Split point label
        split_label = ctk.CTkLabel(
            split_control_frame,
            text="Split after page:",
            font=ctk.CTkFont(size=16)
        )
        split_label.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")
        
        # Split point slider
        self.split_slider = ctk.CTkSlider(
            split_control_frame,
            from_=1,
            to=1,
            number_of_steps=1,
            state="disabled",
            command=self.update_split_preview
        )
        self.split_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Split point value label
        self.split_value_label = ctk.CTkLabel(
            split_control_frame,
            text="1",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=40
        )
        self.split_value_label.grid(row=0, column=2, padx=(10, 0), pady=10)

        # Split point entry (new)
        self.split_entry = ctk.CTkEntry(
            split_control_frame,
            width=60,
            state="disabled"
        )
        self.split_entry.grid(row=0, column=3, padx=(10, 0), pady=10)
        self.split_entry.insert(0, "1")
        self.split_entry.bind("<Return>", self.on_split_entry)
        self.split_entry.bind("<FocusOut>", self.on_split_entry)
        
        # Preview frame - now with both text and visual preview
        preview_frame = ctk.CTkFrame(settings_frame)
        preview_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(1, weight=1)
        
        # Left side - text preview
        text_preview_frame = ctk.CTkFrame(preview_frame)
        text_preview_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        text_preview_title = ctk.CTkLabel(
            text_preview_frame,
            text="📄 Split Preview",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        text_preview_title.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            text_preview_frame,
            text="Select a PDF file to preview split",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.preview_label.grid(row=1, column=0, padx=10, pady=(5, 10))
        
        # Right side - visual page preview
        visual_preview_frame = ctk.CTkFrame(preview_frame)
        visual_preview_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        
        visual_preview_title = ctk.CTkLabel(
            visual_preview_frame,
            text="🖼️ Page Preview",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        visual_preview_title.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Page thumbnail display
        self.page_thumbnail_label = ctk.CTkLabel(
            visual_preview_frame,
            text="No page to preview",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            width=140,
            height=160
        )
        self.page_thumbnail_label.grid(row=1, column=0, padx=10, pady=(5, 5))
        
        # Page info label
        self.page_info_label = ctk.CTkLabel(
            visual_preview_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="lightblue",
            height=20
        )
        self.page_info_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        
        # Split action frame
        action_frame = ctk.CTkFrame(settings_frame)
        action_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(2, weight=1)
        
        # Split button
        self.split_btn = ctk.CTkButton(
            action_frame,
            text="✂️ Split PDF",
            width=180,
            height=55,
            state="disabled",
            command=self.split_pdf,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.split_btn.grid(row=0, column=1, padx=20, pady=20)
    
    def generate_page_thumbnail(self, page_index, size=(120, 160)):
        """Generate a thumbnail image for a PDF page using PyMuPDF"""
        cache_key = f"{page_index}_{size[0]}x{size[1]}"
        if cache_key in self.page_thumbnails:
            return self.page_thumbnails[cache_key]
        
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
            self.page_thumbnails[cache_key] = ctk_image
            
            return ctk_image
        
        except Exception as e:
            print(f"Error generating thumbnail for page {page_index}: {e}")
            # Return a placeholder image
            placeholder = pil.Image.new('RGB', size, color='lightgray')
            return ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=size)
    
    def select_pdf_for_split(self):
        """Select a PDF file for splitting"""
        file_types = [("PDF files", "*.pdf"), ("All files", "*.*")]
        file_path = tk.filedialog.askopenfilename(
            title="Select PDF file to split",
            filetypes=file_types
        )
        
        if file_path:
            try:
                # Close previous document if open
                if self.pdf_document:
                    self.pdf_document.close()
                
                # Read PDF to get page count
                self.pdf_document = fitz.open(file_path)
                page_count = self.pdf_document.page_count
                
                if page_count < 2:
                    tk.messagebox.showwarning("Warning", "PDF must have at least 2 pages to split.")
                    self.pdf_document.close()
                    self.pdf_document = None
                    return
                
                self.split_pdf_path = file_path
                self.split_pdf_pages = page_count
                
                # Clear thumbnail cache
                self.page_thumbnails = {}
                
                # Update UI
                filename = os.path.basename(file_path)
                self.file_info_label.configure(
                    text=f"{filename} ({page_count} pages)",
                    text_color="white"
                )
                
                # Enable controls
                self.clear_pdf_btn.configure(state="normal")
                self.split_slider.configure(state="normal", from_=1, to=page_count-1, number_of_steps=page_count-2)
                self.split_slider.set(1)
                self.split_btn.configure(state="normal")
                self.split_entry.configure(state="normal")
                self.split_entry.delete(0, "end")
                self.split_entry.insert(0, "1")
                # Update preview
                self.update_split_preview(1)
                
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error reading PDF file:\n{str(e)}")
                if self.pdf_document:
                    self.pdf_document.close()
                    self.pdf_document = None
    
    def clear_split_file(self):
        """Clear the selected PDF file"""
        # Close PDF document
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
        
        self.split_pdf_path = None
        self.split_pdf_pages = 0
        self.page_thumbnails = {}  # Clear thumbnail cache
        
        # Update UI
        self.file_info_label.configure(text="No file selected", text_color="gray")
        self.clear_pdf_btn.configure(state="disabled")
        self.split_slider.configure(state="disabled")
        self.split_btn.configure(state="disabled")
        self.preview_label.configure(text="Select a PDF file to preview split", text_color="gray")
        self.page_thumbnail_label.configure(image=None, text="No page to preview", text_color="gray")
        self.page_info_label.configure(text="")
        self.split_value_label.configure(text="1")
        self.split_entry.configure(state="disabled")
        self.split_entry.delete(0, "end")
        self.split_entry.insert(0, "1")
    
    def update_split_preview(self, value):
        """Update the split preview based on slider value"""
        if self.split_pdf_path and self.split_pdf_pages > 0 and self.pdf_document:
            split_page = int(float(value))
            self.split_value_label.configure(text=str(split_page))
            # Sync entry if needed
            if self.split_entry.get() != str(split_page):
                self.split_entry.delete(0, "end")
                self.split_entry.insert(0, str(split_page))
            
            # Update text preview
            preview_text = (
                f"📄 Part 1: Pages 1-{split_page}\n"
                f"    ({split_page} pages)\n\n"
                f"📄 Part 2: Pages {split_page + 1}-{self.split_pdf_pages}\n"
                f"    ({self.split_pdf_pages - split_page} pages)"
            )
            self.preview_label.configure(text=preview_text, text_color="lightblue")
            
            # Update visual preview - show the page after which we'll split
            try:
                page_thumbnail = self.generate_page_thumbnail(split_page - 1)  # 0-based index
                
                # Update thumbnail
                self.page_thumbnail_label.configure(
                    image=page_thumbnail,
                    text="",
                    compound="top"
                )
                
                # Update page info
                self.page_info_label.configure(
                    text=f"Page {split_page}\n(Split after this page)",
                    text_color="lightblue"
                )
                
            except Exception as e:
                print(f"Error updating page preview: {e}")
                self.page_thumbnail_label.configure(
                    image=None,
                    text=f"Page {split_page}\n(Preview error)",
                    text_color="orange"
                )
                self.page_info_label.configure(
                    text="Preview error",
                    text_color="orange"
                )
    
    def on_split_entry(self, event):
        if not self.split_pdf_path or self.split_pdf_pages < 2:
            return
        try:
            value = int(self.split_entry.get())
            if value < 1:
                value = 1
            if value > self.split_pdf_pages - 1:
                value = self.split_pdf_pages - 1
            self.split_slider.set(value)
            self.update_split_preview(value)
        except Exception:
            # Reset to slider value if invalid
            self.split_entry.delete(0, "end")
            self.split_entry.insert(0, str(int(self.split_slider.get())))
    
    def split_pdf(self):
        """Split the selected PDF file"""
        if not self.split_pdf_path:
            tk.messagebox.showwarning("Warning", "Please select a PDF file first.")
            return
        
        split_page = int(self.split_slider.get())
        
        # Ask user where to save the split files
        base_name = os.path.splitext(os.path.basename(self.split_pdf_path))[0]
        
        # Get directory to save files
        save_dir = tk.filedialog.askdirectory(
            title="Select folder to save split PDF files"
        )
        
        if not save_dir:
            return
        
        try:
            # Open the original PDF
            source_doc = fitz.open(self.split_pdf_path)
            
            # Create first part (pages 1 to split_page)
            part1_doc = fitz.open()
            part1_doc.insert_pdf(source_doc, from_page=0, to_page=split_page-1)
            
            # Create second part (pages split_page+1 to end)
            part2_doc = fitz.open()
            part2_doc.insert_pdf(source_doc, from_page=split_page, to_page=source_doc.page_count-1)
            
            # Save both parts
            part1_path = os.path.join(save_dir, f"{base_name}_part1.pdf")
            part2_path = os.path.join(save_dir, f"{base_name}_part2.pdf")
            
            part1_doc.save(part1_path)
            part1_doc.close()
            
            part2_doc.save(part2_path)
            part2_doc.close()
            
            source_doc.close()
            
            # Show success message
            tk.messagebox.showinfo(
                "Success",
                f"PDF successfully split!\n\n"
                f"Part 1: {os.path.basename(part1_path)} ({split_page} pages)\n"
                f"Part 2: {os.path.basename(part2_path)} ({self.split_pdf_pages - split_page} pages)\n\n"
                f"Files saved to: {save_dir}"
            )
            
            # Ask if user wants to clear the current file
            response = tk.messagebox.askyesno("Clear File", "Would you like to clear the current file and start over?")
            if response:
                self.clear_split_file()
                
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error splitting PDF:\n{str(e)}") 