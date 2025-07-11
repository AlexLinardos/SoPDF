"""
Organize Tab for SoPDF

This module contains the PDF page organization functionality.
"""

import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from PyPDF2 import PdfReader, PdfWriter


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
            text="No file selected - Page list will appear here",
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
        
        # Instructions label
        instructions_label = ctk.CTkLabel(
            controls_frame,
            text="🧾 Instructions: Select pages • Use buttons or drag-and-drop to reorder • Remove/restore pages as needed",
            font=ctk.CTkFont(size=14),
            text_color="lightblue"
        )
        instructions_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
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
    
    def select_pdf_for_organize(self):
        """Select a PDF file for text-based organizing"""
        file_types = [("PDF files", "*.pdf"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(
            title="Select PDF file to organize",
            filetypes=file_types
        )
        
        if file_path:
            try:
                # Show loading message
                self.organize_file_info.configure(text="Loading PDF...", text_color="orange")
                self.app.root.update()
                
                # Read PDF to get pages
                reader = PdfReader(file_path)
                page_count = len(reader.pages)
                
                if page_count < 1:
                    messagebox.showwarning("Warning", "PDF file appears to be empty.")
                    return
                
                # Set up organize variables
                self.organize_pdf_path = file_path
                self.organize_pages = reader.pages
                self.organize_page_order = list(range(page_count))  # [0, 1, 2, ...]
                self.removed_pages = set()
                
                # Clear existing content
                for widget in self.pages_frame.winfo_children():
                    widget.destroy()
                
                # Create text-based interface
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
                
                # Update status
                self.update_organize_status()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error reading PDF file:\n{str(e)}")
    
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
    
    def clear_organize_file(self):
        """Clear the selected PDF file"""
        self.organize_pdf_path = None
        self.organize_pages = []
        self.organize_page_order = []
        self.removed_pages = set()
        self.listbox_drag_data = {"dragging": False, "start_index": None}
        
        # Clear all interface elements
        for widget in self.pages_frame.winfo_children():
            widget.destroy()
        
        # Reset text interface references
        if hasattr(self, 'text_organize_listbox'):
            delattr(self, 'text_organize_listbox')
        
        # Update UI
        self.organize_file_info.configure(text="No file selected - Page list will appear here", text_color="gray")
        self.clear_organize_btn.configure(state="disabled")
        self.reset_order_btn.configure(state="disabled")
        self.save_organized_btn.configure(state="disabled")
        self.organize_status.configure(text="No file loaded", text_color="gray")
    
    def reset_page_order(self):
        """Reset page order to original"""
        if not self.organize_pdf_path:
            return
        
        result = messagebox.askyesno(
            "Reset Order", 
            "Reset all changes and restore original page order?\n\nThis will undo all reordering and restore all removed pages."
        )
        
        if result:
            # Reset to original order
            self.organize_page_order = list(range(len(self.organize_pages)))
            self.removed_pages = set()
            
            # Update text display
            if hasattr(self, 'text_organize_listbox'):
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
            messagebox.showwarning("Warning", "Please select a PDF file first.")
            return
        
        # Get active pages in current order
        active_pages = [idx for idx in self.organize_page_order if idx not in self.removed_pages]
        
        if not active_pages:
            messagebox.showwarning("Warning", "Cannot save PDF with no pages. Please restore at least one page.")
            return
        
        # Ask user where to save
        base_name = os.path.splitext(os.path.basename(self.organize_pdf_path))[0]
        output_file = filedialog.asksaveasfilename(
            title="Save organized PDF as...",
            defaultextension=".pdf",
            initialfile=f"{base_name}_organized.pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
        
        try:
            # Create new PDF with organized pages
            writer = PdfWriter()
            
            for page_idx in active_pages:
                writer.add_page(self.organize_pages[page_idx])
            
            # Save the organized PDF
            with open(output_file, 'wb') as output_pdf:
                writer.write(output_pdf)
            
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
            
            messagebox.showinfo("Success", success_msg)
            
            # Ask if user wants to clear the current file
            response = messagebox.askyesno("Clear File", "Would you like to clear the current file and start over?")
            if response:
                self.clear_organize_file()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving organized PDF:\n{str(e)}")
    
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
            result = messagebox.askyesno(
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
                choice = simpledialog.askinteger(
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