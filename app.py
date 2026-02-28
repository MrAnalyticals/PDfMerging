from flask import Flask, render_template, request, send_file
from pypdf import PdfWriter
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Create temp folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('merged_pdfs', exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    # Check if files were uploaded
    if 'pdf_files' not in request.files:
        return "No files uploaded", 400
    
    files = request.files.getlist('pdf_files')
    
    if len(files) < 2:
        return "Please select at least 2 PDF files to merge", 400
    
    # Validate all files
    for file in files:
        if file.filename == '':
            return "One or more files have no name", 400
        if not allowed_file(file.filename):
            return f"Invalid file type: {file.filename}. Only PDF files are allowed.", 400
    
    try:
        # Create PDF writer object
        pdf_writer = PdfWriter()
        temp_files = []
        
        # Process each uploaded PDF
        for file in files:
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            temp_files.append(temp_path)
            
            # Add pages from this PDF to the writer
            pdf_writer.append(temp_path)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'merged_pdf_{timestamp}.pdf'
        output_path = os.path.join('merged_pdfs', output_filename)
        
        # Write the merged PDF
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass
        
        # Send the merged PDF to user
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    
    except Exception as e:
        return f"Error merging PDFs: {str(e)}", 500

# Clean up old files on startup (optional)
def cleanup_old_files():
    """Remove files older than 1 hour"""
    import time
    current_time = time.time()
    
    for folder in ['temp_uploads', 'merged_pdfs']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    if current_time - os.path.getmtime(file_path) > 3600:  # 1 hour
                        try:
                            os.remove(file_path)
                        except:
                            pass

if __name__ == '__main__':
    cleanup_old_files()
    app.run(debug=True, port=5000)
