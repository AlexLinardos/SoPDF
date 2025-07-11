"""
Merge Tab for SoPDF

This module contains the PDF merging functionality.
"""

import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter


class MergeTab:
    """Manages the PDF merging functionality"""
    
    def __init__(self, tab_frame, app_reference):
        self.tab_frame = tab_frame
        self.app = app_reference
        
        # Initialize merge-related variables
        self.pdf_files = []
        
        self.setup_merge_tab()
    
    def setup_merge_tab(self):
        """Setup the Merge tab with PDF merging functionality"""
        # Configure grid weights
        self.tab_frame.grid_columnconfigure(0, weight=1)
        self.tab_frame.grid_rowconfigure(1, weight=1)
        
        # Title and instructions
        title_label = ctk.CTkLabel(
            self.tab_frame,
            text="🔗 Merge PDF Documents",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Main content frame
        content_frame = ctk.CTkFrame(self.tab_frame, corner_radius=8)
        content_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=0)  # Buttons column - fixed width
        content_frame.grid_columnconfigure(1, weight=1)  # List column - expandable
        content_frame.grid_columnconfigure(2, weight=0)  # Merge column - fixed width
        content_frame.grid_rowconfigure(1, weight=1)
        
        # File selection section
        file_section_label = ctk.CTkLabel(
            content_frame,
            text="Select PDF Files to Merge:",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        file_section_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="ns")
        
        # Add files button
        self.add_files_btn = ctk.CTkButton(
            buttons_frame,
            text="➕Add PDF Files",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14),
            command=self.add_pdf_files
        )
        self.add_files_btn.grid(row=0, column=0, pady=(0, 10))
        
        # Remove selected button
        self.remove_file_btn = ctk.CTkButton(
            buttons_frame,
            text="➖Remove Selected",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.remove_selected_file
        )
        self.remove_file_btn.grid(row=1, column=0, pady=10)
        
        # Clear all button
        self.clear_all_btn = ctk.CTkButton(
            buttons_frame,
            text="🧹Clear All",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.clear_all_files
        )
        self.clear_all_btn.grid(row=2, column=0, pady=10)
        
        # Move up button
        self.move_up_btn = ctk.CTkButton(
            buttons_frame,
            text="⬆ Move Up",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.move_file_up
        )
        self.move_up_btn.grid(row=3, column=0, pady=10)
        
        # Move down button
        self.move_down_btn = ctk.CTkButton(
            buttons_frame,
            text="⬇ Move Down",
            width=160,
            height=45,
            font=ctk.CTkFont(size=14),
            state="disabled",
            command=self.move_file_down
        )
        self.move_down_btn.grid(row=4, column=0, pady=(10, 0))
        
        # File list frame
        list_frame = ctk.CTkFrame(content_frame)
        list_frame.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)  # Listbox column - expandable
        list_frame.grid_columnconfigure(1, weight=0)  # Scrollbar column - fixed width
        list_frame.grid_rowconfigure(0, weight=1)
        
        # File listbox
        self.file_listbox = tk.Listbox(
            list_frame,
            bg="#212121",
            fg="white",
            selectbackground="#1f538d",
            selectforeground="white",
            font=("Segoe UI", 12),
            borderwidth=0,
            highlightthickness=0
        )
        self.file_listbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Scrollbar for listbox
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="ns")
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Merge section
        merge_frame = ctk.CTkFrame(content_frame)
        merge_frame.grid(row=1, column=2, padx=(5, 10), pady=10, sticky="ns")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            merge_frame,
            text="No files selected",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Merge button
        self.merge_btn = ctk.CTkButton(
            merge_frame,
            text="🔗 Merge PDFs",
            width=160,
            height=55,
            state="disabled",
            command=self.merge_pdfs,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.merge_btn.grid(row=1, column=0, padx=20, pady=20)
    
    def add_pdf_files(self):
        """Add PDF files to the merge list"""
        file_types = [("PDF files", "*.pdf"), ("All files", "*.*")]
        files = filedialog.askopenfilenames(
            title="Select PDF files to merge",
            filetypes=file_types
        )
        
        for file_path in files:
            if file_path not in self.pdf_files:
                self.pdf_files.append(file_path)
                filename = os.path.basename(file_path)
                self.file_listbox.insert(tk.END, filename)
        
        self.update_merge_ui_state()
    
    def remove_selected_file(self):
        """Remove selected file from the merge list"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_listbox.delete(index)
            self.pdf_files.pop(index)
            self.update_merge_ui_state()
    
    def clear_all_files(self):
        """Clear all files from the merge list"""
        self.file_listbox.delete(0, tk.END)
        self.pdf_files.clear()
        self.update_merge_ui_state()
    
    def move_file_up(self):
        """Move selected file up in the list"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in both lists
            self.pdf_files[index], self.pdf_files[index-1] = self.pdf_files[index-1], self.pdf_files[index]
            
            # Update listbox
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index-1, item)
            self.file_listbox.select_set(index-1)
    
    def move_file_down(self):
        """Move selected file down in the list"""
        selection = self.file_listbox.curselection()
        if selection and selection[0] < len(self.pdf_files) - 1:
            index = selection[0]
            # Swap in both lists
            self.pdf_files[index], self.pdf_files[index+1] = self.pdf_files[index+1], self.pdf_files[index]
            
            # Update listbox
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index+1, item)
            self.file_listbox.select_set(index+1)
    
    def on_file_select(self, event):
        """Handle file selection in listbox"""
        selection = self.file_listbox.curselection()
        if selection:
            # Enable/disable move buttons based on selection position
            index = selection[0]
            self.move_up_btn.configure(state="normal" if index > 0 else "disabled")
            self.move_down_btn.configure(state="normal" if index < len(self.pdf_files) - 1 else "disabled")
            self.remove_file_btn.configure(state="normal")
        else:
            self.move_up_btn.configure(state="disabled")
            self.move_down_btn.configure(state="disabled")
            self.remove_file_btn.configure(state="disabled")
    
    def update_merge_ui_state(self):
        """Update UI state based on selected files"""
        file_count = len(self.pdf_files)
        
        if file_count == 0:
            self.status_label.configure(text="No files selected", text_color="gray")
            self.merge_btn.configure(state="disabled")
            self.clear_all_btn.configure(state="disabled")
            self.remove_file_btn.configure(state="disabled")
            self.move_up_btn.configure(state="disabled")
            self.move_down_btn.configure(state="disabled")
        elif file_count == 1:
            self.status_label.configure(text="1 file selected\n(Need 2+ to merge)", text_color="orange")
            self.merge_btn.configure(state="disabled")
            self.clear_all_btn.configure(state="normal")
        else:
            self.status_label.configure(text=f"{file_count} files selected\nReady to merge!", text_color="lightgreen")
            self.merge_btn.configure(state="normal")
            self.clear_all_btn.configure(state="normal")
    
    def merge_pdfs(self):
        """Merge selected PDF files"""
        if len(self.pdf_files) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 PDF files to merge.")
            return
        
        # Ask user where to save the merged file
        output_file = filedialog.asksaveasfilename(
            title="Save merged PDF as...",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
        
        try:
            # Create a PDF writer object
            writer = PdfWriter()
            
            # Add pages from each PDF
            for pdf_path in self.pdf_files:
                try:
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        writer.add_page(page)
                except Exception as e:
                    messagebox.showerror("Error", f"Error reading {os.path.basename(pdf_path)}:\n{str(e)}")
                    return
            
            # Write the merged PDF
            with open(output_file, 'wb') as output_pdf:
                writer.write(output_pdf)
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"Successfully merged {len(self.pdf_files)} PDF files!\n\nSaved as: {os.path.basename(output_file)}"
            )
            
            # Optionally clear the list after successful merge
            response = messagebox.askyesno("Clear List", "Would you like to clear the file list?")
            if response:
                self.clear_all_files()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error merging PDFs:\n{str(e)}") 