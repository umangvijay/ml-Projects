import os
import sys
import uuid
import threading
import importlib.util
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, jsonify, url_for, redirect, session

# Check if required packages are installed
required_web_packages = [
    "flask", 
    "werkzeug"
]

missing_packages = []
for package in required_web_packages:
    if importlib.util.find_spec(package) is None:
        missing_packages.append(package)

if missing_packages:
    print(f"Missing required packages: {', '.join(missing_packages)}")
    print("Please install them using:")
    print(f"pip install {' '.join(missing_packages)}")
    sys.exit(1)

# Default locations - Changed to use D drive for storage
UPLOAD_FOLDER = 'D:\\OCR_PDF_Uploads'  # Store uploads on D drive
OUTPUT_FOLDER = 'D:\\OCR_PDF_Output'   # Store PDFs on D drive
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')
TEMPLATE_FOLDER = os.path.join(os.getcwd(), 'templates')

# Create required directories with better error handling
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, STATIC_FOLDER, TEMPLATE_FOLDER]:
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")
    except Exception as e:
        print(f"Error creating directory {folder}: {str(e)}")
        print("Make sure you have permission to create this directory")
        print("You may need to run the application as administrator")
        # Don't exit yet, we'll try to continue

# Import core OCR functionality
try:
    # Fix compatibility with newer Pillow versions
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        # In newer Pillow versions, ANTIALIAS was renamed to LANCZOS
        Image.ANTIALIAS = Image.LANCZOS
        print("Applied Pillow compatibility patch")
    
    import easyocr
    import PyPDF2
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph
except ImportError as e:
    print(f"Error importing required packages: {str(e)}")
    print("Please install the required packages first:")
    print("pip install easyocr PyPDF2 reportlab Pillow")
    sys.exit(1)

# Initialize OCR Reader in a background thread to avoid startup delay
ocr_reader = None
ocr_init_error = None  # Track any initialization errors

def init_ocr():
    global ocr_reader, ocr_init_error
    try:
        print("Initializing OCR engine...")
        ocr_reader = easyocr.Reader(['en'])
        print("OCR engine initialized successfully!")
    except Exception as e:
        error_msg = str(e)
        ocr_init_error = error_msg
        print(f"Error initializing OCR engine: {error_msg}")
        print("This may be due to missing dependencies or insufficient memory")

init_thread = threading.Thread(target=init_ocr)
init_thread.daemon = True
init_thread.start()

# Create the Flask application
app = Flask(__name__, 
            static_folder=STATIC_FOLDER, 
            template_folder=TEMPLATE_FOLDER)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Helper function to sanitize text for PDF creation
