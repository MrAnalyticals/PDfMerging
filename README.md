# PDF Merger Web App

A simple and elegant web application to merge multiple PDF files into one.

## Features

- 📁 Drag and drop PDF files or click to browse
- 🔄 Merge multiple PDFs in order
- 💾 Automatic download of merged PDF
- 🎨 Beautiful, modern UI
- ⚡ Fast and lightweight

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Select or drag multiple PDF files (at least 2)

4. Click "Merge PDFs" button

5. The merged PDF will automatically download

## Requirements

- Python 3.7+
- Flask
- pypdf

## Notes

- Maximum file size: 50MB total
- Temporary files are automatically cleaned up after 1 hour
- PDFs are merged in the order they appear in the file list
