# SoPDF - Simple PDF Organizer

<div align="center">
  <img src="assets/SoPDF_logo_trans.png" alt="SoPDF Logo" width="120" height="120">
  
  **A powerful yet simple PDF management application with an elegant modern interface**
  
  [![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
  [![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2.0+-green.svg)](https://github.com/TomSchimansky/CustomTkinter)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

## 🚀 Features

SoPDF provides three powerful PDF management tools in one clean, intuitive interface:

### 📁 **Organize Pages**
- **Visual & Text-based Interface**: Reorder PDF pages with intuitive drag-and-drop or text-based controls
- **Remove & Restore**: Temporarily remove pages and restore them as needed
- **Smart Status**: Real-time feedback on changes made to your document
- **Flexible Controls**: Move pages up/down, drag-and-drop reordering, or use keyboard shortcuts

### 🔗 **Merge PDFs**
- **Multi-file Selection**: Add multiple PDF files with a simple file browser
- **Reorder Files**: Drag and drop or use buttons to change merge order
- **Live Preview**: See exactly which files will be merged and in what order
- **Batch Processing**: Merge any number of PDF files into a single document

### ✂️ **Split PDFs**
- **Interactive Splitting**: Visual slider to choose split point
- **Live Preview**: See exactly how your PDF will be split before saving
- **Smart Naming**: Automatically generates logical names for split files
- **Flexible Output**: Choose where to save your split PDF files

## 📸 Interface Preview

SoPDF features a modern dark theme with clean, intuitive controls:
- **Tabbed Interface**: Three main tabs for different operations
- **Responsive Design**: Adapts to different window sizes
- **Modern UI**: Built with CustomTkinter for a sleek, native feel
- **Accessibility**: Clear fonts, good contrast, and logical navigation

## 📋 Requirements

### System Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Memory**: 512MB RAM minimum (1GB+ recommended for large PDFs)

### Python Dependencies
```
customtkinter>=5.2.0    # Modern GUI framework
PyPDF2>=3.0.0          # PDF manipulation library
Pillow>=9.0.0          # Image processing
pdf2image>=1.16.0      # PDF to image conversion (for previews)
```

## 🛠 Installation

### Quick Start
1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/AlexLinardos/SoPDF.git
   cd SoPDF
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
   # or
   python main.py
   ```

## 🎯 Usage

### Running the Application

You have two options to start SoPDF:

```bash
# Option 1: Dedicated entry point (recommended)
python run.py

# Option 2: Backwards compatibility entry point
python main.py
```

Both commands launch the same application. `run.py` is the streamlined entry point, while `main.py` provides backwards compatibility and shows a startup message.

### Basic Workflow

#### Organizing PDF Pages
1. **Select PDF**: Click "📁 Select PDF File" in the Organize tab
2. **Reorder Pages**: 
   - Drag and drop pages in the list
   - Use ⬆️⬇️ buttons to move selected pages
   - Double-click pages for preview
3. **Remove/Restore**: Right-click pages or use the ❌/↶ buttons
4. **Save**: Click "💾 Save Organized PDF" when satisfied

#### Merging PDFs
1. **Add Files**: Click "➕Add PDF Files" to select multiple PDFs
2. **Reorder**: Use ⬆️⬇️ buttons or drag-and-drop to arrange files
3. **Merge**: Click "🔗 Merge PDFs" and choose output location

#### Splitting PDFs
1. **Select PDF**: Click "📁 Select PDF File" in the Split tab
2. **Choose Split Point**: Use the slider to select where to split
3. **Preview**: Review the split preview
4. **Split**: Click "✂️ Split PDF" and choose output folder

### Keyboard Shortcuts
- **Ctrl+O**: Open file dialog (context-dependent)
- **Ctrl+S**: Save current work
- **F5**: Refresh/Reset current tab
- **Escape**: Close dialogs/deselect

## 🏗 Project Structure

SoPDF uses a modern modular architecture for maintainability and extensibility:

```
SoPDF/
├── 📁 src/                 # Source code (modular architecture)
│   ├── app.py             # Main application class
│   ├── ui/                # User interface modules
│   │   ├── organize_tab.py # Page organization functionality
│   │   ├── merge_tab.py   # PDF merging functionality
│   │   ├── split_tab.py   # PDF splitting functionality
│   │   └── components.py  # Reusable UI components
│   └── utils/             # Utility modules
│       └── file_utils.py  # File operation utilities
├── 📁 assets/             # Application assets
│   ├── SoPDF_icon.ico     # Application icon
│   └── SoPDF_logo_trans.png # Logo with transparency
├── 📁 docs/               # Documentation
│   ├── README.md          # Technical documentation
│   └── INSTALL_UPX.md     # Upx installation guide
├── main.py                # Backwards-compatible entry point
├── run.py                 # Main entry point
├── requirements.txt       # Python dependencies
└── main_backup.py         # Backup of original monolithic version
```

### Architecture Benefits
- **Modular Design**: Each feature is isolated in its own module
- **Easy Maintenance**: Clear separation of concerns
- **Extensible**: Simple to add new features or modify existing ones
- **Testable**: Modular structure enables better testing

## 🔧 Development

### Setting Up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/SoPDF.git
   cd SoPDF
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Document complex functions
- Keep functions focused and small

### Adding New Features
1. Create feature modules in appropriate directories (`src/ui/` for UI, `src/utils/` for utilities)
2. Import and integrate in `src/app.py`
3. Update documentation
4. Test thoroughly across different platforms

### Testing
- Test with various PDF types and sizes
- Test on different operating systems
- Check memory usage with large files

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Ensure you're in the correct directory and have installed dependencies
pip install -r requirements.txt
```

**Application won't start**
- Check Python version: `python --version` (needs 3.7+)
- Verify all dependencies are installed
- Try running with: `python -m src.app`

**PDF files won't open**
- Ensure PDFs aren't password-protected
- Check file permissions
- Try with a different PDF file

### Performance Tips
- For large PDFs (100+ pages), visual previews may be slower
- Consider using text-based mode for very large documents
- Close unused tabs to free memory

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Contributing Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues or have questions:
1. Check the [troubleshooting section](#-troubleshooting) above
2. Look through existing [issues](https://github.com/yourusername/SoPDF/issues)
3. Create a new issue with detailed information about your problem

## 🙏 Acknowledgments

- **CustomTkinter**: For the modern, beautiful GUI framework
- **PyPDF2**: For reliable PDF processing capabilities
- **PIL/Pillow**: For image processing support

---

<div align="center">
  <strong>Made with ❤️ for PDF management simplicity</strong>
</div> 