def sanitize_text(text):
    """Sanitize text to prevent ReportLab XML parsing errors"""
    sanitized = (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;'))
    return sanitized

# Extract text from an image
def extract_text_from_image(image_path):
    """Extract text from image using EasyOCR"""
    global ocr_reader
    # Wait for OCR engine to initialize
    if ocr_reader is None:
        return "OCR engine is still initializing. Please try again in a moment."
    
    try:
        result = ocr_reader.readtext(image_path)
        # Extract just the text from the result
        extracted_text = ' '.join([item[1] for item in result])
        return extracted_text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return f"Error extracting text: {str(e)}"

# Create PDF from extracted text
def create_pdf(text, output_path):
    """Create a PDF with the extracted text"""
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Sanitize text
        sanitized_text = sanitize_text(text)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        
        # Split text into paragraphs and create paragraph objects
        paragraphs = []
        for p in sanitized_text.split('\n\n'):
            if p.strip():  # Skip empty paragraphs
                try:
                    paragraphs.append(Paragraph(p, style))
                except Exception as e:
                    # If a paragraph fails, add it as plain text
                    print(f"Warning: Could not format paragraph: {str(e)}")
                    paragraphs.append(Paragraph(f"<![CDATA[{p}]]>", style))
        
        # If no valid paragraphs, add a default one
        if not paragraphs:
            paragraphs = [Paragraph("No valid text could be extracted from the image.", style)]
            
        # Build PDF document
        doc.build(paragraphs)
        return True, "PDF created successfully!"
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        # Try a more direct approach as fallback
        try:
            print("Attempting fallback PDF creation method...")
            # Create a simple canvas-based PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            y = height - 50  # Start 50 points from the top
            
            # Split text into lines
            for line in text.split('\n'):
                if y < 50:  # When we get to the bottom of the page
                    c.showPage()  # Create a new page
                    y = height - 50  # Reset position to top
                c.drawString(50, y, line)
                y -= 15  # Move down 15 points
            
            c.save()
            return True, "Fallback PDF created successfully!"
        except Exception as e2:
            print(f"Fallback PDF creation also failed: {str(e2)}")
            return False, f"Failed to create PDF: {str(e)}"

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    """Render the main page"""
    # Check if OCR engine is ready
    global ocr_init_error
    ocr_status = "ready" if ocr_reader is not None else "initializing"
    
    # Check if template exists, if not create it
    if not os.path.exists(os.path.join(TEMPLATE_FOLDER, 'index.html')):
        try:
            create_templates()
            print("Templates created on-demand")
        except Exception as e:
            return f"""
            <html>
            <head><title>Error</title></head>
            <body>
                <h1>Template Error</h1>
                <p>Could not create required templates: {str(e)}</p>
                <p>Please check console for more details.</p>
            </body>
            </html>
            """
    
    # Show error page if OCR failed to initialize
    if ocr_init_error:
        return f"""
        <html>
        <head><title>OCR Initialization Error</title></head>
        <body>
            <h1>OCR Engine Error</h1>
            <p>The OCR engine failed to initialize: {ocr_init_error}</p>
            <p>Please check the console for more details and ensure all dependencies are installed.</p>
            <p>You may need to run: <code>pip install easyocr PyPDF2 reportlab Pillow</code></p>
        </body>
        </html>
        """
    
    try:
        return render_template('index.html', ocr_status=ocr_status)
    except Exception as e:
        return f"""
        <html>
        <head><title>Template Error</title></head>
        <body>
            <h1>Template Rendering Error</h1>
            <p>Error: {str(e)}</p>
            <p>Please check that template files exist in: {TEMPLATE_FOLDER}</p>
        </body>
        </html>
        """

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and OCR processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save uploaded file
        file.save(upload_path)
        
        # Extract text
        extracted_text = extract_text_from_image(upload_path)
        
        # Save information in session
        session['uploaded_file'] = upload_path
        session['extracted_text'] = extracted_text
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'filename': unique_filename
        })
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/create-pdf', methods=['POST'])
def create_pdf_route():
    """Create PDF from extracted text"""
    if 'extracted_text' not in session:
        return jsonify({'error': 'No text has been extracted yet'}), 400
    
    # Get the text
    text = session.get('extracted_text', '')
    
    # Create a unique filename for the PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"ocr_text_{timestamp}.pdf"
    pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
    
    # Create the PDF
    success, message = create_pdf(text, pdf_path)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'pdf_url': url_for('download_file', filename=pdf_filename)
        })
    else:
        return jsonify({'error': message}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download a created PDF"""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/status')
def ocr_status():
    """Check if OCR engine is initialized"""
    status = "ready" if ocr_reader is not None else "initializing"
    return jsonify({'status': status})

# Create the HTML template
@app.route('/create-templates', methods=['GET'])
def create_templates():
    """Create the necessary template files"""
    # Create the main HTML template
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR to PDF Converter</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>OCR to PDF Converter</h1>
            <p>Extract text from images and convert to PDF</p>
        </header>
        
        <main>
            <div class="card upload-card">
                <h2>Upload Image</h2>
                <div class="upload-area" id="drop-area">
                    <p>Drag and drop image here or</p>
                    <label class="file-label">
                        <span>Choose File</span>
                        <input type="file" id="file-input" accept=".png,.jpg,.jpeg,.gif,.bmp,.tiff,.tif" />
                    </label>
                    <p class="file-info" id="file-info">No file selected</p>
                </div>
                <div class="progress-container" id="progress-container">
                    <div class="progress-bar" id="progress-bar"></div>
                </div>
                <button id="upload-button" class="btn primary-btn" disabled>Upload & Extract Text</button>
            </div>
            
            <div class="card result-card" id="result-card" style="display: none;">
                <h2>Extracted Text</h2>
                <div class="text-area-container">
                    <textarea id="extracted-text" readonly></textarea>
                </div>
                <button id="create-pdf-button" class="btn primary-btn">Create PDF</button>
            </div>
            
            <div class="card pdf-card" id="pdf-card" style="display: none;">
                <h2>PDF Created</h2>
                <p id="pdf-message"></p>
                <a id="download-link" class="btn primary-btn" href="#">Download PDF</a>
            </div>
        </main>
        
        <div class="status-bar">
            <p>OCR Engine Status: <span id="ocr-status" class="{{ 'status-ready' if ocr_status == 'ready' else 'status-initializing' }}">{{ ocr_status }}</span></p>
        </div>
        
        <footer>
            <p>&copy; 2023 OCR to PDF Converter</p>
        </footer>
    </div>
    
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
"""
    
    # Create the CSS file
    css_content = """/* Main styles for OCR to PDF web app */
:root {
    --primary-color: #4a6fa5;
    --secondary-color: #166088;
    --accent-color: #4d9de0;
    --background-color: #f5f7fa;
    --card-background: #ffffff;
    --text-color: #333333;
    --border-color: #dddddd;
    --success-color: #28a745;
    --error-color: #dc3545;
    --warning-color: #ffc107;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
    padding: 20px;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background-color: var(--primary-color);
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

header h1 {
    margin-bottom: 10px;
    font-size: 2.5rem;
}

main {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.card {
    background-color: var(--card-background);
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}

.card h2 {
    color: var(--primary-color);
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
}

.upload-area {
    border: 2px dashed var(--border-color);
    border-radius: 8px;
    padding: 40px 20px;
    text-align: center;
    margin-bottom: 20px;
    transition: all 0.3s ease;
    background-color: var(--background-color);
}

.upload-area.highlight {
    border-color: var(--accent-color);
    background-color: rgba(77, 157, 224, 0.1);
}

.file-label {
    display: inline-block;
    padding: 10px 20px;
    background-color: var(--primary-color);
    color: white;
    border-radius: 4px;
    cursor: pointer;
    margin: 10px 0;
    transition: background-color 0.3s ease;
}

.file-label:hover {
    background-color: var(--secondary-color);
}

.file-label input {
    display: none;
}

.file-info {
    margin-top: 10px;
    font-size: 0.9rem;
    color: #666;
}

.progress-container {
    height: 10px;
    background-color: var(--background-color);
    border-radius: 5px;
    margin-bottom: 20px;
    overflow: hidden;
    display: none;
}

.progress-bar {
    height: 100%;
    width: 0;
    background-color: var(--accent-color);
    transition: width 0.3s ease;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s ease;
    text-align: center;
    text-decoration: none;
}

.primary-btn {
    background-color: var(--primary-color);
    color: white;
}

.primary-btn:hover {
    background-color: var(--secondary-color);
}

.primary-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

.text-area-container {
    margin: 20px 0;
}

textarea {
    width: 100%;
    min-height: 200px;
    padding: 10px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    resize: vertical;
    font-family: inherit;
    font-size: 0.9rem;
    line-height: 1.5;
}

.status-bar {
    margin-top: 20px;
    padding: 10px;
    background-color: var(--card-background);
    border-radius: 4px;
    text-align: center;
    font-size: 0.9rem;
}

.status-ready {
    color: var(--success-color);
    font-weight: bold;
}

.status-initializing {
    color: var(--warning-color);
    font-weight: bold;
}

footer {
    text-align: center;
    margin-top: 30px;
    padding: 20px;
    border-top: 1px solid var(--border-color);
    color: #666;
}

@media (min-width: 768px) {
    main {
        flex-direction: row;
        flex-wrap: wrap;
    }
    
    .card {
        flex: 1 1 300px;
    }
}
"""
    
    # Create the JavaScript file
    js_content = """// JavaScript for OCR to PDF web app
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const uploadButton = document.getElementById('upload-button');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const resultCard = document.getElementById('result-card');
    const extractedText = document.getElementById('extracted-text');
    const createPdfButton = document.getElementById('create-pdf-button');
    const pdfCard = document.getElementById('pdf-card');
    const pdfMessage = document.getElementById('pdf-message');
    const downloadLink = document.getElementById('download-link');
    const ocrStatus = document.getElementById('ocr-status');
    
    // Check OCR status periodically
    function checkOCRStatus() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                ocrStatus.textContent = data.status;
                ocrStatus.className = data.status === 'ready' ? 'status-ready' : 'status-initializing';
                
                if (data.status === 'initializing') {
                    setTimeout(checkOCRStatus, 2000); // Check again in 2 seconds
                }
            })
            .catch(error => console.error('Error checking OCR status:', error));
    }
    
    // Check immediately on page load
    if (ocrStatus.textContent === 'initializing') {
        checkOCRStatus();
    }
    
    // Drag and drop handling
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    // Handle selected files
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });
    
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            // Check if file is an image
            if (!file.type.match('image.*')) {
                alert('Please select an image file');
                return;
            }
            
            fileInfo.textContent = `${file.name} (${formatSize(file.size)})`;
            uploadButton.disabled = false;
        }
    }
    
    // Format file size
    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    // Handle upload button click
    uploadButton.addEventListener('click', uploadFile);
    
    function uploadFile() {
        const file = fileInput.files[0];
        if (!file) return;
        
        // Prepare FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // Show progress
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';
        uploadButton.disabled = true;
        
        // Create request
        const xhr = new XMLHttpRequest();
        
        // Handle upload progress
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + '%';
            }
        });
        
        // Handle response
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    // Show extracted text
                    extractedText.value = response.text;
                    resultCard.style.display = 'block';
                    
                    // Scroll to result card
                    resultCard.scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert('Error: ' + response.error);
                }
            } else {
                try {
                    const response = JSON.parse(xhr.responseText);
                    alert('Error: ' + response.error);
                } catch (e) {
                    alert('Error: ' + xhr.statusText);
                }
            }
            
            // Reset upload form
            progressContainer.style.display = 'none';
            uploadButton.disabled = false;
        });
        
        // Handle errors
        xhr.addEventListener('error', function() {
            alert('Upload failed. Please try again.');
            progressContainer.style.display = 'none';
            uploadButton.disabled = false;
        });
        
        // Send the request
        xhr.open('POST', '/upload');
        xhr.send(formData);
    }
    
    // Handle create PDF button click
    createPdfButton.addEventListener('click', createPDF);
    
    function createPDF() {
        createPdfButton.disabled = true;
        createPdfButton.textContent = 'Creating PDF...';
        
        fetch('/create-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                pdfMessage.textContent = data.message;
                downloadLink.href = data.pdf_url;
                pdfCard.style.display = 'block';
                
                // Scroll to PDF card
                pdfCard.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error: ' + data.error);
            }
            
            createPdfButton.disabled = false;
            createPdfButton.textContent = 'Create PDF';
        })
        .catch(error => {
            console.error('Error creating PDF:', error);
            alert('Error creating PDF. Please try again.');
            createPdfButton.disabled = false;
            createPdfButton.textContent = 'Create PDF';
        });
    }
});
"""
    
    # Create the directories if they don't exist
    os.makedirs(os.path.join(TEMPLATE_FOLDER), exist_ok=True)
    os.makedirs(os.path.join(STATIC_FOLDER, 'css'), exist_ok=True)
    os.makedirs(os.path.join(STATIC_FOLDER, 'js'), exist_ok=True)
    
    # Write the files
    with open(os.path.join(TEMPLATE_FOLDER, 'index.html'), 'w') as f:
        f.write(index_html)
    
    with open(os.path.join(STATIC_FOLDER, 'css', 'style.css'), 'w') as f:
        f.write(css_content)
    
    with open(os.path.join(STATIC_FOLDER, 'js', 'script.js'), 'w') as f:
        f.write(js_content)
    
    return jsonify({
        'success': True,
        'message': 'Template files created successfully!',
        'files': {
            'html': os.path.join(TEMPLATE_FOLDER, 'index.html'),
            'css': os.path.join(STATIC_FOLDER, 'css', 'style.css'),
            'js': os.path.join(STATIC_FOLDER, 'js', 'script.js')
        }
    })

# Main function to run the web app
def main():
    # Create templates if they don't exist
    if not os.path.exists(os.path.join(TEMPLATE_FOLDER, 'index.html')):
        try:
            # Create template files
            with app.app_context():
                create_templates()
            print("Template files created successfully.")
        except Exception as e:
            print(f"Error creating template files: {str(e)}")
            print("Will attempt to create templates on first request")
    
    # Check for any directory errors    
    dir_errors = []
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, STATIC_FOLDER, TEMPLATE_FOLDER]:
        if not os.path.exists(folder):
            dir_errors.append(f"- {folder}")
    
    if dir_errors:
        print("\nWARNING: The following directories could not be created:")
        for err in dir_errors:
            print(err)
        print("\nThe application may not function correctly!")
        print("Try running as administrator or check drive permissions")
        
    print(f"\nOCR to PDF Web Application")
    print(f"---------------------------")
    print(f"1. Local Mode: http://127.0.0.1:5000")
    print(f"2. Network Mode: http://<your-ip-address>:5000")
    print(f"\nUploads directory: {UPLOAD_FOLDER}")
    print(f"Output directory: {OUTPUT_FOLDER}")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    # Run the web server
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Error starting web server: {str(e)}")
        print("This may be due to the port being in use or insufficient permissions")
        print("Try a different port or running as administrator")
        sys.exit(1)

if __name__ == "__main__":
    main() 